"""
Backtesting Framework for Forex Trading Bot
Tests trading strategies on historical data to evaluate performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logger_config import setup_logger
from config_loader import Config
from data_fetcher import ForexDataFetcher

# Initialize
logger = setup_logger('Backtest')
config = Config()

# Load strategy settings from config
RSI_PERIOD = config.get('strategy.rsi_period', 14)
RSI_OVERSOLD = config.get('strategy.rsi_oversold', 30)
RSI_OVERBOUGHT = config.get('strategy.rsi_overbought', 70)
STARTING_CAPITAL = config.get('risk.starting_capital', 1000.0)
RISK_PER_TRADE = config.get('risk.risk_per_trade', 0.05)
PROFIT_TARGET = config.get('risk.profit_target', 0.10)
STOP_LOSS = config.get('risk.stop_loss', 0.03)


class BacktestEngine:
    """
    Backtesting engine that simulates trading on historical data
    
    Usage:
        engine = BacktestEngine(symbol='EUR/USD', start_date='2024-01-01')
        results = engine.run_backtest()
        engine.print_results()
    """
    
    def __init__(self, symbol='EUR/USD', start_date=None, end_date=None):
        """
        Initialize backtest engine
        
        Args:
            symbol (str): Trading pair (e.g., 'EUR/USD')
            start_date (str): Start date 'YYYY-MM-DD' (default: 6 months ago)
            end_date (str): End date 'YYYY-MM-DD' (default: today)
        """
        self.symbol = symbol
        
        # Set default dates if not provided
        if end_date is None:
            self.end_date = datetime.now()
        else:
            self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date is None:
            self.start_date = self.end_date - timedelta(days=180)  # 6 months
        else:
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Trading state
        self.capital = STARTING_CAPITAL
        self.position = None  # Current position (None, 'LONG')
        self.entry_price = 0.0
        self.position_size = 0.0
        
        # Track performance
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Backtest initialized: {symbol} from {self.start_date.date()} to {self.end_date.date()}")
    
    def calculate_rsi(self, prices, period=14):
        """
        Calculate RSI indicator
        
        Args:
            prices (list/array): Price data
            period (int): RSI period
        
        Returns:
            float: RSI value or None
        """
        try:
            if len(prices) < period + 1:
                return None
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def generate_sample_data(self, days=180):
        """
        Generate sample historical price data for testing
        
        In production, you'd fetch real data from an API
        This creates realistic-looking data for demonstration
        
        Args:
            days (int): Number of days of data to generate
        
        Returns:
            pandas.DataFrame: Price data with dates
        """
        logger.info(f"Generating {days} days of sample price data...")
        
        # Starting price (realistic for EUR/USD)
        base_price = 1.10
        
        # Generate dates
        dates = pd.date_range(start=self.start_date, periods=days, freq='D')
        
        # Generate realistic price movements
        # Random walk with slight upward bias
        np.random.seed(42)  # For reproducibility
        returns = np.random.normal(0.0001, 0.005, days)  # Small daily returns
        
        prices = [base_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'close': prices
        })
        
        logger.info(f"Generated data: {len(df)} days, range ${df['close'].min():.5f} - ${df['close'].max():.5f}")
        
        return df
    
    def open_position(self, date, price):
        """
        Open a long position
        
        Args:
            date: Trade date
            price: Entry price
        """
        if self.position is not None:
            return  # Already in position
        
        trade_size = self.capital * RISK_PER_TRADE
        self.position = 'LONG'
        self.entry_price = price
        self.position_size = trade_size / price
        
        logger.debug(f"{date.date()}: OPEN LONG @ ${price:.5f}, size: {self.position_size:.2f} units")
    
    def close_position(self, date, price, reason='SIGNAL'):
        """
        Close current position
        
        Args:
            date: Trade date
            price: Exit price
            reason: Reason for closing
        
        Returns:
            dict: Trade details
        """
        if self.position is None:
            return None
        
        # Calculate profit/loss
        exit_value = self.position_size * price
        entry_value = self.position_size * self.entry_price
        profit = exit_value - entry_value
        profit_pct = (price - self.entry_price) / self.entry_price
        
        # Update capital
        self.capital += profit
        
        # Record trade
        trade = {
            'entry_date': self.entry_date,
            'exit_date': date,
            'entry_price': self.entry_price,
            'exit_price': price,
            'profit': profit,
            'profit_pct': profit_pct,
            'reason': reason
        }
        
        self.trades.append(trade)
        
        logger.debug(f"{date.date()}: CLOSE @ ${price:.5f}, P/L: ${profit:.2f} ({profit_pct*100:.2f}%), Reason: {reason}")
        
        # Reset position
        self.position = None
        self.entry_price = 0.0
        self.position_size = 0.0
        
        return trade
    
    def run_backtest(self):
        """
        Run the backtest on historical data
        
        Returns:
            dict: Backtest results
        """
        logger.info("=" * 70)
        logger.info("STARTING BACKTEST")
        logger.info("=" * 70)
        
        # Get historical data (using sample data for now)
        df = self.generate_sample_data(days=int((self.end_date - self.start_date).days))
        
        # Run through each day
        for i in range(RSI_PERIOD + 1, len(df)):
            date = df.iloc[i]['date']
            price = df.iloc[i]['close']
            
            # Calculate RSI
            recent_prices = df.iloc[i-RSI_PERIOD-1:i+1]['close'].values
            rsi = self.calculate_rsi(recent_prices, RSI_PERIOD)
            
            if rsi is None:
                continue
            
            # Track equity
            current_equity = self.capital
            if self.position == 'LONG':
                current_equity += (self.position_size * price) - (self.position_size * self.entry_price)
            self.equity_curve.append({
                'date': date,
                'equity': current_equity
            })
            
            # Check if we're in a position
            if self.position == 'LONG':
                # Check exit conditions
                
                # 1. Profit target
                if price >= self.entry_price * (1 + PROFIT_TARGET):
                    self.close_position(date, price, 'PROFIT_TARGET')
                
                # 2. Stop loss
                elif price <= self.entry_price * (1 - STOP_LOSS):
                    self.close_position(date, price, 'STOP_LOSS')
                
                # 3. RSI overbought
                elif rsi >= RSI_OVERBOUGHT:
                    self.close_position(date, price, 'RSI_OVERBOUGHT')
            
            else:
                # Check entry conditions
                if rsi <= RSI_OVERSOLD:
                    self.entry_date = date
                    self.open_position(date, price)
        
        # Close any open position at end
        if self.position == 'LONG':
            final_price = df.iloc[-1]['close']
            final_date = df.iloc[-1]['date']
            self.close_position(final_date, final_price, 'END_OF_BACKTEST')
        
        logger.info("=" * 70)
        logger.info("BACKTEST COMPLETE")
        logger.info("=" * 70)
        
        return self.calculate_results()
    
    def calculate_results(self):
        """
        Calculate performance metrics
        
        Returns:
            dict: Performance statistics
        """
        if not self.trades:
            logger.warning("No trades executed during backtest!")
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'total_return': 0,
                'avg_profit_per_trade': 0
            }
        
        winning_trades = [t for t in self.trades if t['profit'] > 0]
        losing_trades = [t for t in self.trades if t['profit'] <= 0]
        
        total_profit = sum(t['profit'] for t in self.trades)
        total_return = ((self.capital - STARTING_CAPITAL) / STARTING_CAPITAL) * 100
        
        results = {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0,
            'total_profit': total_profit,
            'total_return': total_return,
            'avg_profit_per_trade': total_profit / len(self.trades) if self.trades else 0,
            'final_capital': self.capital,
            'starting_capital': STARTING_CAPITAL,
            'best_trade': max(self.trades, key=lambda x: x['profit'])['profit'] if self.trades else 0,
            'worst_trade': min(self.trades, key=lambda x: x['profit'])['profit'] if self.trades else 0
        }
        
        return results
    
    def print_results(self):
        """Print formatted backtest results"""
        results = self.calculate_results()
        
        print("\n" + "=" * 70)
        print("📊 BACKTEST RESULTS")
        print("=" * 70)
        print(f"Symbol: {self.symbol}")
        print(f"Period: {self.start_date.date()} to {self.end_date.date()}")
        print(f"Strategy: RSI({RSI_PERIOD}) - Buy<{RSI_OVERSOLD}, Sell>{RSI_OVERBOUGHT}")
        print("=" * 70)
        
        print(f"\n💰 PERFORMANCE:")
        print(f"  Starting Capital:  ${results['starting_capital']:,.2f}")
        print(f"  Final Capital:     ${results['final_capital']:,.2f}")
        print(f"  Total Profit/Loss: ${results['total_profit']:,.2f}")
        print(f"  Total Return:      {results['total_return']:.2f}%")
        
        print(f"\n📈 TRADE STATISTICS:")
        print(f"  Total Trades:      {results['total_trades']}")
        print(f"  Winning Trades:    {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"  Losing Trades:     {results['losing_trades']}")
        print(f"  Avg Profit/Trade:  ${results['avg_profit_per_trade']:.2f}")
        
        if results['total_trades'] > 0:
            print(f"\n🎯 BEST/WORST:")
            print(f"  Best Trade:        ${results['best_trade']:.2f}")
            print(f"  Worst Trade:       ${results['worst_trade']:.2f}")
        
        print("\n" + "=" * 70)
        
        # Show sample trades
        if len(self.trades) > 0:
            print("\n📜 SAMPLE TRADES (First 5):")
            print("-" * 70)
            for i, trade in enumerate(self.trades[:5]):
                print(f"{i+1}. {trade['entry_date'].date()} → {trade['exit_date'].date()}")
                print(f"   Entry: ${trade['entry_price']:.5f} | Exit: ${trade['exit_price']:.5f}")
                print(f"   P/L: ${trade['profit']:.2f} ({trade['profit_pct']*100:.2f}%) | {trade['reason']}")
                print()
            
            if len(self.trades) > 5:
                print(f"... and {len(self.trades) - 5} more trades")
        
        print("=" * 70 + "\n")


def main():
    """Run a sample backtest"""
    print("\n🚀 FOREX TRADING BOT - BACKTESTING ENGINE")
    print("=" * 70)
    
    # Create backtest engine
    engine = BacktestEngine(
        symbol='EUR/USD',
        start_date='2024-04-01',  # 6 months ago
        end_date='2024-10-01'
    )
    
    # Run backtest
    results = engine.run_backtest()
    
    # Print results
    engine.print_results()
    
    # Analysis
    if results['total_return'] > 0:
        print("✅ Strategy was PROFITABLE!")
    else:
        print("❌ Strategy LOST money - needs optimization")
    
    if results['win_rate'] > 50:
        print(f"✅ Win rate above 50%: {results['win_rate']:.1f}%")
    else:
        print(f"⚠️  Win rate below 50%: {results['win_rate']:.1f}%")
    
    print("\n" + "=" * 70)
    print("💡 Next steps:")
    print("  - Try different RSI values (edit config.yaml)")
    print("  - Test on different time periods")
    print("  - Add more currency pairs")
    print("  - Create performance charts (Day 3)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

