import src.settings as settings
from src.ExecutionHandler.execution import SimulatedExecution
from src.Portfolio.portfolio import Portfolio
from src.Strategy.strategy import MovingAverageCrossStrategy
from src.DataHandler.HistoricCSVDataHandler import HistoricCSVPriceHandler
import Queue as queue
from decimal import Decimal
import time
import sys
import os

pairs = [sys.argv[1]] # ["GBPUSD"]  #
strategy_params = {
    "short_window": 500,
    "long_window": 2000
}
equity = Decimal(sys.argv[2])  # Decimal(10000.0)  #
file_path = os.path.join(settings.CSV_DATA_DIR,sys.argv[3])  # "GBPUSD_20140102.csv")  #
event_queue = queue.Queue()
market_data = HistoricCSVPriceHandler(pairs,event_queue,file_path) # LoadData, generates MARKET event on new data arrived
strategy = MovingAverageCrossStrategy(pairs, event_queue, **strategy_params) # Trading strategy - later will use Strategy patter to change during execution
portfolio = Portfolio(market_data, event_queue, equity=equity,backtest=True) # Stores openned positions, and will analyze trading events according to Portfolio and
                               # current market state

execution = SimulatedExecution()

print("Running Backtest...")
iters = 0
max_iters = 100
while iters < max_iters and market_data.continue_backtest:
    try:
        event = event_queue.get(False)
    except queue.Empty:
        market_data.stream_next_tick()
    else:
        if event is not None:
            if event.type == 'TICK':
                strategy.calculate_signals(event)
                portfolio.update_portfolio(event)
            elif event.type == 'SIGNAL':
                portfolio.execute_signal(event)
            elif event.type == 'ORDER':
                execution.execute_order(event)
    time.sleep(0.1)
    iters += 1

#print("Calculating Performance Metrics...")
#portfolio.output_results()