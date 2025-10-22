import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from telegram_notifier import TelegramNotifier
from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class PaperTrader:
    def __init__(self, symbol="EURUSD=X", initial_capital=1000, 
                 rsi_period=14, rsi_buy=25, rsi_sell=75, 
                 simulation_mode=False, simulation_volatility=0.0005):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.rsi_period = rsi_period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell
        
        self.simulation_mode = simulation_mode
        self.simulation_volatility = simulation_volatility
        self.simulated_price = 1.16550
        self.simulated_trend = 0.00001
        
        self.position = None
        self.entry_price = 0
        self.entry_time = None
        self.trades = []
        self.price_history = []
        
        self.stop_loss_pct = 0.03
        self.profit_target_pct = 0.10
        
        mode_str = "SIMULATION MODE 🎮" if simulation_mode else "LIVE MODE 📡"
        
        print("\n" + "="*70)
        print(f"📊 PAPER TRADING SYSTEM INITIALIZED - {mode_str}")
        print("="*70)
        print(f"💱 Symbol:           {self.symbol}")
        print(f"💰 Starting Capital: ${self.initial_capital:,.2f}")
        print(f"📈 RSI Settings:     Buy < {self.rsi_buy}, Sell > {self.rsi_sell}")
        if simulation_mode:
            print(f"🎮 Simulation:       ON (Volatility: {simulation_volatility})")
        print("="*70 + "\n")
        
        # Initialize Telegram notifier
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        print("📱 Telegram notifications: ENABLED\n")
    
    def generate_simulated_price(self):
        change_pct = np.random.normal(self.simulated_trend, self.simulation_volatility)
        self.simulated_price = self.simulated_price * (1 + change_pct)
        
        if np.random.random() < 0.1:
            spike = np.random.normal(0, self.simulation_volatility * 3)
            self.simulated_price = self.simulated_price * (1 + spike)
        
        return self.simulated_price
    
    def fetch_current_price(self):
        if self.simulation_mode:
            return self.generate_simulated_price()
        else:
            try:
                ticker = yf.Ticker(self.symbol)
                data = ticker.history(period="1d", interval="1m")
                if len(data) > 0:
                    return data['Close'].iloc[-1]
                return None
            except Exception as e:
                print(f"⚠️  Error: {e}")
                return None
    
    def fetch_historical_prices(self):
        if self.simulation_mode:
            if len(self.price_history) >= self.rsi_period + 1:
                recent_prices = [p['price'] for p in self.price_history[-(self.rsi_period + 1):]]
                return np.array(recent_prices)
            else:
                return None
        else:
            try:
                ticker = yf.Ticker(self.symbol)
                data = ticker.history(period="5d", interval="1h")
                if len(data) >= self.rsi_period + 1:
                    return data['Close'].values
                return None
            except Exception as e:
                print(f"⚠️  Error: {e}")
                return None
    
    def calculate_rsi(self, prices):
        if len(prices) < self.rsi_period + 1:
            return None
        deltas = np.diff(prices)
        seed = deltas[-(self.rsi_period + 1):]
        up = seed[seed >= 0].sum() / self.rsi_period
        down = -seed[seed < 0].sum() / self.rsi_period
        if down == 0:
            return 100
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def open_position(self, price):
        self.position = 'LONG'
        self.entry_price = price
        self.entry_time = datetime.now()
        print(f"\n🔵 OPENING LONG @ ${price:.5f} | Capital: ${self.capital:,.2f}")
        
        # Send Telegram notification
        try:
            self.notifier.notify_trade_opened(
                pair=self.symbol,
                entry_price=price,
                position_size=self.capital * 0.05,
                rsi=0,
                capital=self.capital
            )
        except Exception as e:
            print(f"⚠️  Telegram alert failed: {e}")
    
    def close_position(self, price, reason):
        if self.position != 'LONG':
            return
        
        pnl_pct = (price - self.entry_price) / self.entry_price
        pnl_dollar = pnl_pct * self.capital
        self.capital += pnl_dollar
        
        exit_time = datetime.now()
        holding_time = (exit_time - self.entry_time).total_seconds() / 60
        
        trade = {
            'entry_price': self.entry_price,
            'exit_price': price,
            'pnl_dollar': pnl_dollar,
            'pnl_pct': pnl_pct * 100,
            'reason': reason,
            'holding_time_min': holding_time
        }
        self.trades.append(trade)
        
        emoji = "✅" if pnl_dollar > 0 else "❌"
        print(f"\n{emoji} CLOSING - {reason}")
        print(f"   Entry: ${self.entry_price:.5f} → Exit: ${price:.5f}")
        print(f"   P&L: ${pnl_dollar:+.2f} ({pnl_pct*100:+.2f}%)")
        print(f"   Held: {holding_time:.1f} min | Capital: ${self.capital:,.2f}")
        
        # Send Telegram notification
        try:
            self.notifier.notify_trade_closed(
                pair=self.symbol,
                entry_price=self.entry_price,
                exit_price=price,
                pnl=pnl_dollar,
                pnl_pct=pnl_pct * 100,
                duration_min=holding_time,
                capital=self.capital,
                reason=reason
            )
        except Exception as e:
            print(f"⚠️  Telegram alert failed: {e}")
        
        self.position = None
        self.entry_price = 0
    
    def run_trading_cycle(self):
        current_price = self.fetch_current_price()
        if current_price is None:
            return False
        
        self.price_history.append({
            'timestamp': datetime.now(),
            'price': current_price
        })
        
        historical_prices = self.fetch_historical_prices()
        if historical_prices is None:
            return False
        
        rsi = self.calculate_rsi(historical_prices)
        if rsi is None:
            return False
        
        now = datetime.now().strftime('%H:%M:%S')
        pos = f"LONG @ ${self.entry_price:.5f}" if self.position else "FLAT"
        
        pnl_str = ""
        if self.position == 'LONG':
            unrealized_pnl_pct = (current_price - self.entry_price) / self.entry_price
            unrealized_pnl_dollar = unrealized_pnl_pct * self.capital
            pnl_color = "+" if unrealized_pnl_dollar >= 0 else ""
            pnl_str = f" | P&L: {pnl_color}${unrealized_pnl_dollar:.2f}"
        
        print(f"[{now}] ${current_price:.5f} | RSI: {rsi:.1f} | {pos}{pnl_str} | Capital: ${self.capital:,.2f}")
        
        if self.position == 'LONG':
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            
            if pnl_pct <= -self.stop_loss_pct:
                self.close_position(current_price, "STOP_LOSS")
            elif pnl_pct >= self.profit_target_pct:
                self.close_position(current_price, "PROFIT_TARGET")
            elif rsi > self.rsi_sell:
                self.close_position(current_price, "RSI_EXIT")
        
        if self.position is None and rsi < self.rsi_buy:
            self.open_position(current_price)
        
        return True
    
    def run_paper_trading(self, duration_minutes=60, check_interval_seconds=5):
        interval_str = f"{check_interval_seconds} seconds" if check_interval_seconds < 60 else f"{check_interval_seconds/60:.0f} minutes"
        print(f"🚀 STARTING {duration_minutes} MINUTE SESSION")
        print(f"🔄 Checking every {interval_str}\n")
        
        if self.simulation_mode:
            print("🎮 Warming up simulation...")
            for i in range(self.rsi_period + 5):
                price = self.generate_simulated_price()
                self.price_history.append({
                    'timestamp': datetime.now(),
                    'price': price
                })
            print(f"✅ Generated {len(self.price_history)} initial prices\n")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        cycle = 0
        
        try:
            while time.time() < end_time:
                cycle += 1
                print(f"\n--- Cycle {cycle} ---")
                success = self.run_trading_cycle()
                if not success:
                    print("⚠️  Cycle failed")
                time.sleep(check_interval_seconds)
            
            if self.position == 'LONG':
                price = self.fetch_current_price()
                if price:
                    self.close_position(price, "SESSION_END")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  STOPPED BY USER")
            if self.position == 'LONG':
                price = self.fetch_current_price()
                if price:
                    self.close_position(price, "USER_STOP")
        
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)
        
        total_return = self.capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        print(f"\n💰 PERFORMANCE:")
        print(f"   Starting Capital: ${self.initial_capital:,.2f}")
        print(f"   Ending Capital:   ${self.capital:,.2f}")
        print(f"   Total Return:     ${total_return:+,.2f} ({total_return_pct:+.2f}%)")
        
        if self.trades:
            wins = [t for t in self.trades if t['pnl_dollar'] > 0]
            losses = [t for t in self.trades if t['pnl_dollar'] < 0]
            
            print(f"\n📈 TRADE STATS:")
            print(f"   Total Trades:     {len(self.trades)}")
            print(f"   Wins:             {len(wins)} ({len(wins)/len(self.trades)*100:.1f}%)")
            print(f"   Losses:           {len(losses)} ({len(losses)/len(self.trades)*100:.1f}%)")
            
            if wins:
                avg_win = np.mean([t['pnl_dollar'] for t in wins])
                print(f"   Avg Win:          ${avg_win:.2f}")
            if losses:
                avg_loss = np.mean([t['pnl_dollar'] for t in losses])
                print(f"   Avg Loss:         ${avg_loss:.2f}")
            
            print(f"\n📋 TRADE LOG:")
            for i, t in enumerate(self.trades, 1):
                emoji = "✅" if t['pnl_dollar'] > 0 else "❌"
                print(f"   {emoji} Trade {i}: {t['reason']}")
                print(f"      ${t['entry_price']:.5f} → ${t['exit_price']:.5f}")
                print(f"      P&L: ${t['pnl_dollar']:+.2f} ({t['pnl_pct']:+.2f}%) | Held: {t['holding_time_min']:.1f} min")
        
        else:
            print(f"\n📈 No trades executed")
        
        print("\n" + "="*70)
        # Send Telegram daily summary
        if self.trades:
            try:
                import glob
                trade_history = []
                for trade in self.trades:
                    trade_history.append({
                        'timestamp': datetime.now(),
                        'pair': self.symbol,
                        'entry_price': trade['entry_price'],
                        'exit_price': trade['exit_price'],
                        'pnl': trade['pnl_dollar'],
                        'pnl_pct': trade['pnl_pct'],
                        'duration_min': trade['holding_time_min'],
                        'capital': self.capital
                    })
                
                chart_files = glob.glob('charts/performance_dashboard_*.png')
                latest_chart = max(chart_files) if chart_files else None
                self.notifier.notify_daily_summary(trade_history, chart_path=latest_chart)
            except Exception as e:
                print(f"⚠️  Telegram summary failed: {e}")
