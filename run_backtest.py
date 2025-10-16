import pandas as pd
from visualizer import PerformanceVisualizer

# Load the data
print("📊 Loading EUR/USD data...")
df = pd.read_csv('EUR_USD_1h.csv')
print(f"✅ Loaded {len(df)} data points")

# Simple RSI Strategy Backtest
class SimpleBacktester:
    def __init__(self, initial_capital=1000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None
        self.entry_price = 0
        self.results = []
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        import numpy as np
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        if down == 0:
            return 100
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def run(self, df, rsi_buy=30, rsi_sell=70, stop_loss=0.03, profit_target=0.10):
        print(f"\n🚀 Running backtest...")
        print(f"Strategy: RSI Buy<{rsi_buy}, Sell>{rsi_sell}")
        print(f"Risk: SL={stop_loss*100}%, PT={profit_target*100}%")
        print("=" * 60)
        
        for i in range(14, len(df)):
            current_price = df.iloc[i]['close']
            prices = df.iloc[i-14:i]['close'].values
            rsi = self.calculate_rsi(prices)
            
            trade_pnl = 0
            
            # Exit logic
            if self.position == 'LONG':
                pnl_pct = (current_price - self.entry_price) / self.entry_price
                
                if pnl_pct <= -stop_loss:
                    trade_pnl = (current_price - self.entry_price) * (self.capital / self.entry_price)
                    self.capital += trade_pnl
                    print(f"🛑 Stop Loss | Trade: ${trade_pnl:.2f} | Capital: ${self.capital:.2f}")
                    self.position = None
                
                elif pnl_pct >= profit_target:
                    trade_pnl = (current_price - self.entry_price) * (self.capital / self.entry_price)
                    self.capital += trade_pnl
                    print(f"🎯 Profit Target | Trade: ${trade_pnl:.2f} | Capital: ${self.capital:.2f}")
                    self.position = None
                
                elif rsi > rsi_sell:
                    trade_pnl = (current_price - self.entry_price) * (self.capital / self.entry_price)
                    self.capital += trade_pnl
                    print(f"📈 RSI Exit | RSI={rsi:.1f} | Trade: ${trade_pnl:.2f} | Capital: ${self.capital:.2f}")
                    self.position = None
            
            # Entry logic
            if self.position is None and rsi < rsi_buy:
                self.position = 'LONG'
                self.entry_price = current_price
                print(f"🔵 BUY | RSI={rsi:.1f} | Entry: ${current_price:.5f}")
            
            # Record state
            self.results.append({
                'timestamp': df.iloc[i]['timestamp'],
                'close': current_price,
                'rsi': rsi,
                'position': self.position,
                'capital': self.capital,
                'trade_pnl': trade_pnl
            })
        
        # Close final position
        if self.position == 'LONG':
            final_price = df.iloc[-1]['close']
            trade_pnl = (final_price - self.entry_price) * (self.capital / self.entry_price)
            self.capital += trade_pnl
            print(f"🔚 Final Exit | Trade: ${trade_pnl:.2f} | Final: ${self.capital:.2f}")
        
        print("=" * 60)
        return pd.DataFrame(self.results)

# Run the backtest
bt = SimpleBacktester(initial_capital=1000)
results_df = bt.run(df, rsi_buy=30, rsi_sell=70)

# Print summary
total_return = bt.capital - bt.initial_capital
total_return_pct = (total_return / bt.initial_capital) * 100
trades = results_df[results_df['trade_pnl'] != 0]
wins = (trades['trade_pnl'] > 0).sum()
losses = (trades['trade_pnl'] < 0).sum()
win_rate = (wins / len(trades) * 100) if len(trades) > 0 else 0

print("\n📊 RESULTS SUMMARY")
print("=" * 60)
print(f"Initial Capital:    ${bt.initial_capital:,.2f}")
print(f"Final Capital:      ${bt.capital:,.2f}")
print(f"Total Return:       ${total_return:,.2f} ({total_return_pct:+.2f}%)")
print(f"Total Trades:       {len(trades)}")
print(f"Wins/Losses:        {wins}/{losses}")
print(f"Win Rate:           {win_rate:.1f}%")
print("=" * 60)

# Generate visualizations
print("\n🎨 Generating charts...")
viz = PerformanceVisualizer(results_df)
viz.generate_all_charts()

print("\n✅ DONE! Check your folder for 3 beautiful PNG charts! 📊")
