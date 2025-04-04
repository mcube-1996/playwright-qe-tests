import backtrader as bt
import ccxt
import pandas as pd
import time


# Fetch Data from KuCoin API

def fetch_kucoin_data(symbol="BTC/USDT", timeframe="15m", limit=100000):
    exchange = ccxt.kucoin()
    since = exchange.milliseconds() - (limit * exchange.parse_timeframe(timeframe) * 1000)
    all_data = []

    while len(all_data) < limit:
        remaining = limit - len(all_data)
        fetch_limit = min(remaining, 1500)  # KuCoin max limit per request
        data = exchange.fetch_ohlcv(symbol, timeframe, since, fetch_limit)

        if not data:
            break  # Stop if no more data

        all_data.extend(data)
        since = data[-1][0] + 1  # Move to the next batch
        time.sleep(1)  # Prevent hitting rate limits

    # Convert to DataFrame
    df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")  # Convert timestamp

    return df

# Define Strategy
class EMA_Cross_Printer(bt.Strategy):
    params = {
        "slow_ema": 200,      # 200 EMA
        "fast_ema": 50,       # 50 EMA
        "rsi_period": 14,     # RSI period
        "rsi_threshold": 30   # RSI entry threshold
    }

    def __init__(self):
        # Calculate the EMAs on the close price
        self.slow_ema = bt.indicators.EMA(self.data.close, period=self.params.slow_ema)
        self.fast_ema = bt.indicators.EMA(self.data.close, period=self.params.fast_ema)
        # Track crossovers: +1 when slow EMA crosses above fast EMA, -1 when it crosses below
        self.cross = bt.indicators.CrossOver(self.slow_ema, self.fast_ema)
        # Calculate the RSI
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        # Tracking variables
        self.entry_price = None
        self.total_trades = 0
        self.wins = 0
        self.losses = 0

    def next(self):
        # Entry condition: When 200 EMA crosses above 50 EMA AND RSI is below 30
        if self.cross[0] == 1 and self.rsi[0] < self.params.rsi_threshold:
            if self.entry_price is None:  # Only open a new trade if none is open
                self.entry_price = self.data.close[0]
                print(f"[{self.data.datetime.date(0)}] Entry Price: {self.entry_price} | RSI: {self.rsi[0]}")
                
                # Mark entry on plot
                self.buy(size=1)
                self.plotinfo.plot = True
                self.entry_price = self.data.close[0]  # Set the entry price

        # Exit condition: When 200 EMA crosses below 50 EMA
        elif self.cross[0] == -1:
            if self.entry_price is not None:
                exit_price = self.data.close[0]
                print(f"[{self.data.datetime.date(0)}] Exit Price: {exit_price}")
                self.total_trades += 1
                if exit_price > self.entry_price:
                    self.wins += 1
                    print("Trade Result: WIN")
                else:
                    self.losses += 1
                    print("Trade Result: LOSS")
                
                # Mark exit on plot
                self.sell(size=1)
                self.plotinfo.plot = True
                self.entry_price = None

    def stop(self):
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades else 0
        print("\n--- Backtest Summary ---")
        print(f"Total Trades: {self.total_trades}")
        print(f"Wins: {self.wins}")
        print(f"Losses: {self.losses}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Final Portfolio Value: ${self.broker.getvalue():.2f}")




# Run Backtest
def run_backtest():
    cerebro = bt.Cerebro()
    df = fetch_kucoin_data()
    print(f"DataFrame Size: {df.shape}")

    data = bt.feeds.PandasData(
        dataname=df, 
        datetime=0, open=1, high=2, low=3, close=4, volume=5,
        timeframe=bt.TimeFrame.Minutes, compression=15
    )

    cerebro.adddata(data)
    cerebro.addstrategy(EMA_Cross_Printer)
    cerebro.broker.set_cash(1000)
    cerebro.broker.setcommission(commission=0.001)

    # Run the backtest. The strategy's print statements will output to the console.
    cerebro.run()
    
    # The strategy's stop method will have printed the summary in the console.
    cerebro.plot()




if __name__ == "__main__":
    run_backtest()

