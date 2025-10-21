"""
Test the visualizer with your actual trading data
"""

from visualizer import TradingVisualizer
from datetime import datetime

# Your actual trades!
my_trades = [
    {
        'timestamp': datetime(2025, 10, 20, 14, 30),  # Yesterday afternoon
        'pair': 'EUR/USD',
        'entry_price': 1.16442,
        'exit_price': 1.16469,
        'pnl': 0.23,
        'pnl_pct': 0.02,
        'duration_min': 32.1,
        'capital': 1000.23
    },
    {
        'timestamp': datetime(2025, 10, 21, 9, 9),  # This morning
        'pair': 'EUR/USD',
        'entry_price': 1.16131,
        'exit_price': 1.16117,
        'pnl': -0.12,
        'pnl_pct': -0.01,
        'duration_min': 59.5,
        'capital': 1000.11
    }
]

# Create visualizer
viz = TradingVisualizer(output_dir='charts')

print("🎨 Generating YOUR trading charts...\n")
print("=" * 60)

# Generate full dashboard
print("\n📊 Creating performance dashboard...")
dashboard = viz.create_performance_dashboard(my_trades)

# Generate quick summary
print("\n📈 Creating quick summary...")
summary = viz.create_quick_summary(my_trades)

print("\n" + "=" * 60)
print("✅ DONE! Your charts are ready!")
print("\n📂 Check the 'charts' folder to see:")
print("   1. Full performance dashboard (4 panels)")
print("   2. Quick equity curve summary")
print("\n🎯 You can now:")
print("   • Share these with investors")
print("   • Add to your portfolio")
print("   • Analyze your strategy visually")
print("   • Track progress over time")

