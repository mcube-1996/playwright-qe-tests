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
class EMA_Cross_RSI(bt.Strategy):
    params = {
        "slow_ema": 50,
        "fast_ema": 200,
        "rsi_period": 14,
        "rsi_oversold": 30,  # Oversold level for RSI
        "risk_pct": 0.01
    }

    def __init__(self):
        # EMAs for crossover
        self.slow_ema = bt.indicators.EMA(self.data.close, period=self.params.slow_ema)
        self.fast_ema = bt.indicators.EMA(self.data.close, period=self.params.fast_ema)
        self.cross = bt.indicators.CrossOver(self.fast_ema, self.slow_ema)

        # RSI indicator for long entry condition
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

        # Plotting and trade tracking
        self.buy_signal = None
        self.sell_signal = None
        self.entry_price = None
        self.stop_price = None
        self.take_profit_price = None
        self.in_trade = False

        self.total_trades = 0
        self.wins = 0
        self.losses = 0

    def next(self):
        if self.in_trade:
            # Check if SL or TP was hit this bar
            low = self.data.low[0]
            high = self.data.high[0]

            if low <= self.stop_price:
                self.sell_signal = self.data.close[0]
                print(f"💔 Stop Loss Hit at {low:.2f}")
                self.losses += 1
                self.total_trades += 1
                self.in_trade = False
                self.entry_price = None
                self.sell(data=self.data)

            elif high >= self.take_profit_price:
                self.sell_signal = self.data.close[0]
                print(f"🎯 Take Profit Hit at {high:.2f}")
                self.wins += 1
                self.total_trades += 1
                self.in_trade = False
                self.entry_price = None
                self.sell(data=self.data)

        else:
            # Entry condition: EMA crossover AND RSI below 30 (oversold condition)
            if self.cross[0] == 1 and self.rsi[0] < self.params.rsi_oversold and len(self.data) >= 6:
                entry_price = self.data.close[0]
                lowest_low = min(self.data.low.get(size=6))
                sl_distance = entry_price - lowest_low

                if sl_distance <= 0:
                    return

                # Risk sizing
                cash = self.broker.get_cash()
                risk_amount = cash * self.params.risk_pct
                size = risk_amount / sl_distance

                # Set SL and TP
                self.entry_price = entry_price
                self.stop_price = lowest_low
                self.take_profit_price = entry_price + (2 * sl_distance)
                self.in_trade = True

                # Print entry details including RSI
                print(f"\n📈 Entry: {entry_price:.2f} | SL: {self.stop_price:.2f} | TP: {self.take_profit_price:.2f} | RSI: {self.rsi[0]:.2f}")
                self.buy_signal = entry_price
                self.buy(data=self.data)

    def stop(self):
        print("\n--- Backtest Summary ---")
        print(f"Total Trades: {self.total_trades}")
        print(f"Wins: {self.wins}")
        print(f"Losses: {self.losses}")
        if self.total_trades > 0:
            win_rate = self.wins / self.total_trades * 100
            print(f"Win Rate: {win_rate:.2f}%")
        print(f"Final Portfolio Value: {self.broker.getvalue():.2f}")



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
    cerebro.addstrategy(EMA_Cross_RSI)
    cerebro.broker.set_cash(1000)
    cerebro.broker.setcommission(commission=0.001)

    # Run the backtest. The strategy's print statements will output to the console.
    cerebro.run()
    
    # The strategy's stop method will have printed the summary in the console.
    cerebro.plot()




if __name__ == "__main__":
    run_backtest()

