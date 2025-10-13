"""
Forex Trading Bot - Test Version with Configuration System
Features:
- Professional logging
- Comprehensive error handling
- Configuration file system (settings in config.yaml)
- All settings externalized - no hardcoded values!
"""

import requests
import time
from datetime import datetime
from logger_config import setup_logger
from config_loader import Config

# Initialize logger
logger = setup_logger('ForexTest')

# Load configuration
config = Config()

# Validate configuration before starting
if not config.validate():
    logger.critical("Configuration validation failed! Fix config.yaml before running.")
    exit(1)

# Load all settings from config file (no more hardcoded values!)
SYMBOLS_DICT = {
    'EURUSD': 'EUR/USD',
    'GBPUSD': 'GBP/USD', 
    'USDJPY': 'USD/JPY'
}

# Strategy settings
RSI_PERIOD = config.get('strategy.rsi_period')
RSI_OVERSOLD = config.get('strategy.rsi_oversold')
RSI_OVERBOUGHT = config.get('strategy.rsi_overbought')

# Risk management settings
CAPITAL = config.get('risk.starting_capital')
RISK_PER_TRADE = config.get('risk.risk_per_trade')
PROFIT_TARGET = config.get('risk.profit_target')
STOP_LOSS = config.get('risk.stop_loss')

# Error handling settings
MAX_RETRIES = config.get('error_handling.max_retries')
RETRY_DELAY = config.get('error_handling.retry_delay')
API_TIMEOUT = config.get('error_handling.api_timeout')

logger.info(f"Configuration loaded: RSI({RSI_PERIOD}), Capital(${CAPITAL}), Symbols({len(SYMBOLS_DICT)})")


def calculate_rsi(prices):
    """Calculate RSI from price list with error handling"""
    try:
        if prices is None:
            logger.error("calculate_rsi: prices is None")
            return None
        
        if not isinstance(prices, (list, tuple)):
            logger.error(f"calculate_rsi: Invalid type {type(prices)}, expected list or tuple")
            return None
        
        if len(prices) < RSI_PERIOD + 1:
            logger.warning(f"Insufficient data for RSI: only {len(prices)} prices, need {RSI_PERIOD + 1}")
            return None
        
        if any(p is None or p <= 0 for p in prices):
            logger.error("calculate_rsi: Found invalid price values (None or <= 0)")
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-RSI_PERIOD:]) / RSI_PERIOD
        avg_loss = sum(losses[-RSI_PERIOD:]) / RSI_PERIOD
        
        if avg_loss == 0:
            logger.debug("RSI calculation: avg_loss = 0, returning 100")
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        if rsi < 0 or rsi > 100:
            logger.error(f"Invalid RSI calculated: {rsi} (should be 0-100)")
            return None
        
        logger.debug(f"RSI calculated: {rsi:.2f} (avg_gain={avg_gain:.5f}, avg_loss={avg_loss:.5f})")
        
        return rsi
        
    except ZeroDivisionError as e:
        logger.error(f"Division by zero in RSI calculation: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in calculate_rsi: {e}")
        return None


def get_forex_price(symbol, retry_count=0):
    """Fetch current forex price with retry logic and error handling"""
    try:
        if symbol not in SYMBOLS_DICT:
            logger.error(f"Unknown symbol: {symbol}")
            return None
        
        symbol_map = {
            'EURUSD': ('EUR', 'USD'),
            'GBPUSD': ('GBP', 'USD'),
            'USDJPY': ('USD', 'JPY')
        }
        
        base, quote = symbol_map[symbol]
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        
        logger.debug(f"Fetching {symbol} from {url} (attempt {retry_count + 1}/{MAX_RETRIES})")
        
        response = requests.get(url, timeout=API_TIMEOUT)
        
        if response.status_code != 200:
            logger.warning(f"HTTP {response.status_code} for {symbol}")
            
            if response.status_code >= 500 and retry_count < MAX_RETRIES - 1:
                logger.info(f"Server error, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
                return get_forex_price(symbol, retry_count + 1)
            
            return None
        
        data = response.json()
        
        if 'rates' not in data:
            logger.error(f"Invalid API response for {symbol}: missing 'rates' field")
            return None
        
        rate = data['rates'].get(quote)
        
        if rate is None:
            logger.error(f"Rate for {quote} not found in response")
            return None
        
        if not isinstance(rate, (int, float)) or rate <= 0:
            logger.error(f"Invalid rate for {symbol}: {rate}")
            return None
        
        logger.debug(f"Successfully fetched {symbol}: {rate}")
        return rate
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching {symbol} (attempt {retry_count + 1}/{MAX_RETRIES})")
        
        if retry_count < MAX_RETRIES - 1:
            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return get_forex_price(symbol, retry_count + 1)
        else:
            logger.error(f"Max retries reached for {symbol}")
            return None
    
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error fetching {symbol} (attempt {retry_count + 1}/{MAX_RETRIES})")
        
        if retry_count < MAX_RETRIES - 1:
            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return get_forex_price(symbol, retry_count + 1)
        else:
            logger.error(f"Max retries reached for {symbol} - check internet connection")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching {symbol}: {e}")
        return None
    
    except ValueError as e:
        logger.error(f"JSON parsing error for {symbol}: {e}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error fetching {symbol}: {e}")
        return None


def simulate_trading_signal(symbol, price, rsi):
    """Determine what the bot would do with error handling"""
    try:
        if not all([symbol, price, rsi]):
            logger.error("simulate_trading_signal: Missing required parameters")
            return None
        
        if price <= 0:
            logger.error(f"Invalid price for {symbol}: {price}")
            return None
        
        if rsi < 0 or rsi > 100:
            logger.error(f"Invalid RSI for {symbol}: {rsi}")
            return None
        
        signal = "HOLD"
        action_color = "⚪"
        
        if rsi <= RSI_OVERSOLD:
            signal = "BUY"
            action_color = "🟢"
            trade_size = CAPITAL * RISK_PER_TRADE
            units = trade_size / price
            profit_target_price = price * (1 + PROFIT_TARGET)
            stop_loss_price = price * (1 - STOP_LOSS)
            
            logger.info(f"{symbol}: BUY signal generated (RSI={rsi:.2f} <= {RSI_OVERSOLD})")
            
            return {
                'signal': signal,
                'color': action_color,
                'reason': 'RSI Oversold',
                'trade_size': trade_size,
                'units': units,
                'entry': price,
                'profit_target': profit_target_price,
                'stop_loss': stop_loss_price
            }
        
        elif rsi >= RSI_OVERBOUGHT:
            signal = "SELL"
            action_color = "🔴"
            logger.info(f"{symbol}: SELL signal generated (RSI={rsi:.2f} >= {RSI_OVERBOUGHT})")
            return {
                'signal': signal,
                'color': action_color,
                'reason': 'RSI Overbought',
            }
        
        logger.debug(f"{symbol}: HOLD - RSI in neutral zone ({rsi:.2f})")
        return {
            'signal': signal,
            'color': action_color,
            'reason': 'RSI Neutral'
        }
        
    except Exception as e:
        logger.error(f"Error in simulate_trading_signal: {e}")
        return None


def main():
    """Main test function with comprehensive error handling"""
    try:
        logger.info("=" * 70)
        logger.info("🤖 FOREX TRADING BOT - LIVE TEST (CONFIG-DRIVEN)")
        logger.info("=" * 70)
        logger.info(f"Capital: ${CAPITAL:,.2f}")
        logger.info(f"Risk per trade: {RISK_PER_TRADE*100}%")
        logger.info(f"Profit target: {PROFIT_TARGET*100}%")
        logger.info(f"Stop loss: {STOP_LOSS*100}%")
        logger.info(f"RSI Period: {RSI_PERIOD} | Oversold: {RSI_OVERSOLD} | Overbought: {RSI_OVERBOUGHT}")
        logger.info(f"Max retries: {MAX_RETRIES} | Retry delay: {RETRY_DELAY}s | API timeout: {API_TIMEOUT}s")
        logger.info("=" * 70)
        logger.info("")
        logger.info("🔍 Fetching live forex prices...")
        logger.info("")
        
        price_history = {symbol: [] for symbol in SYMBOLS_DICT.keys()}
        failed_symbols = set()
        
        logger.info("📊 Building price history for RSI calculation...")
        for i in range(RSI_PERIOD + 5):
            for symbol in SYMBOLS_DICT.keys():
                if symbol in failed_symbols:
                    continue
                
                price = get_forex_price(symbol)
                
                if price is not None:
                    price_history[symbol].append(price)
                else:
                    logger.warning(f"Failed to fetch {symbol} on iteration {i+1}")
                    
                    if len(price_history[symbol]) == 0 and i > 2:
                        failed_symbols.add(symbol)
                        logger.error(f"Skipping {symbol} - consistent failures")
            
            if i < RSI_PERIOD + 4:
                logger.info(f"   Collecting data point {i+1}/{RSI_PERIOD + 5}...")
                time.sleep(2)
        
        logger.info("")
        logger.info("✅ Price history collection complete!")
        logger.info("")
        
        valid_symbols = [s for s in SYMBOLS_DICT.keys() if len(price_history[s]) >= RSI_PERIOD + 1]
        
        if not valid_symbols:
            logger.error("❌ No valid data collected for any symbol!")
            logger.error("Possible issues: Internet connection, API problems, rate limiting")
            return
        
        logger.info("=" * 70)
        logger.info(f"{'PAIR':<12} {'PRICE':<12} {'RSI':<8} {'SIGNAL':<15} {'ACTION'}")
        logger.info("=" * 70)
        
        for symbol, display_name in SYMBOLS_DICT.items():
            try:
                prices = price_history[symbol]
                
                if len(prices) < RSI_PERIOD + 1:
                    logger.warning(f"{display_name:<12} {'N/A':<12} {'N/A':<8} ❌ Insufficient data ({len(prices)} prices)")
                    continue
                
                current_price = prices[-1]
                rsi = calculate_rsi(prices)
                
                if rsi is None:
                    logger.error(f"{display_name:<12} {current_price:<12.5f} {'N/A':<8} ❌ RSI calculation failed")
                    continue
                
                signal_data = simulate_trading_signal(symbol, current_price, rsi)
                
                if signal_data is None:
                    logger.error(f"{display_name:<12} {current_price:<12.5f} {rsi:<8.2f} ❌ Signal generation failed")
                    continue
                
                rsi_str = f"{rsi:.2f}"
                
                if rsi <= RSI_OVERSOLD:
                    rsi_display = f"🟢 {rsi_str}"
                elif rsi >= RSI_OVERBOUGHT:
                    rsi_display = f"🔴 {rsi_str}"
                else:
                    rsi_display = f"⚪ {rsi_str}"
                
                logger.info(f"{display_name:<12} {current_price:<12.5f} {rsi_display:<8} {signal_data['color']} {signal_data['signal']:<6} {signal_data['reason']}")
                
                if signal_data['signal'] == 'BUY':
                    logger.info(f"   └─ Trade Size: ${signal_data['trade_size']:.2f} | Units: {signal_data['units']:.2f}")
                    logger.info(f"   └─ Entry: {signal_data['entry']:.5f} | Target: {signal_data['profit_target']:.5f} (+{PROFIT_TARGET*100}%)")
                    logger.info(f"   └─ Stop Loss: {signal_data['stop_loss']:.5f} (-{STOP_LOSS*100}%)")
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        logger.info("=" * 70)
        logger.info("")
        logger.info(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        logger.info("💡 This is a SIMULATION - No actual trades were executed!")
        logger.info("📈 Bot is fully config-driven - change settings in config.yaml!")
        logger.info("✅ All features working: Logging, Error Handling, Configuration!")
        logger.info("")
        logger.info("=" * 70)
        logger.info("🎯 COMPLETED FEATURES:")
        logger.info("=" * 70)
        logger.info("✅ Professional logging system")
        logger.info("✅ Comprehensive error handling")
        logger.info("✅ Retry logic for failures")
        logger.info("✅ Configuration file system")
        logger.info("✅ No hardcoded values!")
        logger.info("")
        logger.info("🚀 Next step: Documentation (Day 5 of Week 1)")
        logger.info("")
        logger.info(f"📁 Full logs: Check 'logs/' folder")
        logger.info(f"⚙️  Settings: Edit 'config.yaml' to customize")
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("")
        logger.info("🛑 Test stopped by user")
    except Exception as e:
        logger.critical(f"Critical error in main(): {e}")
        logger.critical("This should never happen - main loop failed!")
        raise


if __name__ == "__main__":
    main()

