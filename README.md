# Forex Trading Bot

A Python-based automated forex trading bot with RSI (Relative Strength Index) strategy, professional logging, error handling, and configuration management.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 Features

- **RSI-Based Strategy**: Automated trading signals using Relative Strength Index
- **Multi-Pair Support**: Trade EUR/USD, GBP/USD, and USD/JPY simultaneously
- **Professional Logging**: Dual-output logging system (console + file) with multiple log levels
- **Error Handling**: Comprehensive retry logic, timeout handling, and graceful error recovery
- **Configuration-Driven**: All settings externalized in YAML files - no hardcoded values
- **Risk Management**: Built-in stop loss, profit targets, and position sizing
- **Demo Mode**: Safe testing with simulation mode before live trading

## 📊 Strategy Overview

**Entry Signals:**
- **BUY**: When RSI falls below 30 (oversold condition)
- **SELL**: When RSI rises above 70 (overbought condition)

**Exit Conditions:**
- Profit target reached (default: 10% gain)
- Stop loss triggered (default: 3% loss)
- Opposite RSI signal (oversold → overbought or vice versa)

**Risk Management:**
- Position sizing: 5% of capital per trade (configurable)
- Maximum 3 retry attempts for failed API calls
- 10-second timeout protection on API requests

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection for live market data

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ethvoltrader/forex-trading-bot.git
cd forex-trading-bot
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install pyyaml requests
```

4. **Configure the bot**

Edit `config.yaml` to customize settings:
```yaml
strategy:
  rsi_period: 14        # RSI calculation period
  rsi_oversold: 30      # Buy signal threshold
  rsi_overbought: 70    # Sell signal threshold

risk:
  starting_capital: 1000.0   # Your capital in USD
  risk_per_trade: 0.05       # 5% per trade
  profit_target: 0.10        # 10% profit target
  stop_loss: 0.03            # 3% stop loss
```

### Running the Bot

**Test Mode (Recommended First):**
```bash
python forex_test.py
```

This runs the bot in simulation mode with live market data but no actual trades.

**View Logs:**
```bash
# See the latest log file
ls -lt logs/

# View log contents
cat logs/bot_*.log
```

## 📁 Project Structure

```
forex-trading-bot/
├── config.yaml              # Main configuration file
├── config_loader.py         # Configuration management system
├── logger_config.py         # Logging system setup
├── forex_bot.py            # Main trading bot (full implementation)
├── forex_test.py           # Test script with live data
├── logs/                   # Log files directory (auto-created)
│   └── bot_YYYYMMDD_HHMMSS.log
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## ⚙️ Configuration

All bot settings are in `config.yaml`. Key sections:

### Strategy Settings
```yaml
strategy:
  rsi_period: 14          # Number of periods for RSI calculation
  rsi_oversold: 30        # Below this = BUY signal
  rsi_overbought: 70      # Above this = SELL signal
  timeframe: '1h'         # Timeframe for analysis
```

### Risk Management
```yaml
risk:
  starting_capital: 1000.0    # Starting balance (USD)
  risk_per_trade: 0.05        # 5% of capital per trade
  profit_target: 0.10         # Take profit at 10%
  stop_loss: 0.03             # Stop loss at 3%
```

### Trading Pairs
```yaml
symbols:
  - 'EUR/USD'
  - 'GBP/USD'
  - 'USD/JPY'
```

Add or remove pairs as needed.

### Error Handling
```yaml
error_handling:
  max_retries: 3        # Retry failed API calls
  retry_delay: 5        # Seconds between retries
  api_timeout: 10       # API request timeout
```

## 📊 Example Output

```
======================================================================
🤖 FOREX TRADING BOT - LIVE TEST (CONFIG-DRIVEN)
======================================================================
Capital: $1,000.00
Risk per trade: 5.0%
Profit target: 10.0%
Stop loss: 3.0%
RSI Period: 14 | Oversold: 30 | Overbought: 70
======================================================================

PAIR         PRICE        RSI      SIGNAL          ACTION
======================================================================
EUR/USD      1.08520      🟢 28.15  🟢 BUY    RSI Oversold
   └─ Trade Size: $50.00 | Units: 46.06
   └─ Entry: 1.08520 | Target: 1.19372 (+10.0%)
   └─ Stop Loss: 1.05264 (-3.0%)
GBP/USD      1.26340      ⚪ 45.67  ⚪ HOLD   RSI Neutral
USD/JPY      149.85000    🔴 72.40  🔴 SELL   RSI Overbought
======================================================================
```

## 🔧 Customization

### Change Trading Strategy

**More Conservative (Lower Risk):**
```yaml
risk:
  risk_per_trade: 0.02      # 2% per trade
  profit_target: 0.05       # 5% profit
  stop_loss: 0.02           # 2% stop loss
```

**More Aggressive:**
```yaml
strategy:
  rsi_oversold: 25          # Buy earlier
  rsi_overbought: 75        # Sell later
```

### Add More Currency Pairs

```yaml
symbols:
  - 'EUR/USD'
  - 'GBP/USD'
  - 'USD/JPY'
  - 'AUD/USD'     # Australian Dollar
  - 'USD/CAD'     # Canadian Dollar
  - 'EUR/GBP'     # Euro vs Pound
```

### Adjust Logging

```yaml
logging:
  console_level: 'WARNING'   # Less console output
  file_level: 'DEBUG'        # Detailed file logs
```

## 🛡️ Safety Features

- ✅ **Simulation Mode**: Test without risking real money
- ✅ **Retry Logic**: Automatic retry on network failures (3 attempts)
- ✅ **Timeout Protection**: 10-second timeout on API calls
- ✅ **Data Validation**: Checks for invalid prices and RSI values
- ✅ **Error Recovery**: Continues trading other pairs if one fails
- ✅ **Comprehensive Logging**: Track every decision for review

## 📈 Performance Tracking

All trades are logged with:
- Timestamp
- Entry/exit prices
- RSI values at trade time
- Position sizes
- Profit/loss
- Reason for trade (signal type)

View logs in the `logs/` directory:
```bash
cat logs/bot_*.log | grep "signal generated"
```

## ⚠️ Risk Warning

**IMPORTANT:** Trading forex carries significant risk of loss. This bot is for educational purposes.

- Past performance does not guarantee future results
- Never trade with money you cannot afford to lose
- Always test thoroughly in demo mode first
- Start with small amounts when going live
- Monitor the bot regularly

## 🛠️ Technical Details

**Built With:**
- Python 3.8+
- PyYAML - Configuration management
- Requests - API calls
- Custom logging system
- Custom error handling

**Architecture:**
- Object-oriented design
- Modular components (logging, config, strategy)
- Separation of concerns
- Professional error handling patterns

## 📚 Code Examples

### Using the Config System

```python
from config_loader import Config

config = Config()

# Get strategy settings
rsi_period = config.get('strategy.rsi_period')
oversold = config.get('strategy.rsi_oversold')

# Get risk settings
capital = config.get('risk.starting_capital')
risk = config.get('risk.risk_per_trade')

# Validate configuration
if config.validate():
    print("Config valid!")
```

### Using the Logger

```python
from logger_config import setup_logger

logger = setup_logger('MyBot')

logger.info("Bot started")
logger.debug("Detailed debug info")
logger.warning("Something to watch")
logger.error("Something went wrong")
```

## 🗺️ Roadmap

**Week 1 - Complete:**
- [x] Git and GitHub setup
- [x] Professional logging system
- [x] Error handling and retry logic
- [x] Configuration system
- [x] Documentation

**Week 2 - Planned:**
- [ ] Backtesting framework
- [ ] Multi-timeframe analysis
- [ ] Additional indicators (MACD, Moving Averages)
- [ ] Web dashboard for monitoring
- [ ] Database storage for trade history

**Future Features:**
- [ ] Telegram/Discord alerts
- [ ] Multiple broker support (Oanda, FXCM, Interactive Brokers)
- [ ] Machine learning integration
- [ ] Portfolio optimization
- [ ] Paper trading competition mode

## 🤝 Contributing

This is a learning project. Suggestions and improvements welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - Feel free to use and modify for your own projects.

## 👤 Author

**ethvoltrader**
- GitHub: [@ethvoltrader](https://github.com/ethvoltrader)

## 🙏 Acknowledgments

- Built with [CCXT](https://github.com/ccxt/ccxt) architecture patterns
- Inspired by traditional RSI trading strategies
- Free market data provided by exchangerate-api.com

## 📞 Support

For questions or issues:
1. Check the logs in `logs/` directory
2. Review `config.yaml` for correct settings
3. Open an issue on GitHub

---

**⚡ Built with Python | 📊 Trading Strategy | 🤖 Automated | 📈 Portfolio Project**

