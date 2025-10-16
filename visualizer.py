import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set style for beautiful charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class PerformanceVisualizer:
    """
    Creates portfolio-quality visualizations of trading performance
    """
    
    def __init__(self, results_df):
        """
        Initialize with backtest results DataFrame
        
        Parameters:
        -----------
        results_df : pd.DataFrame
            DataFrame with columns: timestamp, capital, trade_pnl, etc.
        """
        self.df = results_df
        self.starting_capital = results_df['capital'].iloc[0] if len(results_df) > 0 else 1000
        
    def create_equity_curve(self, save_path='equity_curve.png'):
        """
        Create beautiful equity curve showing capital growth over time
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # Top chart: Equity Curve
        ax1.plot(self.df.index, self.df['capital'], 
                linewidth=2.5, color='#2E86AB', label='Portfolio Value')
        
        # Add starting capital reference line
        ax1.axhline(y=self.starting_capital, color='gray', 
                   linestyle='--', alpha=0.5, label='Starting Capital')
        
        # Fill area under curve
        ax1.fill_between(self.df.index, self.starting_capital, self.df['capital'], 
                        alpha=0.3, color='#2E86AB')
        
        # Calculate key metrics
        final_capital = self.df['capital'].iloc[-1]
        total_return_pct = ((final_capital - self.starting_capital) / self.starting_capital) * 100
        max_drawdown = self.calculate_max_drawdown()
        
        # Title with key metrics
        title = f'Equity Curve\n'
        title += f'Return: {total_return_pct:+.2f}% | '
        title += f'Final: ${final_capital:,.2f} | '
        title += f'Max Drawdown: {max_drawdown:.2f}%'
        
        ax1.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('Portfolio Value ($)', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Bottom chart: Drawdown
        drawdown = self.calculate_drawdown_series()
        ax2.fill_between(drawdown.index, 0, drawdown, 
                        color='#A23B72', alpha=0.7, label='Drawdown %')
        ax2.set_ylabel('Drawdown (%)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Trade Number', fontsize=12, fontweight='bold')
        ax2.legend(loc='lower left', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Equity curve saved: {save_path}")
        plt.close()
        
        return save_path
    
    def create_trade_distribution(self, save_path='trade_distribution.png'):
        """
        Create charts showing win/loss distribution and trade sizes
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Filter to only rows with trades
        trades_df = self.df[self.df['trade_pnl'] != 0].copy()
        
        if len(trades_df) == 0:
            print("⚠️ No trades to visualize!")
            return None
        
        # Chart 1: Win/Loss Count
        wins = (trades_df['trade_pnl'] > 0).sum()
        losses = (trades_df['trade_pnl'] < 0).sum()
        
        colors = ['#06D6A0', '#EF476F']
        ax1.bar(['Wins', 'Losses'], [wins, losses], color=colors, alpha=0.8)
        ax1.set_title('Win/Loss Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Number of Trades', fontsize=11)
        
        # Add percentages on bars
        total_trades = wins + losses
        for i, (label, value) in enumerate(zip(['Wins', 'Losses'], [wins, losses])):
            pct = (value / total_trades) * 100 if total_trades > 0 else 0
            ax1.text(i, value, f'{value}\n({pct:.1f}%)', 
                    ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: P&L Distribution (Histogram)
        ax2.hist(trades_df['trade_pnl'], bins=20, color='#118AB2', 
                alpha=0.7, edgecolor='black')
        ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
        ax2.set_title('Profit/Loss Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('P&L per Trade ($)', fontsize=11)
        ax2.set_ylabel('Frequency', fontsize=11)
        
        # Chart 3: Cumulative P&L
        cumulative_pnl = trades_df['trade_pnl'].cumsum()
        ax3.plot(range(len(cumulative_pnl)), cumulative_pnl, 
                linewidth=2.5, color='#073B4C')
        ax3.fill_between(range(len(cumulative_pnl)), 0, cumulative_pnl, 
                        alpha=0.3, color='#073B4C')
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax3.set_title('Cumulative P&L', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Trade Number', fontsize=11)
        ax3.set_ylabel('Cumulative P&L ($)', fontsize=11)
        ax3.grid(True, alpha=0.3)
        
        # Chart 4: Trade Performance Over Time
        trade_returns = (trades_df['trade_pnl'] / self.starting_capital) * 100
        colors_scatter = ['#06D6A0' if x > 0 else '#EF476F' for x in trade_returns]
        ax4.scatter(range(len(trade_returns)), trade_returns, 
                   c=colors_scatter, alpha=0.6, s=50)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.set_title('Return per Trade (%)', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Trade Number', fontsize=11)
        ax4.set_ylabel('Return (%)', fontsize=11)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Trade distribution saved: {save_path}")
        plt.close()
        
        return save_path
    
    def create_performance_summary(self, save_path='performance_summary.png'):
        """
        Create a comprehensive performance summary dashboard
        """
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Calculate all metrics
        metrics = self.calculate_all_metrics()
        
        # Main equity curve (top, spanning both columns)
        ax_main = fig.add_subplot(gs[0, :])
        ax_main.plot(self.df.index, self.df['capital'], 
                    linewidth=3, color='#2E86AB')
        ax_main.fill_between(self.df.index, self.starting_capital, 
                            self.df['capital'], alpha=0.3, color='#2E86AB')
        ax_main.set_title('Portfolio Performance', fontsize=16, fontweight='bold')
        ax_main.set_ylabel('Capital ($)', fontsize=12)
        ax_main.grid(True, alpha=0.3)
        ax_main.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Metrics table (middle left)
        ax_metrics = fig.add_subplot(gs[1, 0])
        ax_metrics.axis('off')
        
        metrics_text = f"""
        📊 PERFORMANCE METRICS
        
        💰 Total Return: {metrics['total_return_pct']:+.2f}%
        💵 Final Capital: ${metrics['final_capital']:,.2f}
        
        🎯 Win Rate: {metrics['win_rate']:.1f}%
        📈 Total Trades: {metrics['total_trades']}
        ✅ Winning Trades: {metrics['winning_trades']}
        ❌ Losing Trades: {metrics['losing_trades']}
        
        💎 Avg Win: ${metrics['avg_win']:.2f}
        💔 Avg Loss: ${metrics['avg_loss']:.2f}
        ⚖️  Profit Factor: {metrics['profit_factor']:.2f}
        
        📉 Max Drawdown: {metrics['max_drawdown']:.2f}%
        🏔️ Peak Capital: ${metrics['peak_capital']:,.2f}
        """
        
        ax_metrics.text(0.1, 0.5, metrics_text, 
                       fontsize=11, verticalalignment='center',
                       fontfamily='monospace',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        # Win/Loss pie chart (middle right)
        ax_pie = fig.add_subplot(gs[1, 1])
        if metrics['total_trades'] > 0:
            sizes = [metrics['winning_trades'], metrics['losing_trades']]
            colors = ['#06D6A0', '#EF476F']
            explode = (0.05, 0.05)
            ax_pie.pie(sizes, explode=explode, labels=['Wins', 'Losses'], 
                      colors=colors, autopct='%1.1f%%',
                      shadow=True, startangle=90, textprops={'fontsize': 12})
            ax_pie.set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')
        
        # Trade returns scatter (bottom, spanning both columns)
        ax_scatter = fig.add_subplot(gs[2, :])
        trades_df = self.df[self.df['trade_pnl'] != 0]
        if len(trades_df) > 0:
            trade_returns = (trades_df['trade_pnl'] / self.starting_capital) * 100
            colors_scatter = ['#06D6A0' if x > 0 else '#EF476F' for x in trade_returns]
            ax_scatter.scatter(range(len(trade_returns)), trade_returns, 
                             c=colors_scatter, alpha=0.6, s=50)
            ax_scatter.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
            ax_scatter.set_title('Return per Trade', fontsize=14, fontweight='bold')
            ax_scatter.set_xlabel('Trade Number', fontsize=11)
            ax_scatter.set_ylabel('Return (%)', fontsize=11)
            ax_scatter.grid(True, alpha=0.3)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Performance summary saved: {save_path}")
        plt.close()
        
        return save_path
    
    def calculate_all_metrics(self):
        """Calculate all performance metrics"""
        trades_df = self.df[self.df['trade_pnl'] != 0].copy()
        
        final_capital = self.df['capital'].iloc[-1] if len(self.df) > 0 else self.starting_capital
        total_return_pct = ((final_capital - self.starting_capital) / self.starting_capital) * 100
        
        total_trades = len(trades_df)
        winning_trades = (trades_df['trade_pnl'] > 0).sum()
        losing_trades = (trades_df['trade_pnl'] < 0).sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        wins = trades_df[trades_df['trade_pnl'] > 0]['trade_pnl']
        losses = trades_df[trades_df['trade_pnl'] < 0]['trade_pnl']
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        
        total_wins = wins.sum() if len(wins) > 0 else 0
        total_losses = abs(losses.sum()) if len(losses) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return {
            'total_return_pct': total_return_pct,
            'final_capital': final_capital,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': self.calculate_max_drawdown(),
            'peak_capital': self.df['capital'].max()
        }
    
    def calculate_max_drawdown(self):
        """Calculate maximum drawdown percentage"""
        peak = self.df['capital'].expanding(min_periods=1).max()
        drawdown = (self.df['capital'] - peak) / peak * 100
        return abs(drawdown.min())
    
    def calculate_drawdown_series(self):
        """Calculate drawdown series for plotting"""
        peak = self.df['capital'].expanding(min_periods=1).max()
        drawdown = (self.df['capital'] - peak) / peak * 100
        return drawdown
    
    def generate_all_charts(self):
        """Generate all visualization charts"""
        print("\n🎨 Generating performance visualizations...")
        print("=" * 50)
        
        charts = []
        
        # Generate each chart
        chart1 = self.create_equity_curve()
        charts.append(chart1)
        
        chart2 = self.create_trade_distribution()
        if chart2:
            charts.append(chart2)
        
        chart3 = self.create_performance_summary()
        charts.append(chart3)
        
        print("=" * 50)
        print(f"✅ Generated {len(charts)} charts successfully!")
        print("\n📊 Your charts are ready! 💼")
        
        return charts

