#!/usr/bin/env python3
"""
Create charts for equity curve and sector performance
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def main():
    # Set up output directory
    output_dir = Path("reports/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load equity curve data
    equity_path = Path("data/clean/equity_curve.csv")
    sector_path = Path("data/clean/sector_stats.csv")
    
    # Plot 1: Cumulative Returns
    if equity_path.exists():
        equity_df = pd.read_csv(equity_path)
        
        if not equity_df.empty:
            equity_df['date'] = pd.to_datetime(equity_df['date'])
            
            # Use equity column if available, otherwise cum_ret
            if 'equity' in equity_df.columns:
                y_values = equity_df['equity'] - 1  # Convert equity to cumulative return
                y_label = 'Cumulative Return'
            else:
                y_values = equity_df['cum_ret']
                y_label = 'Cumulative Return'
            
            plt.figure(figsize=(12, 6))
            plt.plot(equity_df['date'], y_values, linewidth=2, color='blue')
            plt.title('Cumulative Returns Over Time', fontsize=14, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Format y-axis as percentage
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
            
            plt.tight_layout()
            plt.savefig(output_dir / "01_cum_return.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Saved equity curve chart to: {output_dir / '01_cum_return.png'}")
        else:
            print("No equity curve data to plot")
    else:
        print(f"Equity curve file not found: {equity_path}")
    
    # Plot 2: Sector Sharpe Ratios
    if sector_path.exists():
        sector_df = pd.read_csv(sector_path)
        
        if not sector_df.empty:
            sector_df = sector_df[sector_df["sector"] != "Benchmark"]
        
        if not sector_df.empty:
            # Show all sectors, but filter out those with NaN Sharpe ratios
            if 'sharpe' in sector_df.columns:
                sector_df = sector_df.dropna(subset=['sharpe'])
            elif 'sharpe_ratio' in sector_df.columns:
                sector_df = sector_df.dropna(subset=['sharpe_ratio'])
            
            if not sector_df.empty:
                plt.figure(figsize=(14, 8))
                # Use 'sharpe' column if available, otherwise 'sharpe_ratio'
                sharpe_col = 'sharpe' if 'sharpe' in sector_df.columns else 'sharpe_ratio'
                
                # Color bars based on positive/negative Sharpe ratio
                colors = ['green' if x >= 0 else 'red' for x in sector_df[sharpe_col]]
                bars = plt.bar(range(len(sector_df)), sector_df[sharpe_col], 
                             color=colors, alpha=0.7)
                
                plt.title('Sharpe Ratio by Sector', fontsize=16, fontweight='bold')
                plt.xlabel('Sector', fontsize=12)
                plt.ylabel('Sharpe Ratio', fontsize=12)
                plt.xticks(range(len(sector_df)), sector_df['sector'], rotation=45, ha='right')
                plt.grid(True, alpha=0.3, axis='y')
                
                # Add horizontal line at zero
                plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    offset = 0.05 if height >= 0 else -0.05
                    plt.text(bar.get_x() + bar.get_width()/2, height + offset,
                            f'{height:.2f}', ha='center', 
                            va='bottom' if height >= 0 else 'top', fontsize=10)
                
                plt.tight_layout()
                plt.savefig(output_dir / "02_sector_sharpe.png", dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"Saved sector Sharpe chart to: {output_dir / '02_sector_sharpe.png'}")
                
                # Print all sectors sorted by Sharpe ratio
                print(f"\nAll Sectors by Sharpe Ratio:")
                for _, row in sector_df.iterrows():
                    sharpe_val = row.get('sharpe', row.get('sharpe_ratio', 'N/A'))
                    if 'non_zero_days' in row:
                        print(f"{row['sector']}: {sharpe_val:.3f} (non-zero days: {row['non_zero_days']})")
                    elif 'trades' in row:
                        print(f"{row['sector']}: {sharpe_val:.3f} (trades: {row['trades']})")
                    else:
                        print(f"{row['sector']}: {sharpe_val:.3f}")
            else:
                print("No sector data with sufficient trades to plot")
        else:
            print("No sector statistics data to plot")
    else:
        print(f"Sector stats file not found: {sector_path}")
    
    print(f"\nCharts saved to: {output_dir}")

if __name__ == "__main__":
    main()
