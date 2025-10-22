"""
Notification System for Forex Trading Bot
Sends email alerts for trades and daily summaries
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import os
from pathlib import Path


class TradingNotifier:
    def __init__(self, sender_email, sender_password, recipient_email):
        """
        Initialize notification system
        
        Args:
            sender_email: Gmail address to send from
            sender_password: Gmail app password (NOT your regular password!)
            recipient_email: Email address to receive alerts
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        
    def send_email(self, subject, body, html_body=None, image_path=None):
        """Send an email with optional HTML and image attachment"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Add plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Attach image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', 
                                  filename=os.path.basename(image_path))
                    msg.attach(img)
            
            # Connect to SMTP server (supports Gmail, ProtonMail, etc.)
            # ProtonMail uses: smtp.protonmail.com or mail.protonmail.com
            smtp_server = 'smtp.protonmail.com' if 'proton' in self.sender_email else 'smtp.gmail.com'
            
            with smtplib.SMTP_SSL(smtp_server, 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def notify_trade_opened(self, pair, entry_price, position_size, rsi, capital):
        """Send alert when a trade is opened"""
        subject = f"🤖 TRADE OPENED - {pair}"
        
        body = f"""
🚀 NEW TRADE ALERT!

Pair: {pair}
Action: LONG POSITION OPENED
Entry Price: ${entry_price:.5f}
Position Size: ${position_size:.2f}
RSI: {rsi:.1f}
Current Capital: ${capital:.2f}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Your forex bot is working! 📈
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2ecc71;">🚀 NEW TRADE OPENED!</h2>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Pair</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{pair}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Action</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">LONG POSITION OPENED</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Entry Price</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${entry_price:.5f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Position Size</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${position_size:.2f}</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>RSI</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{rsi:.1f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Current Capital</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${capital:.2f}</td>
                </tr>
            </table>
            <p style="margin-top: 20px; color: #666;">
                Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            <p style="color: #2ecc71; font-weight: bold;">Your forex bot is working! 📈</p>
        </body>
        </html>
        """
        
        return self.send_email(subject, body, html_body)
    
    def notify_trade_closed(self, pair, entry_price, exit_price, pnl, pnl_pct, 
                           duration_min, capital, reason="SESSION_END"):
        """Send alert when a trade is closed"""
        
        # Determine if win or loss
        is_win = pnl > 0
        emoji = "✅" if is_win else "❌"
        color = "#2ecc71" if is_win else "#e74c3c"
        
        subject = f"{emoji} TRADE CLOSED - {pair} ({'+' if is_win else ''}{pnl_pct:.2f}%)"
        
        body = f"""
{emoji} TRADE CLOSED!

Pair: {pair}
Entry: ${entry_price:.5f}
Exit: ${exit_price:.5f}

P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)
Duration: {duration_min:.1f} minutes
Reason: {reason}

New Capital: ${capital:.2f}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'Great trade! 🎉' if is_win else 'Small loss, keep going! 💪'}
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: {color};">{emoji} TRADE CLOSED!</h2>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Pair</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{pair}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Entry Price</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${entry_price:.5f}</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Exit Price</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${exit_price:.5f}</td>
                </tr>
                <tr style="background-color: {color}20;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>P&L</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: {color}; font-weight: bold;">
                        ${pnl:+.2f} ({pnl_pct:+.2f}%)
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Duration</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{duration_min:.1f} minutes</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Reason</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{reason}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>New Capital</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${capital:.2f}</td>
                </tr>
            </table>
            <p style="margin-top: 20px; color: #666;">
                Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            <p style="color: {color}; font-weight: bold;">
                {'Great trade! 🎉' if is_win else 'Small loss, keep going! 💪'}
            </p>
        </body>
        </html>
        """
        
        return self.send_email(subject, body, html_body)
    
    def notify_daily_summary(self, trade_history, chart_path=None):
        """Send end-of-day summary with statistics and chart"""
        
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
        
        subject = f"📊 Daily Trading Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
📊 DAILY TRADING SUMMARY

Date: {datetime.now().strftime('%Y-%m-%d')}

PERFORMANCE:
Starting Capital: ${start_capital:.2f}
Ending Capital: ${end_capital:.2f}
Total Return: ${total_pnl:+.2f} ({total_return_pct:+.2f}%)

TRADE STATS:
Total Trades: {total_trades}
Wins: {len(wins)} ({win_rate:.1f}%)
Losses: {len(losses)} ({100-win_rate:.1f}%)
Avg Win: ${avg_win:.2f}
Avg Loss: ${avg_loss:.2f}

See attached chart for visual breakdown!

Keep up the great work! 💪
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #3498db;">📊 DAILY TRADING SUMMARY</h2>
            <p style="color: #666;">Date: {datetime.now().strftime('%Y-%m-%d')}</p>
            
            <h3 style="color: #2ecc71;">💰 PERFORMANCE</h3>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-bottom: 20px;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Starting Capital</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${start_capital:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Ending Capital</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${end_capital:.2f}</td>
                </tr>
                <tr style="background-color: {'#2ecc7120' if total_pnl >= 0 else '#e74c3c20'};">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Return</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: {'#2ecc71' if total_pnl >= 0 else '#e74c3c'};">
                        ${total_pnl:+.2f} ({total_return_pct:+.2f}%)
                    </td>
                </tr>
            </table>
            
            <h3 style="color: #3498db;">📈 TRADE STATS</h3>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Trades</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{total_trades}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Wins</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{len(wins)} ({win_rate:.1f}%)</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Losses</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{len(losses)} ({100-win_rate:.1f}%)</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Avg Win</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${avg_win:.2f}</td>
                </tr>
                <tr style="background-color: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Avg Loss</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${avg_loss:.2f}</td>
                </tr>
            </table>
            
            <p style="margin-top: 20px; color: #2ecc71; font-weight: bold;">
                Keep up the great work! 💪
            </p>
            
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                See attached chart for visual breakdown!
            </p>
        </body>
        </html>
        """
        
        return self.send_email(subject, body, html_body, chart_path)


# Test/Example usage
if __name__ == "__main__":
    print("📧 Testing Notification System...\n")
    print("=" * 60)
    print("\n⚠️  SETUP REQUIRED:")
    print("\n1. You need a Gmail account")
    print("2. Enable 2-factor authentication")
    print("3. Create an 'App Password' for this bot:")
    print("   • Go to: https://myaccount.google.com/apppasswords")
    print("   • Create a new app password")
    print("   • Use that password (NOT your regular Gmail password)")
    print("\n" + "=" * 60)
    print("\n💡 Once you have your app password, update the code below:")
    print("\nExample:")
    print('notifier = TradingNotifier(')
    print('    sender_email="your.email@gmail.com",')
    print('    sender_password="your-16-char-app-password",')
    print('    recipient_email="your.email@gmail.com"')
    print(')')
    print("\n" + "=" * 60)

