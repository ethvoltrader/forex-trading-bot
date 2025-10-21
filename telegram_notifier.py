"""
Telegram Notification System for Forex Trading Bot
Sends instant alerts to your Telegram
"""

import requests
from datetime import datetime


class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Bot token from BotFather
            chat_id: Your Telegram chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, text, parse_mode='HTML'):
        """Send a message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram message sent!")
                return True
            else:
                print(f"❌ Telegram failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def send_photo(self, photo_path, caption=''):
        """Send a photo to Telegram"""
        try:
            url = f"{self.base_url}/sendPhoto"
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Telegram photo sent!")
                return True
            else:
                print(f"❌ Photo failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Photo error: {e}")
            return False
    
    def notify_trade_opened(self, pair, entry_price, position_size, rsi, capital):
        """Send alert when a trade is opened"""
        text = f"""
🚀 <b>NEW TRADE OPENED!</b>

<b>Pair:</b> {pair}
<b>Action:</b> LONG POSITION
<b>Entry Price:</b> ${entry_price:.5f}
<b>Position Size:</b> ${position_size:.2f}
<b>RSI:</b> {rsi:.1f}
<b>Current Capital:</b> ${capital:.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Your forex bot is working!
        """
        return self.send_message(text)
    
    def notify_trade_closed(self, pair, entry_price, exit_price, pnl, pnl_pct, 
                           duration_min, capital, reason="SESSION_END"):
        """Send alert when a trade is closed"""
        
        # Determine if win or loss
        is_win = pnl > 0
        emoji = "✅" if is_win else "❌"
        
        text = f"""
{emoji} <b>TRADE CLOSED!</b>

<b>Pair:</b> {pair}
<b>Entry:</b> ${entry_price:.5f}
<b>Exit:</b> ${exit_price:.5f}

{'🎉' if is_win else '📉'} <b>P&L:</b> ${pnl:+.2f} ({pnl_pct:+.2f}%)
<b>Duration:</b> {duration_min:.1f} minutes
<b>Reason:</b> {reason}

<b>New Capital:</b> ${capital:.2f}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'Great trade! 🎉' if is_win else 'Small loss, keep going! 💪'}
        """
        return self.send_message(text)
    
    def notify_daily_summary(self, trade_history, chart_path=None):
        """Send end-of-day summary with statistics"""
        
        if not trade_history:
            return False
        
        # Calculate summary stats
        total_trades = len(trade_history)
        wins = [t for t in trade_history if t['pnl'] > 0]
        losses = [t for t in trade_history if t['pnl'] < 0]
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in trade_history)
        start_capital = trade_history[0]['capital'] - trade_history[0]['pnl']
        end_capital = trade_history[-1]['capital']
        total_return_pct = ((end_capital - start_capital) / start_capital) * 100
        
        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
        
        text = f"""
📊 <b>DAILY TRADING SUMMARY</b>

📅 {datetime.now().strftime('%Y-%m-%d')}

💰 <b>PERFORMANCE</b>
<b>Starting Capital:</b> ${start_capital:.2f}
<b>Ending Capital:</b> ${end_capital:.2f}
<b>Total Return:</b> ${total_pnl:+.2f} ({total_return_pct:+.2f}%)

📈 <b>TRADE STATS</b>
<b>Total Trades:</b> {total_trades}
<b>Wins:</b> {len(wins)} ({win_rate:.1f}%)
<b>Losses:</b> {len(losses)} ({100-win_rate:.1f}%)
<b>Avg Win:</b> ${avg_win:.2f}
<b>Avg Loss:</b> ${avg_loss:.2f}

💪 Keep up the great work!
        """
        
        # Send text summary
        self.send_message(text)
        
        # Send chart if available
        if chart_path:
            self.send_photo(chart_path, caption="📊 Performance Dashboard")
        
        return True


# Test function
if __name__ == "__main__":
    print("📱 Telegram Notifier Module")
    print("=" * 60)
    print("\n⚠️  To test, run: python test_telegram.py")
    print("\nMake sure you've created telegram_config.py with:")
    print("  • TELEGRAM_BOT_TOKEN")
    print("  • TELEGRAM_CHAT_ID")

