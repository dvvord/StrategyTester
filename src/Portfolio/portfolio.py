from __future__ import print_function

from copy import deepcopy
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import logging
import os
import sqlite3


import pandas as pd

from src.Events.event import SignalEvent
from src.Performance.performance import create_drawdowns
from position import Position
from src.settings import OUTPUT_RESULTS_DIR
from src.settings import DB_PATH

class Portfolio(object):
    def __init__(
        self, ticker, events, home_currency="GBP", 
        leverage=20, equity=Decimal("100000.00"), 
        risk_per_trade=Decimal("0.02"), backtest=True
    ):
        self.ticker = ticker
        self.events = events
        self.home_currency = home_currency
        self.leverage = leverage
        self.equity = equity
        self.balance = deepcopy(self.equity)
        self.risk_per_trade = risk_per_trade
        self.backtest = backtest
        self.trade_units = self.calc_risk_position_size()
        self.positions = {}
        self.logger = logging.getLogger(__name__)
        self.conn = sqlite3.connect(DB_PATH)

    def calc_risk_position_size(self):
        return self.equity * self.risk_per_trade

    def add_new_position(
        self, position_type, currency_pair, units, ticker
    ):
        ps = Position(
            self.home_currency, position_type, 
            currency_pair, units, ticker
        )
        self.positions[currency_pair] = ps

    def add_position_units(self, currency_pair, units):
        if currency_pair not in self.positions:
            return False
        else:
            ps = self.positions[currency_pair]
            ps.add_units(units)
            return True

    def remove_position_units(self, currency_pair, units):
        if currency_pair not in self.positions:
            return False
        else:
            ps = self.positions[currency_pair]
            pnl = ps.remove_units(units)
            self.balance += pnl
            return True

    def close_position(self, currency_pair):
        if currency_pair not in self.positions:
            return False
        else:
            ps = self.positions[currency_pair]
            pnl = ps.close_position()
            self.balance += pnl
            del[self.positions[currency_pair]]
            return True

    def update_portfolio(self, tick_event):
        currency_pair = tick_event.instrument
        if currency_pair in self.positions:
            ps = self.positions[currency_pair]
            ps.update_position_price()
        if self.backtest:
            out_line = "%s,%s" % (tick_event.time, self.balance)
            for pair in self.ticker.pairs:
                if pair in self.positions:
                    out_line += ",%s" % self.positions[pair].profit_base
                else:
                    out_line += ",0.00"
            out_line += "\n"
            self.conn.execute("INSERT INTO StrategyUI_Trade VALUES (" + out_line.strip() +");")
            self.conn.commit()
            print(out_line[:-2])

    def execute_signal(self, signal_event):
        # Check that the prices ticker contains all necessary
        # currency pairs prior to executing an order
        execute = True
        tp = self.ticker.prices
        for pair in tp:
            if tp[pair]["ask"] is None or tp[pair]["bid"] is None:
                execute = False

        # All necessary pricing data is available,
        # we can execute
        if execute:
            side = signal_event.side
            currency_pair = signal_event.instrument
            units = int(self.trade_units)
            time = signal_event.time
            
            # If there is no position, create one
            if currency_pair not in self.positions:
                if side == "buy":
                    position_type = "long"
                else:
                    position_type = "short"
                self.add_new_position(
                    position_type, currency_pair, 
                    units, self.ticker
                )

            # If a position exists add or remove units
            else:
                ps = self.positions[currency_pair]

                if side == "buy" and ps.position_type == "long":
                    add_position_units(currency_pair, units)

                elif side == "sell" and ps.position_type == "long":
                    if units == ps.units:
                        self.close_position(currency_pair)
                    elif units < ps.units:
                        return
                    elif units > ps.units:
                        return

                elif side == "buy" and ps.position_type == "short":
                    if units == ps.units:
                        self.close_position(currency_pair)
                    elif units < ps.units:
                        return
                    elif units > ps.units:
                        return
                        
                elif side == "sell" and ps.position_type == "short":
                    add_position_units(currency_pair, units)

            order = OrderEvent(currency_pair, units, "market", side)
            self.events.put(order)

            self.logger.info("Portfolio Balance: %s" % self.balance)
        else:
            self.logger.info("Unable to execute order as price data was insufficient.")
