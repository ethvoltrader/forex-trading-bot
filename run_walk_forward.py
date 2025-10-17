import pandas as pd
from walk_forward import WalkForwardAnalyzer

print("🚀 Loading EUR/USD data...")
df = pd.read_csv('EUR_USD_1h.csv')
print(f"✅ Loaded {len(df)} data points\n")

# Create analyzer
wf = WalkForwardAnalyzer(initial_capital=1000)

# Run walk-forward analysis
# This will split data into 5 windows, train on 70%, test on 30%
results_df = wf.run_walk_forward(
    df, 
    train_size=0.7,     # Use 70% for training
    test_size=0.3,      # Use 30% for testing
    n_windows=5,        # 5 different time periods
    rsi_range=[25, 30, 35, 40, 70, 75, 80]  # RSI values to test
)

# Analyze and display results
metrics = wf.analyze_results(results_df)

# Create visualization
wf.visualize_results(results_df)

print("\n🎉 Walk-forward analysis complete!")
print("📊 Check walk_forward_results.png for visualization")
