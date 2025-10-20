from paper_trader_alphavantage import AlphaVantagePaperTrader

print("🌐 ALPHA VANTAGE LIVE PAPER TRADING")
print("Using professional real-time forex data!")
print("\n" + "="*70 + "\n")

trader = AlphaVantagePaperTrader(
    from_currency="EUR",
    to_currency="USD",
    initial_capital=1000,
    rsi_buy=25,
    rsi_sell=75,
    simulation_mode=False
)

print("\n⚠️  IMPORTANT:")
print("   - Real LIVE market data from Alpha Vantage")
print("   - Checks every 60 seconds (API rate limit)")
print("   - Session runs for 30 minutes")
print("   - Press Ctrl+C anytime to stop")
print("\n" + "="*70 + "\n")

input("Press ENTER to start live trading with Alpha Vantage... ")

trader.run_paper_trading(
    duration_minutes=30,
    check_interval_seconds=60
)

print("\n✅ Alpha Vantage session complete!")

