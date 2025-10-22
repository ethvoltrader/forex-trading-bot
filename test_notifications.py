"""
Test the notification system with your actual trading data
"""

from notifications import TradingNotifier
from email_config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL
from datetime import datetime

# Initialize notifier
notifier = TradingNotifier(
    sender_email=SENDER_EMAIL,
    sender_password=SENDER_PASSWORD,
    recipient_email=RECIPIENT_EMAIL
)

print("📧 Testing Email Notification System...\n")
print("=" * 60)

# Test 1: Trade Opened Alert
print("\n📨 Test 1: Sending 'Trade Opened' alert...")
notifier.notify_trade_opened(
    pair="EUR/USD",
    entry_price=1.16442,
    position_size=50.0,
    rsi=25.5,
    capital=1000.00
)

# Test 2: Trade Closed Alert (WIN)
print("\n📨 Test 2: Sending 'Trade Closed' alert (WIN)...")
notifier.notify_trade_closed(
    pair="EUR/USD",
    entry_price=1.16442,
    exit_price=1.16469,
    pnl=0.23,
    pnl_pct=0.02,
    duration_min=32.1,
    capital=1000.23,
    reason="SESSION_END"
)

# Test 3: Trade Closed Alert (LOSS)
print("\n📨 Test 3: Sending 'Trade Closed' alert (LOSS)...")
notifier.notify_trade_closed(
    pair="EUR/USD",
    entry_price=1.16131,
    exit_price=1.16117,
    pnl=-0.12,
    pnl_pct=-0.01,
    duration_min=59.5,
    capital=1000.11,
    reason="SESSION_END"
)

# Test 4: Daily Summary with Chart
print("\n📨 Test 4: Sending Daily Summary...")

# Your actual trade data
trade_history = [
    {
        'timestamp': datetime(2025, 10, 20, 14, 30),
        'pair': 'EUR/USD',
        'entry_price': 1.16442,
        'exit_price': 1.16469,
        'pnl': 0.23,
        'pnl_pct': 0.02,
        'duration_min': 32.1,
        'capital': 1000.23
    },
    {
        'timestamp': datetime(2025, 10, 21, 9, 9),
        'pair': 'EUR/USD',
        'entry_price': 1.16131,
        'exit_price': 1.16117,
        'pnl': -0.12,
        'pnl_pct': -0.01,
        'duration_min': 59.5,
        'capital': 1000.11
    }
]

# Find the most recent chart (optional)
import glob
chart_files = glob.glob('charts/performance_dashboard_*.png')
latest_chart = max(chart_files) if chart_files else None

notifier.notify_daily_summary(trade_history, chart_path=latest_chart)

print("\n" + "=" * 60)
print("✅ All test emails sent!")
print("\n📬 Check your ProtonMail inbox!")
print("   • You should receive 4 emails")
print("   • Check spam folder if you don't see them")
print("\n💡 If emails aren't arriving:")
print("   • Verify your email_config.py settings")
print("   • Make sure you used the correct ProtonMail password")
print("   • ProtonMail free tier should support SMTP")

