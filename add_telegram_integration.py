"""
Automatic Telegram Integration Script
Adds Telegram notifications to paper_trader.py with perfect indentation
"""

# Read the original file
with open('paper_trader.py', 'r') as f:
    lines = f.readlines()

# Find and modify specific lines
modified_lines = []
for i, line in enumerate(lines):
    modified_lines.append(line)
    
    # 1. Add imports after warnings line
    if 'warnings.filterwarnings' in line:
        modified_lines.append('from telegram_notifier import TelegramNotifier\n')
        modified_lines.append('from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID\n')
    
    # 2. Add notifier initialization after the print("="*70 + "\n") in __init__
    if line.strip() == 'print("="*70 + "\\n")' and i < 50:  # In __init__ section
        modified_lines.append('        \n')
        modified_lines.append('        # Initialize Telegram notifier\n')
        modified_lines.append('        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)\n')
        modified_lines.append('        print("📱 Telegram notifications: ENABLED\\n")\n')
    
    # 3. Add notification in open_position after the print statement
    if 'OPENING LONG @' in line and 'print' in line:
        modified_lines.append('        \n')
        modified_lines.append('        # Send Telegram notification\n')
        modified_lines.append('        try:\n')
        modified_lines.append('            self.notifier.notify_trade_opened(\n')
        modified_lines.append('                pair=self.symbol,\n')
        modified_lines.append('                entry_price=price,\n')
        modified_lines.append('                position_size=self.capital * 0.05,\n')
        modified_lines.append('                rsi=0,\n')
        modified_lines.append('                capital=self.capital\n')
        modified_lines.append('            )\n')
        modified_lines.append('        except Exception as e:\n')
        modified_lines.append('            print(f"⚠️  Telegram alert failed: {e}")\n')
    
    # 4. Add notification in close_position after holding_time print
    if 'Held:' in line and 'holding_time' in line and 'print' in line:
        modified_lines.append('        \n')
        modified_lines.append('        # Send Telegram notification\n')
        modified_lines.append('        try:\n')
        modified_lines.append('            self.notifier.notify_trade_closed(\n')
        modified_lines.append('                pair=self.symbol,\n')
        modified_lines.append('                entry_price=self.entry_price,\n')
        modified_lines.append('                exit_price=price,\n')
        modified_lines.append('                pnl=pnl_dollar,\n')
        modified_lines.append('                pnl_pct=pnl_pct * 100,\n')
        modified_lines.append('                duration_min=holding_time,\n')
        modified_lines.append('                capital=self.capital,\n')
        modified_lines.append('                reason=reason\n')
        modified_lines.append('            )\n')
        modified_lines.append('        except Exception as e:\n')
        modified_lines.append('            print(f"⚠️  Telegram alert failed: {e}")\n')

# Write the modified file
with open('paper_trader.py', 'w') as f:
    f.writelines(modified_lines)

print("✅ Telegram integration added successfully!")
print("🧪 Test it with: python3 run_paper_trading.py")
