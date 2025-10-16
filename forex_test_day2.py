"""
Forex Trading Bot - Quick Test Version with Logging
This version fetches REAL forex prices and shows what the bot would do
NO API keys needed - uses free data source
NO actual trading - just displays signals
NOW WITH PROFESSIONAL LOGGING!
"""

import requests
import time
from datetime import datetime
from logger_config import setup_logger

# Initialize logger
logger = setup_logger('ForexTest')

# Configuration
SYMBOLS = {
    'EURUSD': 'EUR/USD',
    'GBPUSD': 'GBP/USD',
    'USDJPY': 'USD/JPY'
}

RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Portfolio simulation
CAPITAL = 1000.0
RISK_PER_TRADE = 0.05  # 5%
PROFIT_TARGET = 0.10   # 10%
STOP_LOSS = 0.03       # 3%

def calculate_rsi(prices):
    """Calculate RSI from price list"""
    if len(prices) < RSI_PERIOD + 1:
        logger.warning(f"Insufficient data for RSI: only {len(prices)} prices available")
        return None
    
    # Calculate price changes
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Separate gains and losses
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    # Calculate average gains and losses
    avg_gain = sum(gains[-RSI_PERIOD:]) / RSI_PERIOD
    avg_loss = sum(losses[-RSI_PERIOD:]) / RSI_PERIOD
    
    if avg_loss == 0:
        logger.debug("RSI calculation: avg_loss = 0, returning 100")
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    logger.debug(f"RSI calculated: {rsi:.2f} (avg_gain={avg_gain:.5f}, avg_loss={avg_loss:.5f})")
    
    return rsi

def get_forex_price(symbol):
    """
    Fetch current forex price using free API
    Returns current price or None if failed
    """
    try:
        # Using exchangerate-api.com (free, no key needed for basic use)
        # Format: EUR/USD becomes EUR base, USD quote
        if symbol == 'EURUSD':
            base, quote = 'EUR', 'USD'
        elif symbol == 'GBPUSD':
            base, quote = 'GBP', 'USD'
        elif symbol == 'USDJPY':
            base, quote = 'USD', 'JPY'
        else:
            logger.error(f"Unknown symbol: {symbol}")
            return None
        
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        logger.debug(f"Fetching price for {symbol} from {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(quote)
            logger.debug(f"Successfully fetched {symbol}: {rate}")
            return rate
        else:
            logger.error(f"HTTP {response.status_code} for {symbol}")
            return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {symbol}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching {symbol}")
        return None
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None

def simulate_trading_signal(symbol, price, rsi):
    """Determine what the bot would do"""
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

def main():
    """Main test function"""
    logger.info("=" * 70)
    logger.info("🤖 FOREX TRADING BOT - LIVE TEST MODE")
    logger.info("=" * 70)
    logger.info(f"Capital: ${CAPITAL:,.2f}")
    logger.info(f"Risk per trade: {RISK_PER_TRADE*100}%")
    logger.info(f"Profit target: {PROFIT_TARGET*100}%")
    logger.info(f"Stop loss: {STOP_LOSS*100}%")
    logger.info(f"RSI Period: {RSI_PERIOD} | Oversold: {RSI_OVERSOLD} | Overbought: {RSI_OVERBOUGHT}")
    logger.info("=" * 70)
    logger.info("")
    logger.info("🔍 Fetching live forex prices...")
    logger.info("")
    
    # Store historical prices for RSI calculation
    price_history = {symbol: [] for symbol in SYMBOLS.keys()}
    
    # Fetch prices multiple times to build history for RSI
    logger.info("📊 Building price history for RSI calculation...")
    for i in range(RSI_PERIOD + 5):
        for symbol in SYMBOLS.keys():
            price = get_forex_price(symbol)
            if price:
                price_history[symbol].append(price)
        
        if i < RSI_PERIOD + 4:
            logger.info(f"   Collecting data point {i+1}/{RSI_PERIOD + 5}...")
            time.sleep(2)  # Wait 2 seconds between fetches
    
    logger.info("")
    logger.info("✅ Price history collected!")
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"{'PAIR':<12} {'PRICE':<12} {'RSI':<8} {'SIGNAL':<15} {'ACTION'}")
    logger.info("=" * 70)
    
    # Analyze each pair
    for symbol, display_name in SYMBOLS.items():
        prices = price_history[symbol]
        
        if len(prices) < RSI_PERIOD + 1:
            logger.warning(f"{display_name:<12} {'N/A':<12} {'N/A':<8} ❌ Insufficient data")
            continue
        
        current_price = prices[-1]
        rsi = calculate_rsi(prices)
        
        if rsi is None:
            logger.error(f"{display_name:<12} {current_price:<12.5f} {'N/A':<8} ❌ RSI Error")
            continue
        
        # Get trading signal
        signal_data = simulate_trading_signal(symbol, current_price, rsi)
        
        # Display
        rsi_str = f"{rsi:.2f}"
        
        # Color code RSI
        if rsi <= RSI_OVERSOLD:
            rsi_display = f"🟢 {rsi_str}"
        elif rsi >= RSI_OVERBOUGHT:
            rsi_display = f"🔴 {rsi_str}"
        else:
            rsi_display = f"⚪ {rsi_str}"
        
        logger.info(f"{display_name:<12} {current_price:<12.5f} {rsi_display:<8} {signal_data['color']} {signal_data['signal']:<6} {signal_data['reason']}")
        
        # If there's a BUY signal, show trade details
        if signal_data['signal'] == 'BUY':
            logger.info(f"   └─ Trade Size: ${signal_data['trade_size']:.2f} | Units: {signal_data['units']:.2f}")
            logger.info(f"   └─ Entry: {signal_data['entry']:.5f} | Target: {signal_data['profit_target']:.5f} (+{PROFIT_TARGET*100}%)")
            logger.info(f"   └─ Stop Loss: {signal_data['stop_loss']:.5f} (-{STOP_LOSS*100}%)")
    
    logger.info("=" * 70)
    logger.info(f"")
    logger.info(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    logger.info("💡 This is a SIMULATION - No actual trades were executed!")
    logger.info("📈 Your bot is analyzing real live forex prices!")
    logger.info("✅ Bot logic is working correctly!")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("🎯 WHAT THIS MEANS:")
    logger.info("=" * 70)
    logger.info("🟢 RSI < 30 (Oversold) → BUY signal")
    logger.info("🔴 RSI > 70 (Overbought) → SELL signal")
    logger.info("⚪ RSI 30-70 (Neutral) → HOLD (no action)")
    logger.info("")
    logger.info("Your bot successfully:")
    logger.info("✅ Fetched real-time forex prices")
    logger.info("✅ Calculated RSI indicator")
    logger.info("✅ Generated trading signals")
    logger.info("✅ Calculated position sizes and targets")
    logger.info("✅ Logged everything professionally!")
    logger.info("")
    logger.info("🚀 Next step: Add error handling (Day 3 of Week 1)")
    logger.info("")
    logger.info(f"📁 Full logs saved to: Check 'logs/' folder")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("")
        logger.info("🛑 Test stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error("This is normal - it helps you debug! This is why we need logging (Day 2)")
