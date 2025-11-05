#!/usr/bin/env python3
"""
Create comparison charts for balanced vs unbalanced modes
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def main():
    # Set up output directory
    output_dir = Path("reports/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    equity_unbal = Path("data/clean/equity_curve.csv")
    equity_bal = Path("data/clean/equity_curve_balanced.csv")
    sector_unbal = Path("data/clean/sector_stats.csv")
    sector_bal = Path("data/clean/sector_stats_balanced.csv")
    
    # ========== Plot 1: Cumulative Returns Comparison ==========
    if equity_unbal.exists() and equity_bal.exists():
        eq_unbal = pd.read_csv(equity_unbal)
        eq_bal = pd.read_csv(equity_bal)
        
        if not eq_unbal.empty and not eq_bal.empty:
            eq_unbal['date'] = pd.to_datetime(eq_unbal['date'])
            eq_bal['date'] = pd.to_datetime(eq_bal['date'])
            
            # Calculate cumulative returns
            y_unbal = eq_unbal['equity'] - 1 if 'equity' in eq_unbal.columns else eq_unbal['cum_ret']
            y_bal = eq_bal['equity'] - 1 if 'equity' in eq_bal.columns else eq_bal['cum_ret']
            
            plt.figure(figsize=(14, 7))
            plt.plot(eq_unbal['date'], y_unbal, linewidth=2.5, color='#2E86AB', 
                    label='Unbalanced (Real-World Coverage)', alpha=0.9)
            plt.plot(eq_bal['date'], y_bal, linewidth=2.5, color='#A23B72', 
                    label='Balanced (Robustness Check)', alpha=0.9, linestyle='--')
            
            plt.title('Cumulative Returns: Unbalanced vs Balanced Training', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Cumulative Return', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='best', fontsize=11, framealpha=0.9)
            plt.xticks(rotation=45)
            
            # Format y-axis as percentage
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
            
            # Add final return annotations
            final_unbal = y_unbal.iloc[-1]
            final_bal = y_bal.iloc[-1]
            plt.text(0.02, 0.98, f'Unbalanced: {final_unbal:.2%}\nBalanced: {final_bal:.2%}', 
                    transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            plt.savefig(output_dir / "03_cum_return_comparison.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Saved comparison equity curve: 03_cum_return_comparison.png")
            print(f"  Unbalanced final return: {final_unbal:.2%}")
            print(f"  Balanced final return: {final_bal:.2%}")
            print(f"  Difference: {(final_bal - final_unbal)*100:+.2f}%")
    
    # ========== Plot 2: Sector Sharpe Ratios Comparison ==========
    if sector_unbal.exists() and sector_bal.exists():
        sec_unbal = pd.read_csv(sector_unbal)
        sec_bal = pd.read_csv(sector_bal)
        
        # Filter out Benchmark and fill NaNs (shouldn't have any, but handle gracefully)
        sec_unbal = sec_unbal[sec_unbal["sector"] != "Benchmark"].copy()
        sec_bal = sec_bal[sec_bal["sector"] != "Benchmark"].copy()
        
        sharpe_col_unbal = 'sharpe' if 'sharpe' in sec_unbal.columns else 'sharpe_ratio'
        sharpe_col_bal = 'sharpe' if 'sharpe' in sec_bal.columns else 'sharpe_ratio'
        
        # Fill NaNs with 0 instead of dropping (all sectors should be present)
        sec_unbal[sharpe_col_unbal] = sec_unbal[sharpe_col_unbal].fillna(0.0)
        sec_bal[sharpe_col_bal] = sec_bal[sharpe_col_bal].fillna(0.0)
        
        if not sec_unbal.empty and not sec_bal.empty:
            # Get all sectors and sort by unbalanced Sharpe ratio
            all_sectors = sorted(set(sec_unbal['sector'].unique()) | set(sec_bal['sector'].unique()))
            
            # Create merged DataFrame for comparison
            comparison = pd.DataFrame({'sector': all_sectors})
            comparison = comparison.merge(
                sec_unbal[['sector', sharpe_col_unbal]], 
                on='sector', how='left'
            ).rename(columns={sharpe_col_unbal: 'unbalanced'})
            comparison = comparison.merge(
                sec_bal[['sector', sharpe_col_bal]], 
                on='sector', how='left'
            ).rename(columns={sharpe_col_bal: 'balanced'})
            comparison = comparison.fillna(0)
            
            # Sort by unbalanced Sharpe ratio
            comparison = comparison.sort_values('unbalanced', ascending=False)
            
            x = np.arange(len(comparison))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(16, 8))
            
            bars1 = ax.bar(x - width/2, comparison['unbalanced'], width, 
                          label='Unbalanced (Real-World Coverage)', 
                          color='#2E86AB', alpha=0.8)
            bars2 = ax.bar(x + width/2, comparison['balanced'], width, 
                          label='Balanced (Robustness Check)', 
                          color='#A23B72', alpha=0.8)
            
            ax.set_xlabel('Sector', fontsize=12)
            ax.set_ylabel('Sharpe Ratio', fontsize=12)
            ax.set_title('Sector Sharpe Ratios: Unbalanced vs Balanced Training', 
                        fontsize=16, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(comparison['sector'], rotation=45, ha='right')
            ax.legend(loc='best', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if not np.isnan(height) and height != 0:
                        offset = 0.05 if height >= 0 else -0.05
                        ax.text(bar.get_x() + bar.get_width()/2, height + offset,
                               f'{height:.2f}', ha='center', 
                               va='bottom' if height >= 0 else 'top', fontsize=9)
            
            plt.tight_layout()
            plt.savefig(output_dir / "04_sector_sharpe_comparison.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"\n✓ Saved comparison sector Sharpe: 04_sector_sharpe_comparison.png")
            print(f"\nTop 5 Sectors Comparison:")
            print(f"{'Sector':<25} {'Unbalanced':<12} {'Balanced':<12} {'Change':<10}")
            print("-" * 60)
            for _, row in comparison.head(5).iterrows():
                change = row['balanced'] - row['unbalanced']
                change_str = f"{change:+.2f}"
                print(f"{row['sector']:<25} {row['unbalanced']:<12.2f} {row['balanced']:<12.2f} {change_str:<10}")
    
    # ========== Plot 3: Individual Balanced Charts (for consistency) ==========
    if equity_bal.exists():
        eq_bal = pd.read_csv(equity_bal)
        if not eq_bal.empty:
            eq_bal['date'] = pd.to_datetime(eq_bal['date'])
            y_values = eq_bal['equity'] - 1 if 'equity' in eq_bal.columns else eq_bal['cum_ret']
            
            plt.figure(figsize=(12, 6))
            plt.plot(eq_bal['date'], y_values, linewidth=2, color='#A23B72')
            plt.title('Cumulative Returns Over Time (Balanced Mode)', fontsize=14, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Cumulative Return', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
            plt.tight_layout()
            plt.savefig(output_dir / "01_cum_return_balanced.png", dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ Saved balanced equity curve: 01_cum_return_balanced.png")
    
    if sector_bal.exists():
        sec_bal = pd.read_csv(sector_bal)
        sec_bal = sec_bal[sec_bal["sector"] != "Benchmark"].copy()
        sharpe_col = 'sharpe' if 'sharpe' in sec_bal.columns else 'sharpe_ratio'
        sec_bal[sharpe_col] = sec_bal[sharpe_col].fillna(0.0)  # Fill NaNs instead of dropping
        
        if not sec_bal.empty:
            sec_bal = sec_bal.sort_values(sharpe_col, ascending=False)
            
            plt.figure(figsize=(14, 8))
            colors = ['green' if x >= 0 else 'red' for x in sec_bal[sharpe_col]]
            bars = plt.bar(range(len(sec_bal)), sec_bal[sharpe_col], 
                         color=colors, alpha=0.7)
            
            plt.title('Sharpe Ratio by Sector (Balanced Mode)', fontsize=16, fontweight='bold')
            plt.xlabel('Sector', fontsize=12)
            plt.ylabel('Sharpe Ratio', fontsize=12)
            plt.xticks(range(len(sec_bal)), sec_bal['sector'], rotation=45, ha='right')
            plt.grid(True, alpha=0.3, axis='y')
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            for i, bar in enumerate(bars):
                height = bar.get_height()
                offset = 0.05 if height >= 0 else -0.05
                plt.text(bar.get_x() + bar.get_width()/2, height + offset,
                        f'{height:.2f}', ha='center', 
                        va='bottom' if height >= 0 else 'top', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(output_dir / "02_sector_sharpe_balanced.png", dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ Saved balanced sector Sharpe: 02_sector_sharpe_balanced.png")
    
    print(f"\n✅ All comparison charts saved to: {output_dir}")

if __name__ == "__main__":
    main()

