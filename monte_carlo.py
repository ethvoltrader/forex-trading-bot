import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class MonteCarloAnalyzer:
    """
    Monte Carlo Simulation with Percentage-Based Returns
    Tests different trade sequences with realistic compounding
    """
    
    def __init__(self, initial_capital=1000):
        self.initial_capital = initial_capital
        
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        if down == 0:
            return 100
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def run_backtest_for_trades(self, df, rsi_buy=25, rsi_sell=75):
        """
        Run backtest to generate trade P&Ls AND percentage returns
        """
        capital = self.initial_capital
        position = None
        entry_price = 0
        trades = []
        trade_returns_pct = []  # NEW: Track percentage returns
        
        for i in range(14, len(df)):
            current_price = df.iloc[i]['close']
            prices = df.iloc[i-14:i]['close'].values
            rsi = self.calculate_rsi(prices)
            
            # Exit logic
            if position == 'LONG':
                pnl_pct = (current_price - entry_price) / entry_price
                
                # Stop loss 3%
                if pnl_pct <= -0.03:
                    trade_return_pct = pnl_pct  # Percentage return
                    trade_pnl = trade_return_pct * capital
                    capital += trade_pnl
                    trades.append(trade_pnl)
                    trade_returns_pct.append(trade_return_pct)
                    position = None
                
                # Profit target 10%
                elif pnl_pct >= 0.10:
                    trade_return_pct = pnl_pct
                    trade_pnl = trade_return_pct * capital
                    capital += trade_pnl
                    trades.append(trade_pnl)
                    trade_returns_pct.append(trade_return_pct)
                    position = None
                
                # RSI exit
                elif rsi > rsi_sell:
                    trade_return_pct = pnl_pct
                    trade_pnl = trade_return_pct * capital
                    capital += trade_pnl
                    trades.append(trade_pnl)
                    trade_returns_pct.append(trade_return_pct)
                    position = None
            
            # Entry logic
            if position is None and rsi < rsi_buy:
                position = 'LONG'
                entry_price = current_price
        
        # Close final position
        if position == 'LONG':
            final_price = df.iloc[-1]['close']
            pnl_pct = (final_price - entry_price) / entry_price
            trade_pnl = pnl_pct * capital
            trades.append(trade_pnl)
            trade_returns_pct.append(pnl_pct)
        
        return np.array(trades), np.array(trade_returns_pct)
    
    def run_monte_carlo(self, trade_returns_pct, n_simulations=10000, ruin_threshold=0.5):
        """
        Run Monte Carlo simulation using PERCENTAGE returns
        Now order matters due to compounding!
        
        Parameters:
        -----------
        trade_returns_pct : array of trade percentage returns (e.g., 0.05 = 5%)
        n_simulations : number of simulations to run
        ruin_threshold : capital multiplier below which = ruin (0.5 = 50% of capital)
        """
        
        print("\n" + "="*70)
        print("🎲 MONTE CARLO SIMULATION (Percentage-Based with Compounding)")
        print("="*70)
        print(f"📊 Base Trades: {len(trade_returns_pct)}")
        print(f"🔄 Simulations: {n_simulations:,}")
        print(f"💰 Starting Capital: ${self.initial_capital:,.2f}")
        print(f"⚠️  Ruin Threshold: {ruin_threshold*100}% of capital")
        print(f"📈 Using compounding returns (order matters!)")
        print("="*70)
        
        final_capitals = []
        max_drawdowns = []
        ruin_count = 0
        
        ruin_capital = self.initial_capital * ruin_threshold
        
        print("\n🎲 Running simulations...")
        
        for sim in range(n_simulations):
            # Randomly shuffle trade returns
            shuffled_returns = np.random.permutation(trade_returns_pct)
            
            # Simulate equity curve with COMPOUNDING
            capital = self.initial_capital
            peak_capital = capital
            max_dd = 0
            
            ruined = False
            
            for return_pct in shuffled_returns:
                # Apply percentage return (this compounds!)
                capital = capital * (1 + return_pct)
                
                # Check for ruin
                if capital <= ruin_capital:
                    ruined = True
                    break
                
                # Track drawdown
                if capital > peak_capital:
                    peak_capital = capital
                
                current_dd = (peak_capital - capital) / peak_capital * 100
                if current_dd > max_dd:
                    max_dd = current_dd
            
            if ruined:
                ruin_count += 1
                final_capitals.append(capital)
                max_drawdowns.append(100)  # Total loss
            else:
                final_capitals.append(capital)
                max_drawdowns.append(max_dd)
            
            # Progress indicator
            if (sim + 1) % 2000 == 0:
                print(f"   Completed {sim + 1:,} / {n_simulations:,} simulations...")
        
        print(f"✅ Simulations complete!\n")
        
        return {
            'final_capitals': np.array(final_capitals),
            'max_drawdowns': np.array(max_drawdowns),
            'ruin_count': ruin_count,
            'n_simulations': n_simulations
        }
    
    def analyze_results(self, mc_results):
        """
        Analyze Monte Carlo results and print statistics
        """
        final_caps = mc_results['final_capitals']
        max_dds = mc_results['max_drawdowns']
        ruin_count = mc_results['ruin_count']
        n_sims = mc_results['n_simulations']
        
        # Calculate returns
        returns = ((final_caps - self.initial_capital) / self.initial_capital) * 100
        
        print("\n" + "="*70)
        print("📊 MONTE CARLO ANALYSIS RESULTS")
        print("="*70)
        
        # Return statistics
        print(f"\n💰 RETURN DISTRIBUTION:")
        print(f"   Mean Return:            {returns.mean():+.2f}%")
        print(f"   Median Return:          {np.median(returns):+.2f}%")
        print(f"   Std Deviation:          {returns.std():.2f}%")
        print(f"   Best Case:              {returns.max():+.2f}%")
        print(f"   Worst Case:             {returns.min():+.2f}%")
        
        # Confidence intervals
        ci_95_low, ci_95_high = np.percentile(returns, [2.5, 97.5])
        ci_68_low, ci_68_high = np.percentile(returns, [16, 84])
        
        print(f"\n📊 CONFIDENCE INTERVALS:")
        print(f"   95% Confidence:         {ci_95_low:+.2f}% to {ci_95_high:+.2f}%")
        print(f"   68% Confidence:         {ci_68_low:+.2f}% to {ci_68_high:+.2f}%")
        
        # Probability of profit
        prob_profit = (returns > 0).sum() / n_sims * 100
        prob_loss = (returns < 0).sum() / n_sims * 100
        
        print(f"\n🎯 PROBABILITY OF OUTCOMES:")
        print(f"   Probability of Profit:  {prob_profit:.1f}%")
        print(f"   Probability of Loss:    {prob_loss:.1f}%")
        
        # Drawdown statistics
        print(f"\n📉 DRAWDOWN ANALYSIS:")
        print(f"   Mean Max Drawdown:      {max_dds.mean():.2f}%")
        print(f"   Median Max Drawdown:    {np.median(max_dds):.2f}%")
        print(f"   Worst Drawdown:         {max_dds.max():.2f}%")
        print(f"   Best Drawdown:          {max_dds.min():.2f}%")
        
        # Risk of ruin
        risk_of_ruin = (ruin_count / n_sims) * 100
        
        print(f"\n⚠️  RISK OF RUIN:")
        print(f"   Ruin Events:            {ruin_count} / {n_sims:,}")
        print(f"   Risk of Ruin:           {risk_of_ruin:.2f}%")
        
        if risk_of_ruin == 0:
            print(f"   Status:                 EXCELLENT ✅ (No ruin in any simulation!)")
        elif risk_of_ruin < 1:
            print(f"   Status:                 VERY GOOD ✅ (Very low risk)")
        elif risk_of_ruin < 5:
            print(f"   Status:                 ACCEPTABLE ⚠️ (Manageable risk)")
        else:
            print(f"   Status:                 HIGH RISK ❌ (Dangerous!)")
        
        # Percentile analysis
        print(f"\n📊 PERCENTILE RETURNS:")
        for percentile in [10, 25, 50, 75, 90]:
            val = np.percentile(returns, percentile)
            print(f"   {percentile}th Percentile:        {val:+.2f}%")
        
        print("\n" + "="*70)
        
        return {
            'mean_return': returns.mean(),
            'median_return': np.median(returns),
            'std_return': returns.std(),
            'prob_profit': prob_profit,
            'risk_of_ruin': risk_of_ruin,
            'mean_max_dd': max_dds.mean(),
            'ci_95': (ci_95_low, ci_95_high)
        }
    
    def visualize_results(self, mc_results, save_path='monte_carlo_results.png'):
        """
        Create comprehensive Monte Carlo visualization
        """
        final_caps = mc_results['final_capitals']
        max_dds = mc_results['max_drawdowns']
        returns = ((final_caps - self.initial_capital) / self.initial_capital) * 100
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Chart 1: Return Distribution (Histogram)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(returns, bins=50, color='#118AB2', alpha=0.7, edgecolor='black')
        ax1.axvline(x=returns.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {returns.mean():.2f}%')
        ax1.axvline(x=np.median(returns), color='green', linestyle='--', 
                   linewidth=2, label=f'Median: {np.median(returns):.2f}%')
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax1.set_xlabel('Return (%)', fontweight='bold', fontsize=11)
        ax1.set_ylabel('Frequency', fontweight='bold', fontsize=11)
        ax1.set_title('Return Distribution (10,000 Simulations)', 
                     fontweight='bold', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Cumulative Probability
        ax2 = fig.add_subplot(gs[0, 1])
        sorted_returns = np.sort(returns)
        cumulative_prob = np.arange(1, len(sorted_returns) + 1) / len(sorted_returns) * 100
        ax2.plot(sorted_returns, cumulative_prob, linewidth=2, color='#2E86AB')
        ax2.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Return (%)', fontweight='bold', fontsize=11)
        ax2.set_ylabel('Cumulative Probability (%)', fontweight='bold', fontsize=11)
        ax2.set_title('Cumulative Distribution Function', fontweight='bold', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        # Chart 3: Drawdown Distribution
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.hist(max_dds, bins=50, color='#EF476F', alpha=0.7, edgecolor='black')
        ax3.axvline(x=max_dds.mean(), color='darkred', linestyle='--', 
                   linewidth=2, label=f'Mean: {max_dds.mean():.2f}%')
        ax3.set_xlabel('Max Drawdown (%)', fontweight='bold', fontsize=11)
        ax3.set_ylabel('Frequency', fontweight='bold', fontsize=11)
        ax3.set_title('Maximum Drawdown Distribution', fontweight='bold', fontsize=14)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Chart 4: Box Plot
        ax4 = fig.add_subplot(gs[1, 1])
        box_data = [returns]
        bp = ax4.boxplot(box_data, widths=0.6, patch_artist=True,
                        boxprops=dict(facecolor='#06D6A0', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5))
        ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax4.set_ylabel('Return (%)', fontweight='bold', fontsize=11)
        ax4.set_title('Return Distribution (Box Plot)', fontweight='bold', fontsize=14)
        ax4.set_xticklabels(['All Simulations'])
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Chart 5: Statistics Table
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        # Calculate statistics
        mean_ret = returns.mean()
        median_ret = np.median(returns)
        std_ret = returns.std()
        prob_profit = (returns > 0).sum() / len(returns) * 100
        ci_95_low, ci_95_high = np.percentile(returns, [2.5, 97.5])
        mean_dd = max_dds.mean()
        risk_ruin = (mc_results['ruin_count'] / mc_results['n_simulations']) * 100
        
        stats_text = f"""
        📊 MONTE CARLO STATISTICS SUMMARY
        
        💰 RETURNS:
           Mean Return:              {mean_ret:+.2f}%
           Median Return:            {median_ret:+.2f}%
           Standard Deviation:       {std_ret:.2f}%
           95% Confidence Interval:  {ci_95_low:+.2f}% to {ci_95_high:+.2f}%
        
        🎯 PROBABILITIES:
           Probability of Profit:    {prob_profit:.1f}%
           Probability of Loss:      {100-prob_profit:.1f}%
        
        📉 RISK METRICS:
           Mean Max Drawdown:        {mean_dd:.2f}%
           Risk of Ruin:             {risk_ruin:.2f}%
        
        🔢 SIMULATIONS:
           Total Simulations:        {mc_results['n_simulations']:,}
           Ruin Events:              {mc_results['ruin_count']}
        """
        
        ax5.text(0.1, 0.5, stats_text, 
                fontsize=12, verticalalignment='center',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Monte Carlo visualization saved: {save_path}")
        plt.close()

