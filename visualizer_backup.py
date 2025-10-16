"""
Performance Visualizer for Forex Trading Bot
Creates beautiful charts showing backtest results
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
from logger_config import setup_logger

logger = setup_logger('Visualizer')


class PerformanceVisualizer:
    """
    Create visual charts of trading performance
    
    Usage:
        viz = PerformanceVisualizer(backtest_engine)
        viz.plot_equity_curve()
        viz.plot_trades()
        viz.create_performance_dashboard()
    """
    
    def __init__(self, backtest_engine):
        """
        Initialize visualizer with backtest results
        
        Args:
            backtest_engine: BacktestEngine instance with completed backtest
        """
        self.engine = backtest_engine
        self.trades = backtest_engine.trades
        self.equity_curve = backtest_engine.equity_curve
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        logger.info("PerformanceVisualizer initialized")
    
    def plot_equity_curve(self, save_path='charts/equity_curve.png'):
        """
        Plot equity curve showing capital growth over time
        
        Args:
            save_path (str): Where to save the chart
        """
        logger.info("Creating equity curve chart...")
        
        if not self.equity_curve:
            logger.warning("No equity data to plot!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.equity_curve)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot equity curve
        ax.plot(df['date'], df['equity'], linewidth=2, color='#2E86AB', label='Portfolio Value')
        
        # Add starting capital line
        ax.axhline(y=self.engine.capital - sum(t['profit'] for t in self.trades), 
                   color='gray', linestyle='--', alpha=0.5, label='Starting Capital')
        
        # Mark trades
        for trade in self.trades:
            entry_date = trade['entry_date']
            exit_date = trade['exit_date']
            
            # Find equity at these dates
            entry_equity = df[df['date'] == entry_date]['equity'].iloc[0] if len(df[df['date'] == entry_date]) > 0 else None
            exit_equity = df[df['date'] == exit_date]['equity'].iloc[0] if len(df[df['date'] == exit_date]) > 0 else None
            
            if entry_equity is not None:
                color = 'green' if trade['profit'] > 0 else 'red'
                ax.scatter(entry_date, entry_equity, color=color, s=100, zorder=5, alpha=0.7)
            
            if exit_equity is not None:
                ax.scatter(exit_date, exit_equity, color=color, s=100, marker='x', zorder=5, alpha=0.7)
        
        # Format
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Portfolio Value ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Equity Curve - {self.engine.symbol}', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.xticks(rotation=45)
        
        # Add annotations
        final_equity = df['equity'].iloc[-1]
        starting_equity = df['equity'].iloc[0]
        total_return = ((final_equity - starting_equity) / starting_equity) * 100
        
        textstr = f'Starting: ${starting_equity:,.2f}\nFinal: ${final_equity:,.2f}\nReturn: {total_return:.2f}%'
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        import os
        os.makedirs('charts', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Equity curve saved to {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_trades(self, save_path='charts/trades.png'):
        """
        Plot individual trades showing profit/loss
        
        Args:
            save_path (str): Where to save the chart
        """
        logger.info("Creating trades chart...")
        
        if not self.trades:
            logger.warning("No trades to plot!")
            return
        
        # Extract trade data
        trade_nums = list(range(1, len(self.trades) + 1))
        profits = [t['profit'] for t in self.trades]
        colors = ['green' if p > 0 else 'red' for p in profits]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Bar chart
        bars = ax.bar(trade_nums, profits, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar, profit in zip(bars, profits):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${profit:.2f}',
                   ha='center', va='bottom' if profit > 0 else 'top',
                   fontsize=9, fontweight='bold')
        
        # Format
        ax.set_xlabel('Trade Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Profit/Loss ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Individual Trade Results - {self.engine.symbol}', fontsize=14, fontweight='bold', pad=20)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Stats box
        winning = len([p for p in profits if p > 0])
        losing = len([p for p in profits if p <= 0])
        win_rate = (winning / len(profits)) * 100 if profits else 0
        
        textstr = f'Total Trades: {len(profits)}\nWinners: {winning}\nLosers: {losing}\nWin Rate: {win_rate:.1f}%'
        ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        import os
        os.makedirs('charts', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Trades chart saved to {save_path}")
        
        plt.show()
        plt.close()
    
    def plot_trade_duration(self, save_path='charts/trade_duration.png'):
        """
        Plot how long each trade was held
        
        Args:
            save_path (str): Where to save the chart
        """
        logger.info("Creating trade duration chart...")
        
        if not self.trades:
            logger.warning("No trades to plot!")
            return
        
        # Calculate durations
        durations = []
        for trade in self.trades:
            duration = (trade['exit_date'] - trade['entry_date']).days
            durations.append(duration)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        trade_nums = list(range(1, len(durations) + 1))
        colors = ['green' if self.trades[i]['profit'] > 0 else 'red' for i in range(len(self.trades))]
        
        bars = ax.bar(trade_nums, durations, color=colors, alpha=0.7, edgecolor='black')
        
        # Add labels
        for bar, dur in zip(bars, durations):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{dur}d',
                   ha='center', va='bottom',
                   fontsize=9, fontweight='bold')
        
        # Format
        ax.set_xlabel('Trade Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Days Held', fontsize=12, fontweight='bold')
        ax.set_title(f'Trade Duration - {self.engine.symbol}', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Stats
        avg_duration = np.mean(durations)
        textstr = f'Avg Duration: {avg_duration:.1f} days\nMin: {min(durations)} days\nMax: {max(durations)} days'
        ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
        
        plt.tight_layout()
        
        # Save
        import os
        os.makedirs('charts', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Trade duration chart saved to {save_path}")
        
        plt.show()
        plt.close()
    
    def create_performance_dashboard(self, save_path='charts/dashboard.png'):
        """
        Create a comprehensive 4-panel dashboard
        
        Args:
            save_path (str): Where to save the chart
        """
        logger.info("Creating performance dashboard...")
        
        if not self.trades or not self.equity_curve:
            logger.warning("Insufficient data for dashboard!")
            return
        
        # Create 2x2 subplot grid
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Equity Curve (top left)
        ax1 = plt.subplot(2, 2, 1)
        df = pd.DataFrame(self.equity_curve)
        ax1.plot(df['date'], df['equity'], linewidth=2, color='#2E86AB')
        ax1.set_title('Equity Curve', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        
        # 2. Trade Results (top right)
        ax2 = plt.subplot(2, 2, 2)
        trade_nums = list(range(1, len(self.trades) + 1))
        profits = [t['profit'] for t in self.trades]
        colors = ['green' if p > 0 else 'red' for p in profits]
        ax2.bar(trade_nums, profits, color=colors, alpha=0.7)
        ax2.set_title('Trade Results', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Profit/Loss ($)')
        ax2.set_xlabel('Trade Number')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Trade Duration (bottom left)
        ax3 = plt.subplot(2, 2, 3)
        durations = [(t['exit_date'] - t['entry_date']).days for t in self.trades]
        ax3.bar(trade_nums, durations, color=colors, alpha=0.7)
        ax3.set_title('Trade Duration', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Days Held')
        ax3.set_xlabel('Trade Number')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Performance Stats (bottom right)
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        # Calculate stats
        results = self.engine.calculate_results()
        
        stats_text = f"""
PERFORMANCE SUMMARY

Symbol: {self.engine.symbol}
Period: {self.engine.start_date.date()} to {self.engine.end_date.date()}

RETURNS:
  Starting Capital: ${results['starting_capital']:,.2f}
  Final Capital: ${results['final_capital']:,.2f}
  Total Profit: ${results['total_profit']:,.2f}
  Total Return: {results['total_return']:.2f}%

TRADES:
  Total Trades: {results['total_trades']}
  Winning Trades: {results['winning_trades']}
  Losing Trades: {results['losing_trades']}
  Win Rate: {results['win_rate']:.1f}%

TRADE METRICS:
  Avg Profit/Trade: ${results['avg_profit_per_trade']:.2f}
  Best Trade: ${results['best_trade']:.2f}
  Worst Trade: ${results['worst_trade']:.2f}
  Avg Duration: {np.mean(durations):.1f} days
"""
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        # Main title
        fig.suptitle(f'Trading Performance Dashboard - {self.engine.symbol}',
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        # Save
        import os
        os.makedirs('charts', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ Dashboard saved to {save_path}")
        
        plt.show()
        plt.close()
    
    def create_all_charts(self):
        """Create all visualization charts at once"""
        logger.info("Creating all visualization charts...")
        
        self.plot_equity_curve()
        self.plot_trades()
        self.plot_trade_duration()
        self.create_performance_dashboard()
        
        logger.info("✅ All charts created successfully!")
        logger.info("   Check the 'charts/' directory for your visualizations")


def main():
    """Test visualizer with backtest results"""
    print("\n" + "="*70)
    print("📊 PERFORMANCE VISUALIZER - TEST")
    print("="*70 + "\n")
    
    print("To use this visualizer:")
    print("1. Run a backtest first: python backtest.py")
    print("2. Then use the visualizer in your code:")
    print()
    print("   from backtest import BacktestEngine")
    print("   from visualizer import PerformanceVisualizer")
    print()
    print("   engine = BacktestEngine('EUR/USD', '2024-04-01', '2024-10-01')")
    print("   engine.run_backtest()")
    print()
    print("   viz = PerformanceVisualizer(engine)")
    print("   viz.create_all_charts()")
    print()
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
