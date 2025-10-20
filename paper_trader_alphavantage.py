from paper_trader import PaperTrader
from alpha_vantage_fetcher import AlphaVantageDataFetcher
import numpy as np
from datetime import datetime

class AlphaVantagePaperTrader(PaperTrader):
    """
    Paper trader using Alpha Vantage for real-time data
    Builds RSI from collected prices over time (no intraday endpoint needed!)
    """
    
    def __init__(self, from_currency="EUR", to_currency="USD", **kwargs):
        self.av_fetcher = AlphaVantageDataFetcher()
        self.from_currency = from_currency
        self.to_currency = to_currency
        
        super().__init__(symbol=f"{from_currency}/{to_currency}", **kwargs)
        print(f"🌐 Using Alpha Vantage for {from_currency}/{to_currency}")
        print(f"📊 Building RSI from live collected prices (no historical data needed!)")
    
    def fetch_current_price(self):
        """
        Fetch current price from Alpha Vantage
        """
        if self.simulation_mode:
            return self.generate_simulated_price()
        
        try:
            quote = self.av_fetcher.get_forex_quote(self.from_currency, self.to_currency)
            if quote and quote['price'] > 0:
                print(f"   💰 Alpha Vantage price: ${quote['price']:.5f}")
                return quote['price']
            return None
        except Exception as e:
            print(f"⚠️  Error fetching price: {e}")
            return None
    
    def fetch_historical_prices(self):
        """
        Use our OWN collected price history instead of API intraday!
        This is better for real-time trading anyway!
        """
        if self.simulation_mode:
            return super().fetch_historical_prices()
        
        # Use prices we've collected over time
        if len(self.price_history) >= self.rsi_period + 1:
            prices = [p['price'] for p in self.price_history[-(self.rsi_period + 1):]]
            print(f"   📈 Using {len(prices)} collected prices for RSI")
            return np.array(prices)
        else:
            # Not enough history yet
            print(f"   ⏳ Collecting prices... ({len(self.price_history)}/{self.rsi_period + 1} needed)")
            return None
    
    def run_trading_cycle(self):
        """
        Override to add Alpha Vantage specific logging
        """
        print(f"\n🔍 Fetching from Alpha Vantage...")
        result = super().run_trading_cycle()
        
        if not result:
            print(f"   ⚠️  Cycle incomplete (not enough data yet)")
        
        return result


if __name__ == "__main__":
    print("📊 Alpha Vantage Paper Trader")
    print("Uses real-time Alpha Vantage data + builds own RSI history!")

