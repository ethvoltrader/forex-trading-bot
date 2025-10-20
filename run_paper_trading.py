from paper_trader import PaperTrader

print("🚀 Welcome to Paper Trading!")
print("\nThis will test your strategy with REAL current market data")
print("using FAKE money (zero risk!)")
print("\n" + "="*70 + "\n")

# Create paper trader with optimal parameters from Week 2
trader = PaperTrader(
    symbol="EURUSD=X",       # EUR/USD forex pair
    initial_capital=1000,    # Start with $1,000 fake money
    rsi_buy=25,             # Buy when RSI < 25 (from walk-forward)
    rsi_sell=75,            # Sell when RSI > 75 (from walk-forward)
)

# Run paper trading session
print("📌 INSTRUCTIONS:")
print("   - Bot will check market every 60 seconds")
print("   - Session runs for 60 minutes (1 hour)")
print("   - Press Ctrl+C anytime to stop early")
print("   - All trades are SIMULATED (no real money!)")
print("\n" + "="*70 + "\n")

input("Press ENTER to start paper trading... ")

# Start trading!
trader.run_paper_trading(
    duration_minutes=60,         # Run for 1 hour
    check_interval_seconds=60    # Check every 60 seconds
)

print("\n✅ Paper trading session complete!")
print("📊 Review your results above")
