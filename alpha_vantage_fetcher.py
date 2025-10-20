import requests
import os
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

class AlphaVantageDataFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        
        if not self.api_key:
            raise ValueError("API key not found! Set ALPHA_VANTAGE_API_KEY in .env file")
        
        print(f"✅ Alpha Vantage initialized (API Key: {self.api_key[:4]}...)")
    
    def get_forex_quote(self, from_currency="EUR", to_currency="USD"):
        try:
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_currency,
                'to_currency': to_currency,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Error Message' in data:
                print(f"❌ API Error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"⚠️  Rate Limit: {data['Note']}")
                return None
            
            rate_data = data.get('Realtime Currency Exchange Rate', {})
            
            if not rate_data:
                print(f"❌ No data returned")
                return None
            
            result = {
                'price': float(rate_data.get('5. Exchange Rate', 0)),
                'bid': float(rate_data.get('8. Bid Price', 0)),
                'ask': float(rate_data.get('9. Ask Price', 0)),
                'timestamp': rate_data.get('6. Last Refreshed', ''),
                'from': rate_data.get('1. From_Currency Code', ''),
                'to': rate_data.get('3. To_Currency Code', '')
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_forex_intraday(self, from_currency="EUR", to_currency="USD", 
                          interval="5min", outputsize="compact"):
        try:
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': from_currency,
                'to_symbol': to_currency,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Error Message' in data:
                print(f"❌ API Error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"⚠️  Rate Limit: {data['Note']}")
                return None
            
            time_series_key = f'Time Series FX ({interval})'
            time_series = data.get(time_series_key, {})
            
            if not time_series:
                print(f"❌ No time series data")
                return None
            
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ['open', 'high', 'low', 'close']
            df = df.astype(float)
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_connection(self):
        print("\n" + "="*70)
        print("🧪 TESTING ALPHA VANTAGE CONNECTION")
        print("="*70)
        
        print("\n📊 Fetching EUR/USD quote...")
        quote = self.get_forex_quote("EUR", "USD")
        
        if quote:
            print(f"✅ Success!")
            print(f"   Price:     ${quote['price']:.5f}")
            print(f"   Bid:       ${quote['bid']:.5f}")
            print(f"   Ask:       ${quote['ask']:.5f}")
            print(f"   Timestamp: {quote['timestamp']}")
        else:
            print("❌ Failed")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    fetcher = AlphaVantageDataFetcher()
    fetcher.test_connection()

