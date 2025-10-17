import pandas as pd
from monte_carlo import MonteCarloAnalyzer

print("🚀 Loading EUR/USD data...")
df = pd.read_csv('EUR_USD_1h.csv')
print(f"✅ Loaded {len(df)} data points\n")

# Create Monte Carlo analyzer
mc = MonteCarloAnalyzer(initial_capital=1000)

# Run backtest to get trades (using optimal parameters from walk-forward: RSI 25/75)
print("📊 Running backtest to extract trade history...")
trades_dollar, trades_pct = mc.run_backtest_for_trades(df, rsi_buy=25, rsi_sell=75)
print(f"✅ Extracted {len(trades_pct)} trades\n")

# Show trade statistics
wins = trades_pct[trades_pct > 0]
losses = trades_pct[trades_pct < 0]
print(f"📈 Trade Summary:")
print(f"   Total Trades:  {len(trades_pct)}")
print(f"   Wins:          {len(wins)} ({len(wins)/len(trades_pct)*100:.1f}%)")
print(f"   Losses:        {len(losses)} ({len(losses)/len(trades_pct)*100:.1f}%)")
print(f"   Avg Win:       {wins.mean()*100:+.2f}%")
print(f"   Avg Loss:      {losses.mean()*100:+.2f}%")
print(f"   Total P&L:     ${trades_dollar.sum():.2f}")

# Run Monte Carlo simulation with PERCENTAGE returns (compounding!)
mc_results = mc.run_monte_carlo(
    trades_pct,           # Use percentage returns now!
    n_simulations=10000,  # Run 10,000 simulations
    ruin_threshold=0.5    # Ruin = losing 50% of capital
)

# Analyze results
stats = mc.analyze_results(mc_results)

# Create visualization
mc.visualize_results(mc_results)

print("\n🎉 Monte Carlo analysis complete!")
print("📊 Check monte_carlo_results.png for full visualization")

