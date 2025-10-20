"""
Analysis script for trading results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

def analyze_trading_results(excel_file="trading_log.xlsx"):
    """Analyze trading results from Excel file"""
    
    if not os.path.exists(excel_file):
        print(f"Excel file {excel_file} not found. Run the simulator first.")
        return
    
    try:
        # Read trading data
        df = pd.read_excel(excel_file, sheet_name="Trading Log")
        
        if df.empty:
            print("No trading data found.")
            return
        
        print("Day Trading Simulator - Results Analysis")
        print("=" * 50)
        print()
        
        # Basic statistics
        total_trades = len(df)
        winning_trades = len(df[df['Win/Loss'] == 'Win'])
        losing_trades = len(df[df['Win/Loss'] == 'Loss'])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit = df[df['Gross P/L ($)'] > 0]['Gross P/L ($)'].sum()
        total_loss = abs(df[df['Gross P/L ($)'] < 0]['Gross P/L ($)'].sum())
        net_profit = total_profit - total_loss
        
        avg_win = total_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = total_loss / losing_trades if losing_trades > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        print("Overall Performance:")
        print(f"  Total Trades: {total_trades}")
        print(f"  Winning Trades: {winning_trades}")
        print(f"  Losing Trades: {losing_trades}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Total Profit: ${total_profit:,.2f}")
        print(f"  Total Loss: ${total_loss:,.2f}")
        print(f"  Net Profit: ${net_profit:,.2f}")
        print(f"  Average Win: ${avg_win:,.2f}")
        print(f"  Average Loss: ${avg_loss:,.2f}")
        print(f"  Profit Factor: {profit_factor:.2f}")
        print()
        
        # Strategy performance
        print("Strategy Performance:")
        strategy_stats = df.groupby('Strategy').agg({
            'Win/Loss': lambda x: (x == 'Win').sum(),
            'Gross P/L ($)': ['count', 'sum', 'mean']
        }).round(2)
        
        strategy_stats.columns = ['Wins', 'Total_Trades', 'Total_PL', 'Avg_PL']
        strategy_stats['Win_Rate'] = (strategy_stats['Wins'] / strategy_stats['Total_Trades'] * 100).round(1)
        strategy_stats['Profit_Factor'] = (strategy_stats['Total_PL'] / 
                                         strategy_stats['Total_PL'].where(strategy_stats['Total_PL'] < 0).abs()).round(2)
        
        print(strategy_stats)
        print()
        
        # Daily performance
        df['Date'] = pd.to_datetime(df['Date'])
        daily_perf = df.groupby('Date').agg({
            'Gross P/L ($)': 'sum',
            'Win/Loss': lambda x: (x == 'Win').sum(),
            'Order ID': 'count'
        }).round(2)
        
        daily_perf.columns = ['Daily_PL', 'Wins', 'Total_Trades']
        daily_perf['Daily_Win_Rate'] = (daily_perf['Wins'] / daily_perf['Total_Trades'] * 100).round(1)
        
        print("Recent Daily Performance (Last 10 days):")
        print(daily_perf.tail(10))
        print()
        
        # Risk metrics
        print("Risk Metrics:")
        max_drawdown = df['Cumulative P/L'].min()
        avg_risk = df['$ Risked (per trade)'].mean()
        max_risk = df['$ Risked (per trade)'].max()
        
        print(f"  Maximum Drawdown: ${max_drawdown:,.2f}")
        print(f"  Average Risk per Trade: ${avg_risk:,.2f}")
        print(f"  Maximum Risk per Trade: ${max_risk:,.2f}")
        print()
        
        # Best and worst trades
        print("Best Trades:")
        best_trades = df.nlargest(3, 'Gross P/L ($)')[['Ticker', 'Strategy', 'Gross P/L ($)', 'Date']]
        print(best_trades)
        print()
        
        print("Worst Trades:")
        worst_trades = df.nsmallest(3, 'Gross P/L ($)')[['Ticker', 'Strategy', 'Gross P/L ($)', 'Date']]
        print(worst_trades)
        print()
        
        # Generate charts
        create_performance_charts(df)
        
    except Exception as e:
        print(f"Error analyzing results: {e}")

def create_performance_charts(df):
    """Create performance visualization charts"""
    try:
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Day Trading Simulator - Performance Analysis', fontsize=16)
        
        # 1. Cumulative P&L
        df['Cumulative P/L'] = df['Cumulative P/L'].fillna(0)
        axes[0, 0].plot(df.index, df['Cumulative P/L'], linewidth=2, color='blue')
        axes[0, 0].set_title('Cumulative P&L Over Time')
        axes[0, 0].set_xlabel('Trade Number')
        axes[0, 0].set_ylabel('Cumulative P&L ($)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Strategy Performance
        strategy_pnl = df.groupby('Strategy')['Gross P/L ($)'].sum().sort_values(ascending=True)
        axes[0, 1].barh(strategy_pnl.index, strategy_pnl.values)
        axes[0, 1].set_title('Total P&L by Strategy')
        axes[0, 1].set_xlabel('Total P&L ($)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Win Rate by Strategy
        win_rates = df.groupby('Strategy').apply(
            lambda x: (x['Win/Loss'] == 'Win').sum() / len(x) * 100
        ).sort_values(ascending=True)
        axes[1, 0].barh(win_rates.index, win_rates.values, color='green', alpha=0.7)
        axes[1, 0].set_title('Win Rate by Strategy (%)')
        axes[1, 0].set_xlabel('Win Rate (%)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Trade Duration Distribution
        axes[1, 1].hist(df['Trade Duration (min)'].dropna(), bins=20, alpha=0.7, color='orange')
        axes[1, 1].set_title('Trade Duration Distribution')
        axes[1, 1].set_xlabel('Duration (minutes)')
        axes[1, 1].set_ylabel('Number of Trades')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('trading_performance_analysis.png', dpi=300, bbox_inches='tight')
        print("Performance charts saved as 'trading_performance_analysis.png'")
        
    except Exception as e:
        print(f"Error creating charts: {e}")

def main():
    """Main function"""
    analyze_trading_results()

if __name__ == "__main__":
    main()
