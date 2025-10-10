import ccxt
import numpy as np
import pandas as pd
import time
from datetime import datetime

# Configuration - FOREX SPECIFIC
EXCHANGE = 'oanda'  # Can also use: 'fxcm', 'interactivebrokers'
SYMBOLS = ['EUR/USD', 'GBP/USD', 'USD/JPY']  # Forex pairs
TIMEFRAME = '1h'
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Portfolio Management (from our previous bot)
STARTING_CAPITAL = 1000.0
RISK_PER_TRADE = 0.05      # 5% of capital per trade
PROFIT_TARGET = 0.10       # 10% profit target
STOP_LOSS = 0.03           # 3% stop loss

SLEEP_SECONDS = 3600  # Check every hour
SIMULATION = True     # Set False for real trading

# Position tracking class (adapted from crypto bot)
class ForexPosition:
    def __init__(self, symbol):
        self.symbol = symbol
        self.position = 'FLAT'
        self.entry_price = 0.0
        self.position_size = 0.0
        self.units = 0.0
        
    def open_long(self, price, trade_size_usd):
        self.position = 'LONG'
        self.entry_price = price
        self.position_size = trade_size_usd
        # For forex, calculate units (standard lots, mini lots, or micro lots)
        self.units = trade_size_usd / price
        return True
    
    def close_position(self, price):
        if self.position == 'LONG':
            profit_usd = (price - self.entry_price) * self.units
            profit_pct = (price - self.entry_price) / self.entry_price
            self.position = 'FLAT'
            self.entry_price = 0.0
            self.position_size = 0.0
            units_closed = self.units
            self.units = 0.0
            return True, profit_usd, profit_pct, units_closed
        return False, 0, 0, 0
    
    def should_take_profit(self, current_price):
        if self.position == 'LONG' and self.entry_price > 0:
            profit_pct = (current_price - self.entry_price) / self.entry_price
            return profit_pct >= PROFIT_TARGET
        return False
    
    def should_stop_loss(self, current_price):
        if self.position == 'LONG' and self.entry_price > 0:
            loss_pct = (current_price - self.entry_price) / self.entry_price
            return loss_pct <= -STOP_LOSS
        return False

class ForexPortfolio:
    def __init__(self, starting_capital):
        self.cash = starting_capital
        self.starting_capital = starting_capital
        self.positions = {symbol: ForexPosition(symbol) for symbol in SYMBOLS}
        self.trade_history = []
        
    def get_portfolio_value(self, current_prices):
        total_value = self.cash
        for symbol, position in self.positions.items():
            if position.position == 'LONG':
                current_price = current_prices.get(symbol, 0)
                total_value += position.units * current_price
        return total_value
    
    def get_available_capital(self):
        # Calculate how much capital is not tied up in positions
        used_capital = sum(pos.position_size for pos in self.positions.values() if pos.position == 'LONG')
        return self.cash - used_capital
    
    def get_trade_size_usd(self):
        return self.get_available_capital() * RISK_PER_TRADE
    
    def can_open_position(self, symbol):
        position = self.positions[symbol]
        trade_size = self.get_trade_size_usd()
        return position.position == 'FLAT' and self.get_available_capital() >= trade_size
    
    def open_position(self, symbol, price):
        if self.can_open_position(symbol):
            trade_size = self.get_trade_size_usd()
            position = self.positions[symbol]
            success = position.open_long(price, trade_size)
            if success:
                self.log_trade(symbol, 'BUY', price, position.units, trade_size)
            return success
        return False
    
    def close_position(self, symbol, price, reason='RSI_SIGNAL'):
        position = self.positions[symbol]
        success, profit_usd, profit_pct, units = position.close_position(price)
        if success:
            self.cash += profit_usd + position.position_size
            self.log_trade(symbol, 'SELL', price, units, profit_usd, profit_pct, reason)
        return success
    
    def log_trade(self, symbol, action, price, units, amount, profit_pct=0, reason=''):
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': action,
            'price': price,
            'units': units,
            'amount_usd': amount,
            'profit_pct': profit_pct * 100,
            'reason': reason,
            'portfolio_value': self.get_portfolio_value({})
        }
        self.trade_history.append(trade)
        
        # Print trade log
        if action == 'BUY':
            print(f"[{trade['timestamp']}] 🟢 BUY {symbol} @ {price:.5f} | Units: {units:.2f} | Cost: ${amount:.2f}")
        else:
            print(f"[{trade['timestamp']}] 🔴 SELL {symbol} @ {price:.5f} | Units: {units:.2f} | "
                  f"Profit: ${amount:.2f} ({profit_pct:.2f}%) | Reason: {reason}")
    
    def get_performance_stats(self):
        total_trades = len([t for t in self.trade_history if t['action'] == 'SELL'])
        if total_trades == 0:
            return None
        
        winning_trades = len([t for t in self.trade_history if t['action'] == 'SELL' and t['amount_usd'] > 0])
        win_rate = (winning_trades / total_trades) * 100
        total_profit = sum([t['amount_usd'] for t in self.trade_history if t['action'] == 'SELL'])
        roi = ((self.cash - self.starting_capital) / self.starting_capital) * 100
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'roi': roi,
            'current_cash': self.cash
        }

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    deltas = np.diff(prices)
    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_market_data(exchange, symbol, timeframe, limit=100):
    """Fetch OHLCV data for forex pair"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df['close'].values
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def trading_loop():
    """Main trading loop for forex bot"""
    # Initialize exchange
    if SIMULATION:
        print("🔹 SIMULATION MODE - No real trades will be executed")
    
    exchange = ccxt.oanda({
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_API_SECRET',
        'enableRateLimit': True,
    })
    
    # For demo, you can use sandbox mode
    exchange.set_sandbox_mode(SIMULATION)
    
    # Initialize portfolio
    portfolio = ForexPortfolio(STARTING_CAPITAL)
    print(f"\n💰 Starting Forex Trading Bot")
    print(f"Capital: ${STARTING_CAPITAL}")
    print(f"Pairs: {', '.join(SYMBOLS)}")
    print(f"Strategy: RSI | Profit Target: {PROFIT_TARGET*100}% | Stop Loss: {STOP_LOSS*100}%")
    print("=" * 70)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n[Iteration {iteration}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 70)
            
            current_prices = {}
            
            # Check each forex pair
            for symbol in SYMBOLS:
                try:
                    # Get market data
                    closes = get_market_data(exchange, symbol, TIMEFRAME)
                    if closes is None or len(closes) < RSI_PERIOD + 1:
                        continue
                    
                    current_price = closes[-1]
                    current_prices[symbol] = current_price
                    rsi = calculate_rsi(closes, RSI_PERIOD)
                    
                    position = portfolio.positions[symbol]
                    
                    print(f"{symbol}: Price: {current_price:.5f} | RSI: {rsi:.2f} | Position: {position.position}")
                    
                    # Check if we have an open position
                    if position.position == 'LONG':
                        # Check profit target
                        if position.should_take_profit(current_price):
                            portfolio.close_position(symbol, current_price, 'PROFIT_TARGET')
                        # Check stop loss
                        elif position.should_stop_loss(current_price):
                            portfolio.close_position(symbol, current_price, 'STOP_LOSS')
                        # Check RSI exit signal
                        elif rsi >= RSI_OVERBOUGHT:
                            portfolio.close_position(symbol, current_price, 'RSI_OVERBOUGHT')
                    
                    # Check for entry signal
                    elif position.position == 'FLAT' and rsi <= RSI_OVERSOLD:
                        if portfolio.can_open_position(symbol):
                            portfolio.open_position(symbol, current_price)
                
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    continue
            
            # Display portfolio status
            portfolio_value = portfolio.get_portfolio_value(current_prices)
            print(f"\n📊 Portfolio Value: ${portfolio_value:.2f} | Available Cash: ${portfolio.get_available_capital():.2f}")
            
            # Display performance stats
            stats = portfolio.get_performance_stats()
            if stats:
                print(f"📈 Stats: {stats['total_trades']} trades | {stats['win_rate']:.1f}% win rate | "
                      f"ROI: {stats['roi']:.2f}% | Total P/L: ${stats['total_profit']:.2f}")
            
            print(f"\n⏰ Sleeping for {SLEEP_SECONDS} seconds...")
            time.sleep(SLEEP_SECONDS)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user.")
        
        # Final summary
        print("\n" + "=" * 70)
        print("FINAL SUMMARY")
        print("=" * 70)
        final_stats = portfolio.get_performance_stats()
        if final_stats:
            print(f"Total Trades: {final_stats['total_trades']}")
            print(f"Winning Trades: {final_stats['winning_trades']}")
            print(f"Win Rate: {final_stats['win_rate']:.2f}%")
            print(f"Total Profit/Loss: ${final_stats['total_profit']:.2f}")
            print(f"ROI: {final_stats['roi']:.2f}%")
            print(f"Final Capital: ${final_stats['current_cash']:.2f}")
        
        # Display trade history
        if portfolio.trade_history:
            print("\n📜 Trade History:")
            for trade in portfolio.trade_history:
                print(f"  {trade['timestamp']} | {trade['action']} {trade['symbol']} @ {trade['price']:.5f}")

if __name__ == "__main__":
    trading_loop()
