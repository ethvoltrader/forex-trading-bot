import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("📊 Downloading EUR/USD Historical Data...")
print("=" * 50)

# Download 1 year of EUR/USD data (hourly)
ticker = "EURUSD=X"
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

print(f"Period: {start_date.date()} to {end_date.date()}")
print("Timeframe: 1 hour")
print("Downloading... ⏳")

# Download data
df = yf.download(ticker, start=start_date, end=end_date, interval="1h")

# Clean and prepare data
df.reset_index(inplace=True)
df = df[['Datetime', 'Close']]
df.columns = ['timestamp', 'close']

# Remove any NaN values
df = df.dropna()

# Save to CSV
filename = 'EUR_USD_1h.csv'
df.to_csv(filename, index=False)

print("=" * 50)
print(f"✅ Success! Downloaded {len(df)} data points")
print(f"📁 Saved to: {filename}")
print(f"💰 Price range: ${df['close'].min():.5f} - ${df['close'].max():.5f}")
print("\n🚀 Ready for backtesting!")

