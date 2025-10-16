"""
Historical Data Fetcher for Forex Trading Bot
Downloads real forex price data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from logger_config import setup_logger

logger = setup_logger('DataFetcher')


class ForexDataFetcher:
    """
    Fetch real historical forex data from Yahoo Finance
    
    Usage:
        fetcher = ForexDataFetcher()
        data = fetcher.fetch_forex_data('EUR/USD', '2024-01-01', '2024-10-01')
    """
    
    # Yahoo Finance uses different symbols for forex pairs
    SYMBOL_MAP = {
        'EUR/USD': 'EURUSD=X',
        'GBP/USD': 'GBPUSD=X',
        'USD/JPY': 'USDJPY=X',
        'AUD/USD': 'AUDUSD=X',
        'USD/CAD': 'USDCAD=X',
        'EUR/GBP': 'EURGBP=X'
    }
    
    def __init__(self):
        """Initialize data fetcher"""
        logger.info("ForexDataFetcher initialized")
    
    def fetch_forex_data(self, symbol='EUR/USD', start_date=None, end_date=None):
        """
        Fetch historical forex data from Yahoo Finance
        
        Args:
            symbol (str): Forex pair (e.g., 'EUR/USD')
            start_date (str): Start date 'YYYY-MM-DD' (default: 6 months ago)
            end_date (str): End date 'YYYY-MM-DD' (default: today)
        
        Returns:
            pandas.DataFrame: Historical price data with columns [date, close]
            None: If fetch fails
        
        Example:
            >>> fetcher = ForexDataFetcher()
            >>> data = fetcher.fetch_forex_data('EUR/USD', '2024-01-01', '2024-10-01')
            >>> print(data.head())
        """
        try:
            # Convert symbol to Yahoo Finance format
            if symbol not in self.SYMBOL_MAP:
                logger.error(f"Unsupported symbol: {symbol}")
                logger.info(f"Supported symbols: {list(self.SYMBOL_MAP.keys())}")
                return None
            
            yahoo_symbol = self.SYMBOL_MAP[symbol]
            
            # Set default dates if not provided
            if end_date is None:
                end_dt = datetime.now()
            else:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_date is None:
                start_dt = end_dt - timedelta(days=180)  # 6 months
            else:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            logger.info(f"Fetching {symbol} data from {start_dt.date()} to {end_dt.date()}")
            logger.info(f"Yahoo Finance symbol: {yahoo_symbol}")
            
            # Download data from Yahoo Finance
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(start=start_dt, end=end_dt)
            
            # Check if data was returned
            if df.empty:
                logger.error(f"No data returned for {symbol}")
                logger.warning("This could mean:")
                logger.warning("  1. Invalid date range")
                logger.warning("  2. Yahoo Finance API issue")
                logger.warning("  3. Market was closed during this period")
                return None
            
            # Clean and format data
            df = df.reset_index()
            df = df.rename(columns={'Date': 'date', 'Close': 'close'})
            
            # Keep only date and close price
            df = df[['date', 'close']]
            
            # Remove any NaN values
            df = df.dropna()
            
            logger.info(f"✅ Successfully fetched {len(df)} days of data")
            logger.info(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
            logger.info(f"   Price range: ${df['close'].min():.5f} - ${df['close'].max():.5f}")
            logger.info(f"   Latest price: ${df['close'].iloc[-1]:.5f}")
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            logger.error("Possible issues:")
            logger.error("  - Check internet connection")
            logger.error("  - Yahoo Finance API might be down")
            logger.error("  - Invalid date range")
            return None
    
    def fetch_multiple_pairs(self, symbols, start_date=None, end_date=None):
        """
        Fetch data for multiple forex pairs
        
        Args:
            symbols (list): List of forex pairs
            start_date (str): Start date
            end_date (str): End date
        
        Returns:
            dict: Dictionary with symbol as key, DataFrame as value
        
        Example:
            >>> fetcher = ForexDataFetcher()
            >>> data = fetcher.fetch_multiple_pairs(['EUR/USD', 'GBP/USD'])
            >>> print(data['EUR/USD'].head())
        """
        logger.info(f"Fetching data for {len(symbols)} pairs...")
        
        results = {}
        
        for symbol in symbols:
            logger.info(f"\nFetching {symbol}...")
            data = self.fetch_forex_data(symbol, start_date, end_date)
            
            if data is not None:
                results[symbol] = data
                logger.info(f"✅ {symbol} fetched successfully")
            else:
                logger.warning(f"❌ {symbol} fetch failed")
        
        logger.info(f"\n✅ Fetched {len(results)}/{len(symbols)} pairs successfully")
        
        return results
    
    def get_latest_price(self, symbol='EUR/USD'):
        """
        Get the latest price for a forex pair
        
        Args:
            symbol (str): Forex pair
        
        Returns:
            float: Latest price or None
        """
        try:
            if symbol not in self.SYMBOL_MAP:
                logger.error(f"Unsupported symbol: {symbol}")
                return None
            
            yahoo_symbol = self.SYMBOL_MAP[symbol]
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get just the last day
            df = ticker.history(period='1d')
            
            if df.empty:
                logger.error(f"Could not get latest price for {symbol}")
                return None
            
            latest_price = df['Close'].iloc[-1]
            logger.info(f"{symbol} latest price: ${latest_price:.5f}")
            
            return latest_price
        
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {e}")
            return None
    
    def validate_data(self, df):
        """
        Validate fetched data quality
        
        Args:
            df (DataFrame): Price data to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        if df is None or df.empty:
            logger.error("Data is None or empty")
            return False
        
        # Check for required columns
        required_cols = ['date', 'close']
        if not all(col in df.columns for col in required_cols):
            logger.error(f"Missing required columns. Need: {required_cols}")
            return False
        
        # Check for NaN values
        if df['close'].isna().any():
            nan_count = df['close'].isna().sum()
            logger.warning(f"Found {nan_count} NaN values in price data")
            return False
        
        # Check for zeros or negative prices
        if (df['close'] <= 0).any():
            logger.error("Found zero or negative prices in data")
            return False
        
        # Check for reasonable price range (forex pairs typically between 0.5 and 200)
        min_price = df['close'].min()
        max_price = df['close'].max()
        
        if min_price < 0.5 or max_price > 200:
            logger.warning(f"Unusual price range: ${min_price:.5f} - ${max_price:.5f}")
        
        # Check for sufficient data points
        if len(df) < 30:
            logger.warning(f"Only {len(df)} data points - might not be enough for analysis")
        
        logger.info("✅ Data validation passed")
        return True


def main():
    """Test the data fetcher"""
    print("\n" + "="*70)
    print("🌐 FOREX DATA FETCHER - TEST")
    print("="*70 + "\n")
    
    fetcher = ForexDataFetcher()
    
    # Test 1: Fetch EUR/USD data
    print("Test 1: Fetching EUR/USD (6 months)...")
    data = fetcher.fetch_forex_data('EUR/USD', '2024-04-01', '2024-10-01')
    
    if data is not None:
        print("\n✅ SUCCESS! Data fetched:")
        print(f"   Total days: {len(data)}")
        print(f"   Date range: {data['date'].min().date()} to {data['date'].max().date()}")
        print(f"   Price range: ${data['close'].min():.5f} - ${data['close'].max():.5f}")
        print("\n📊 First 5 days:")
        print(data.head())
        print("\n📊 Last 5 days:")
        print(data.tail())
        
        # Validate data
        if fetcher.validate_data(data):
            print("\n✅ Data validation: PASSED")
        else:
            print("\n❌ Data validation: FAILED")
    else:
        print("\n❌ FAILED to fetch data")
        print("   Check your internet connection or try again later")
    
    print("\n" + "="*70)
    
    # Test 2: Get latest price
    print("\nTest 2: Getting latest price...")
    latest = fetcher.get_latest_price('EUR/USD')
    if latest:
        print(f"✅ EUR/USD current price: ${latest:.5f}")
    
    print("\n" + "="*70)
    print("✅ DATA FETCHER TEST COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
