from paper_trader import PaperTrader

print("🎮 SIMULATION MODE - Paper Trading with Fake Price Movement")
print("\nThis simulates realistic EUR/USD price changes")
print("so you can test your bot logic RIGHT NOW!")
print("\n" + "="*70 + "\n")

# Create paper trader in SIMULATION MODE
trader = PaperTrader(
    symbol="EURUSD=X",
    initial_capital=1000,
    rsi_buy=25,
    rsi_sell=75,
    simulation_mode=True,           # 🎮 SIMULATION ON!
    simulation_volatility=0.0005    # Realistic forex volatility
)

print("📌 SIMULATION INFO:")
print("   - Prices will move up/down realistically")
print("   - Checks every 5 seconds (faster than live!)")
print("   - Session runs for 10 minutes")
print("   - You'll see trades happen in real-time!")
print("   - Press Ctrl+C anytime to stop")
print("\n" + "="*70 + "\n")

input("Press ENTER to start simulation... ")

# Run fast simulation (5 second intervals, 10 minute session)
trader.run_paper_trading(
    duration_minutes=10,        # 10 minute session
    check_interval_seconds=5    # Check every 5 seconds!
)

print("\n✅ Simulation complete!")
print("🎯 This is how your bot will behave when market is open!")
