import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class WalkForwardAnalyzer:
    """
    Walk-Forward Analysis: Train on past data, test on future data
    This validates your strategy works on UNSEEN data (like real trading)
    """
    
    def __init__(self, initial_capital=1000):
        self.initial_capital = initial_capital
        self.results = []
        
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
    
    def backtest_strategy(self, df, rsi_buy=30, rsi_sell=70, 
                         stop_loss=0.03, profit_target=0.10):
        """
        Run backtest on a dataset with given parameters
        Returns: final capital, return %, win rate, profit factor
        """
        capital = self.initial_capital
        position = None
        entry_price = 0
        trades = []
        
        for i in range(14, len(df)):
            current_price = df.iloc[i]['close']
            prices = df.iloc[i-14:i]['close'].values
            rsi = self.calculate_rsi(prices)
            
            trade_pnl = 0
            
            # Exit logic
            if position == 'LONG':
                pnl_pct = (current_price - entry_price) / entry_price
                
                if pnl_pct <= -stop_loss:
                    trade_pnl = (current_price - entry_price) * (capital / entry_price)
                    capital += trade_pnl
                    trades.append(trade_pnl)
                    position = None
                
                elif pnl_pct >= profit_target:
                    trade_pnl = (current_price - entry_price) * (capital / entry_price)
                    capital += trade_pnl
                    trades.append(trade_pnl)
                    position = None
                
                elif rsi > rsi_sell:
                    trade_pnl = (current_price - entry_price) * (capital / entry_price)
                    capital += trade_pnl
                    trades.append(trade_pnl)
                    position = None
            
            # Entry logic
            if position is None and rsi < rsi_buy:
                position = 'LONG'
                entry_price = current_price
        
        # Close final position if any
        if position == 'LONG':
            final_price = df.iloc[-1]['close']
            trade_pnl = (final_price - entry_price) * (capital / entry_price)
            capital += trade_pnl
            trades.append(trade_pnl)
        
        # Calculate metrics
        total_return_pct = ((capital - self.initial_capital) / self.initial_capital) * 100
        
        if len(trades) > 0:
            wins = [t for t in trades if t > 0]
            losses = [t for t in trades if t < 0]
            win_rate = (len(wins) / len(trades)) * 100
            
            total_wins = sum(wins) if wins else 0
            total_losses = abs(sum(losses)) if losses else 0
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
        else:
            win_rate = 0
            profit_factor = 0
        
        return {
            'final_capital': capital,
            'return_pct': total_return_pct,
            'total_trades': len(trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor
        }
    
    def optimize_parameters(self, df, rsi_range, verbose=False):
        """
        Find best RSI parameters for a training dataset
        Tests multiple RSI combinations
        """
        best_return = -999999
        best_params = None
        best_result = None
        
        if verbose:
            print(f"  🔍 Testing {len(rsi_range)} RSI configurations...")
        
        for rsi_buy in rsi_range:
            for rsi_sell in rsi_range:
                if rsi_buy >= rsi_sell:
                    continue
                    
                result = self.backtest_strategy(df, rsi_buy=rsi_buy, rsi_sell=rsi_sell)
                
                if result['return_pct'] > best_return:
                    best_return = result['return_pct']
                    best_params = (rsi_buy, rsi_sell)
                    best_result = result
        
        if verbose and best_params:
            print(f"  ✅ Best: RSI {best_params[0]}/{best_params[1]} → {best_return:+.2f}%")
        
        return best_params, best_result
    
    def run_walk_forward(self, df, train_size=0.7, test_size=0.3, 
                        n_windows=5, rsi_range=[25, 30, 35, 40, 70, 75, 80]):
        """
        Walk-Forward Analysis Main Function
        
        Parameters:
        -----------
        df : DataFrame with price data
        train_size : float, portion of data for training (0.7 = 70%)
        test_size : float, portion of data for testing (0.3 = 30%)
        n_windows : int, number of walk-forward windows
        rsi_range : list, RSI values to test
        """
        
        print("\n" + "="*70)
        print("🚀 WALK-FORWARD ANALYSIS")
        print("="*70)
        print(f"📊 Total Data Points: {len(df)}")
        print(f"🎯 Strategy: RSI-based with Stop Loss & Profit Target")
        print(f"🔄 Windows: {n_windows}")
        print(f"📈 Train/Test Split: {int(train_size*100)}% / {int(test_size*100)}%")
        print("="*70 + "\n")
        
        # Calculate window size
        total_points = len(df)
        window_size = total_points // n_windows
        
        results = []
        
        for window in range(n_windows):
            start_idx = window * window_size
            
            # Skip if not enough data
            if start_idx + window_size > total_points:
                break
                
            end_idx = start_idx + window_size
            
            # Split into train and test
            split_point = int(window_size * train_size)
            train_end = start_idx + split_point
            
            train_df = df.iloc[start_idx:train_end].reset_index(drop=True)
            test_df = df.iloc[train_end:end_idx].reset_index(drop=True)
            
            print(f"📊 WINDOW {window + 1}/{n_windows}")
            print(f"   Train: {len(train_df)} bars | Test: {len(test_df)} bars")
            
            # Optimize on training data
            print(f"   🎓 Training phase...")
            best_params, train_result = self.optimize_parameters(
                train_df, rsi_range, verbose=True
            )
            
            if best_params is None:
                print(f"   ⚠️  No profitable parameters found in training")
                continue
            
            # Test on unseen data
            print(f"   🧪 Testing on unseen data...")
            test_result = self.backtest_strategy(
                test_df, 
                rsi_buy=best_params[0], 
                rsi_sell=best_params[1]
            )
            
            print(f"   📈 Test Results: {test_result['return_pct']:+.2f}% | "
                  f"Win Rate: {test_result['win_rate']:.1f}% | "
                  f"Trades: {test_result['total_trades']}")
            
            results.append({
                'window': window + 1,
                'train_return': train_result['return_pct'],
                'test_return': test_result['return_pct'],
                'rsi_buy': best_params[0],
                'rsi_sell': best_params[1],
                'test_trades': test_result['total_trades'],
                'test_win_rate': test_result['win_rate'],
                'test_profit_factor': test_result['profit_factor']
            })
            
            print()
        
        return pd.DataFrame(results)
    
    def analyze_results(self, results_df):
        """
        Analyze walk-forward results and print summary
        """
        print("\n" + "="*70)
        print("📊 WALK-FORWARD ANALYSIS SUMMARY")
        print("="*70)
        
        # Overall statistics
        avg_test_return = results_df['test_return'].mean()
        avg_train_return = results_df['train_return'].mean()
        std_test_return = results_df['test_return'].std()
        
        wins = (results_df['test_return'] > 0).sum()
        losses = (results_df['test_return'] <= 0).sum()
        win_rate = (wins / len(results_df)) * 100
        
        print(f"\n🎯 PERFORMANCE METRICS:")
        print(f"   Training Avg Return:    {avg_train_return:+.2f}%")
        print(f"   Testing Avg Return:     {avg_test_return:+.2f}%")
        print(f"   Testing Std Dev:        {std_test_return:.2f}%")
        print(f"   Profitable Windows:     {wins}/{len(results_df)} ({win_rate:.1f}%)")
        
        print(f"\n📈 RETURN RANGE:")
        print(f"   Best Window:            {results_df['test_return'].max():+.2f}%")
        print(f"   Worst Window:           {results_df['test_return'].min():+.2f}%")
        
        print(f"\n🎲 OPTIMAL PARAMETERS (Most Common):")
        most_common_buy = results_df['rsi_buy'].mode()[0]
        most_common_sell = results_df['rsi_sell'].mode()[0]
        print(f"   RSI Buy:                {most_common_buy}")
        print(f"   RSI Sell:               {most_common_sell}")
        
        print(f"\n⚖️  CONSISTENCY CHECK:")
        consistency = (results_df['test_return'] > 0).sum() / len(results_df)
        if consistency >= 0.7:
            grade = "EXCELLENT ✅"
        elif consistency >= 0.5:
            grade = "GOOD 👍"
        elif consistency >= 0.3:
            grade = "FAIR ⚠️"
        else:
            grade = "POOR ❌"
        print(f"   Strategy Consistency:   {consistency*100:.1f}% - {grade}")
        
        # Degradation check
        degradation = avg_train_return - avg_test_return
        print(f"\n🔍 OVERFITTING CHECK:")
        print(f"   Performance Degradation: {degradation:.2f}%")
        if degradation < 5:
            print(f"   Status: ROBUST ✅ (Low overfitting)")
        elif degradation < 15:
            print(f"   Status: ACCEPTABLE ⚠️ (Some overfitting)")
        else:
            print(f"   Status: CONCERNING ❌ (High overfitting)")
        
        print("\n" + "="*70)
        
        return {
            'avg_test_return': avg_test_return,
            'consistency': consistency,
            'degradation': degradation
        }
    
    def visualize_results(self, results_df, save_path='walk_forward_results.png'):
        """
        Create visualization of walk-forward results
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Chart 1: Train vs Test Returns
        x = results_df['window']
        ax1.plot(x, results_df['train_return'], 'o-', label='Training', 
                linewidth=2, markersize=8, color='#2E86AB')
        ax1.plot(x, results_df['test_return'], 's-', label='Testing (Unseen)', 
                linewidth=2, markersize=8, color='#A23B72')
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Window', fontweight='bold')
        ax1.set_ylabel('Return (%)', fontweight='bold')
        ax1.set_title('Training vs Testing Returns', fontweight='bold', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Chart 2: Test Return Distribution
        ax2.bar(x, results_df['test_return'], color='#118AB2', alpha=0.7, edgecolor='black')
        ax2.axhline(y=0, color='red', linestyle='-', linewidth=2)
        ax2.set_xlabel('Window', fontweight='bold')
        ax2.set_ylabel('Return (%)', fontweight='bold')
        ax2.set_title('Test Returns by Window', fontweight='bold', fontsize=14)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Chart 3: Win Rate by Window
        ax3.bar(x, results_df['test_win_rate'], color='#06D6A0', alpha=0.7, edgecolor='black')
        ax3.axhline(y=50, color='orange', linestyle='--', label='50% Breakeven')
        ax3.set_xlabel('Window', fontweight='bold')
        ax3.set_ylabel('Win Rate (%)', fontweight='bold')
        ax3.set_title('Win Rate by Window', fontweight='bold', fontsize=14)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Chart 4: Parameter Stability
        ax4_twin = ax4.twinx()
        ax4.plot(x, results_df['rsi_buy'], 'o-', label='RSI Buy', 
                linewidth=2, markersize=8, color='#06D6A0')
        ax4_twin.plot(x, results_df['rsi_sell'], 's-', label='RSI Sell', 
                     linewidth=2, markersize=8, color='#EF476F')
        ax4.set_xlabel('Window', fontweight='bold')
        ax4.set_ylabel('RSI Buy Threshold', fontweight='bold')
        ax4_twin.set_ylabel('RSI Sell Threshold', fontweight='bold')
        ax4.set_title('Optimal Parameters by Window', fontweight='bold', fontsize=14)
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Walk-forward visualization saved: {save_path}")
        plt.close()
