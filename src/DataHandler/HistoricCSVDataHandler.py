from __future__ import print_function

import datetime
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import os
import os.path
import re
import time

import numpy as np
import pandas as pd

import src.settings as settings
from src.Events.event import TickEvent


class PriceHandler(object):
    def _set_up_prices_dict(self):
        prices_dict = dict(
            (k, v) for k,v in [
                (p, {"bid": None, "ask": None, "time": None}) for p in self.pairs
            ]
        )
        inv_prices_dict = dict(
            (k, v) for k,v in [
                (
                    "%s%s" % (p[3:], p[:3]), 
                    {"bid": None, "ask": None, "time": None}
                ) for p in self.pairs
            ]
        )
        prices_dict.update(inv_prices_dict)
        return prices_dict

    def invert_prices(self, pair, bid, ask):
        getcontext().rounding = ROUND_HALF_DOWN
        inv_pair = "%s%s" % (pair[3:], pair[:3])
        inv_bid = (Decimal("1.0")/bid).quantize(
            Decimal("0.00001")
        )
        inv_ask = (Decimal("1.0")/ask).quantize(
            Decimal("0.00001")
        )
        return inv_pair, inv_bid, inv_ask


class HistoricCSVPriceHandler(PriceHandler):
    def __init__(self, pairs, events_queue, csv_dir):
        self.pairs = pairs
        self.events_queue = events_queue
        self.csv_dir = csv_dir
        self.prices = self._set_up_prices_dict()
        self.pair_frames = {}
        self.file_dates = self._list_all_file_dates()
        self.continue_backtest = True
        self.cur_date_idx = 0
        self.cur_date_pairs = self._open_convert_csv_files_for_day(
            self.file_dates[self.cur_date_idx]
        )

    def _list_all_csv_files(self):
        files = os.listdir(settings.CSV_DATA_DIR)
        pattern = re.compile("[A-Z]{6}_\d{8}.csv")
        matching_files = [f for f in files if pattern.search(f)]
        matching_files.sort()
        return matching_files

    def _list_all_file_dates(self):
        csv_files = self._list_all_csv_files()
        de_dup_csv = list(set([d[7:-4] for d in csv_files]))
        de_dup_csv.sort()
        return de_dup_csv

    def _open_convert_csv_files_for_day(self, date_str):
        p = self.pairs[0]
        pair_path = self.csv_dir  # os.path.join(self.csv_dir, '%s_%s.csv' % (p, date_str))
        self.pair_frames[p] = pd.io.parsers.read_csv(
            pair_path, header=True, index_col=0,
            parse_dates=True, dayfirst=True,
            names=("Time", "Ask", "Bid", "AskVolume", "BidVolume")
        )
        self.pair_frames[p]["Pair"] = p
        return pd.concat(self.pair_frames.values()).sort().iterrows()

    def _update_csv_for_day(self):
            return False

    def stream_next_tick(self):
        try:
            index, row = next(self.cur_date_pairs)
        except StopIteration:
            # End of the current days data
            if self._update_csv_for_day():
                index, row = next(self.cur_date_pairs)
            else: # End of the data
                self.continue_backtest = False
                return
        
        getcontext().rounding = ROUND_HALF_DOWN
        pair = row["Pair"]
        bid = Decimal(str(row["Bid"])).quantize(
            Decimal("0.00001")
        )
        ask = Decimal(str(row["Ask"])).quantize(
            Decimal("0.00001")
        )

        # Create decimalised prices for traded pair
        self.prices[pair]["bid"] = bid
        self.prices[pair]["ask"] = ask
        self.prices[pair]["time"] = index

        # Create decimalised prices for inverted pair
        inv_pair, inv_bid, inv_ask = self.invert_prices(pair, bid, ask)
        self.prices[inv_pair]["bid"] = inv_bid
        self.prices[inv_pair]["ask"] = inv_ask
        self.prices[inv_pair]["time"] = index

        # Create the tick event for the queue
        tev = TickEvent(pair, index, bid, ask)
        self.events_queue.put(tev)
