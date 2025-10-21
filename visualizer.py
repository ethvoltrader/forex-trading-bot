"""
Performance Visualization Module for Forex Trading Bot
Creates professional charts and analytics
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Set style for professional charts
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

class TradingVisualizer:
    def __init__(self, output_dir='charts'):
        """Initialize visualizer with output directory for charts"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_performance_dashboard(self, trade_history):
        """
        Create a comprehensive 4-panel performance dashboard
        
        Args:
            trade_history: List of trade dictionaries with keys:
                - 'timestamp': datetime
                - 'pair': str (e.g., 'EUR/USD')
                - 'entry_price': float
                - 'exit_price': float
                - 'pnl': float (profit/loss in dollars)
                - 'pnl_pct': float (profit/loss percentage)
                - 'duration_min': float
                - 'capital': float (capital after trade)
        """
        if not trade_history:
            print("⚠️  No trades to visualize yet!")
            return None
            
        df = pd.DataFrame(trade_history)
        
        # Create 2x2 subplot dashboard
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🤖 Forex Trading Bot - Performance Dashboard', 
                     fontsize=16, fontweight='bold', y=0.995)
        
        # --- PANEL 1: Equity Curve ---
        ax1.plot(range(len(df)), df['capital'], 
                linewidth=2.5, color='#2ecc71', marker='o', markersize=6)
        ax1.fill_between(range(len(df)), df['capital'], 
                         alpha=0.3, color='#2ecc71')
        ax1.set_title('💰 Equity Curve - Capital Over Time', 
                     fontsize=12, fontweight='bold', pad=10)
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Capital ($)')
        ax1.grid(True, alpha=0.3)
        
        # Add start/end annotations
        start_capital = df['capital'].iloc[0] - df['pnl'].iloc[0]
        end_capital = df['capital'].iloc[-1]
        total_return = end_capital - start_capital
        total_return_pct = (total_return / start_capital) * 100
        
        color = '#2ecc71' if total_return >= 0 else '#e74c3c'
        ax1.axhline(y=start_capital, color='gray', linestyle='--', 
                   alpha=0.5, label=f'Starting: ${start_capital:.2f}')
        ax1.text(len(df)-1, end_capital, 
                f'${end_capital:.2f}\n({total_return_pct:+.2f}%)', 
                fontsize=10, fontweight='bold', color=color,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax1.legend()
        
        # --- PANEL 2: Win/Loss Distribution ---
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] < 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / len(df)) * 100 if len(df) > 0 else 0
        
        bars = ax2.bar(['Wins', 'Losses'], [win_count, loss_count],
                      color=['#2ecc71', '#e74c3c'], alpha=0.7, edgecolor='black')
        ax2.set_title(f'📊 Win/Loss Distribution - Win Rate: {win_rate:.1f}%', 
                     fontsize=12, fontweight='bold', pad=10)
        ax2.set_ylabel('Number of Trades')
        
        # Add count labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # --- PANEL 3: P&L per Trade ---
        colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in df['pnl']]
        bars = ax3.bar(range(len(df)), df['pnl'], color=colors, alpha=0.7, edgecolor='black')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax3.set_title('💵 Profit/Loss Per Trade', 
                     fontsize=12, fontweight='bold', pad=10)
        ax3.set_xlabel('Trade Number')
        ax3.set_ylabel('P&L ($)')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add average P&L line
        avg_pnl = df['pnl'].mean()
        ax3.axhline(y=avg_pnl, color='blue', linestyle='--', 
                   alpha=0.7, label=f'Avg: ${avg_pnl:.2f}')
        ax3.legend()
        
        # --- PANEL 4: Trade Statistics Table ---
        ax4.axis('off')
        
        # Calculate statistics
        total_trades = len(df)
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0
        largest_win = df['pnl'].max()
        largest_loss = df['pnl'].min()
        avg_duration = df['duration_min'].mean()
        
        # Create statistics table
        stats_data = [
            ['📊 Total Trades', f'{total_trades}'],
            ['✅ Wins', f'{win_count} ({win_rate:.1f}%)'],
            ['❌ Losses', f'{loss_count} ({100-win_rate:.1f}%)'],
            ['', ''],
            ['💰 Total Return', f'${total_return:+.2f} ({total_return_pct:+.2f}%)'],
            ['📈 Avg Win', f'${avg_win:.2f}'],
            ['📉 Avg Loss', f'${avg_loss:.2f}'],
            ['🎯 Largest Win', f'${largest_win:.2f}'],
            ['💔 Largest Loss', f'${largest_loss:.2f}'],
            ['', ''],
            ['⏱️  Avg Duration', f'{avg_duration:.1f} min'],
            ['🏦 Starting Capital', f'${start_capital:.2f}'],
            ['💵 Ending Capital', f'${end_capital:.2f}']
        ]
        
        table = ax4.table(cellText=stats_data, 
                         colWidths=[0.5, 0.5],
                         cellLoc='left',
                         loc='center',
                         bbox=[0.1, 0.1, 0.8, 0.8])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(stats_data)):
            cell = table[(i, 0)]
            cell.set_facecolor('#f0f0f0')
            cell.set_text_props(weight='bold')
            
            if stats_data[i][0] == '':  # Separator rows
                cell.set_facecolor('white')
                table[(i, 1)].set_facecolor('white')
        
        ax4.set_title('📋 Performance Statistics', 
                     fontsize=12, fontweight='bold', pad=10)
        
        # Save the dashboard
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.output_dir}/performance_dashboard_{timestamp}.png'
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Dashboard saved: {filename}")
        
        return filename
    
    def create_quick_summary(self, trade_history):
        """Create a simple single-panel summary chart"""
        if not trade_history:
            return None
            
        df = pd.DataFrame(trade_history)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot equity curve
        ax.plot(range(len(df)), df['capital'], 
               linewidth=3, color='#3498db', marker='o', markersize=8)
        ax.fill_between(range(len(df)), df['capital'], 
                       alpha=0.2, color='#3498db')
        
        start_capital = df['capital'].iloc[0] - df['pnl'].iloc[0]
        end_capital = df['capital'].iloc[-1]
        total_return = end_capital - start_capital
        total_return_pct = (total_return / start_capital) * 100
        
        title_color = '#2ecc71' if total_return >= 0 else '#e74c3c'
        ax.set_title(f'💰 Trading Performance: ${start_capital:.2f} → ${end_capital:.2f} ({total_return_pct:+.2f}%)', 
                    fontsize=14, fontweight='bold', color=title_color, pad=15)
        ax.set_xlabel('Trade Number', fontsize=12)
        ax.set_ylabel('Capital ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.output_dir}/quick_summary_{timestamp}.png'
        plt.tight_layout()
        plt.savefig(filename, dpi=200, bbox_inches='tight')
        print(f"✅ Summary saved: {filename}")
        
        return filename

