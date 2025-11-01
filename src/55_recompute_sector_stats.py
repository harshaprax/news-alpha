#!/usr/bin/env python3
"""
Recompute sector statistics from daily time series with proper calendarization
"""

import pandas as pd
import numpy as np
from pathlib import Path

def compute_daily_metrics(daily_returns: pd.Series) -> dict:
    r = pd.to_numeric(daily_returns, errors="coerce").fillna(0.0).astype(float)
    n = len(r)
    if n == 0:
        return {
            "ann_return_arith": np.nan,
            "ann_return_geom": np.nan,
            "ann_vol": np.nan,
            "sharpe": np.nan,
            "max_drawdown": np.nan,
            "days": 0,
            "non_zero_days": 0,
        }
    mu_d = r.mean()
    sd_d = r.std(ddof=1)
    ann_return_arith = mu_d * 252.0
    ann_vol = sd_d * np.sqrt(252.0)
    sharpe = (ann_return_arith / ann_vol) if ann_vol > 0 else np.nan
    equity = (1.0 + r).cumprod()
    total = equity.iloc[-1] - 1.0
    ann_return_geom = (1.0 + total) ** (252.0 / n) - 1.0
    peak = equity.cummax()
    max_dd = (equity / peak - 1.0).min()
    return {
        "ann_return_arith": ann_return_arith,
        "ann_return_geom": ann_return_geom,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "days": n,
        "non_zero_days": int((r != 0).sum()),
    }

def main():
    # Load data
    equity_path = Path("data/clean/equity_curve.csv")
    training_path = Path("data/clean/training_data.csv")
    
    if not equity_path.exists() or not training_path.exists():
        print("Required files not found")
        return
    
    equity_df = pd.read_csv(equity_path)
    training_df = pd.read_csv(training_path)
    
    print(f"Equity curve shape: {equity_df.shape}")
    print(f"Training data shape: {training_df.shape}")
    
    # Convert dates
    equity_df['date'] = pd.to_datetime(equity_df['date'])
    training_df['date'] = pd.to_datetime(training_df['date'])
    
    # Get test period dates from equity curve
    test_start = equity_df['date'].min()
    test_end = equity_df['date'].max()
    
    # Filter training data to test period
    test_data = training_df[
        (training_df['date'] >= test_start) & 
        (training_df['date'] <= test_end)
    ].copy()
    
    print(f"Test period: {test_start.date()} to {test_end.date()}")
    print(f"Test data points: {len(test_data)}")
    
    # Build sector daily returns matrix
    # Create business day calendar
    business_days = pd.bdate_range(start=test_start, end=test_end, freq='B')
    calendar_df = pd.DataFrame({'date': business_days})
    
    # Get unique sectors
    sectors = test_data['sector'].unique()
    print(f"Unique sectors: {len(sectors)}")
    
    # Initialize sector returns DataFrame
    sector_returns = calendar_df.copy()
    
    # For each sector, compute daily returns
    for sector in sectors:
        sector_data = test_data[test_data['sector'] == sector].copy()
        
        if len(sector_data) == 0:
            sector_returns[f'{sector}_ret'] = 0.0
            continue
        
        # Group by date and compute average return for the sector
        sector_daily = sector_data.groupby('date')['fwd_ret'].mean().reset_index()
        sector_daily.columns = ['date', f'{sector}_ret']
        
        # Merge with calendar (fill missing days with 0)
        sector_returns = sector_returns.merge(sector_daily, on='date', how='left')
        sector_returns[f'{sector}_ret'] = sector_returns[f'{sector}_ret'].fillna(0.0)
    
    print(f"Sector returns matrix shape: {sector_returns.shape}")
    
    # Compute metrics for each sector
    sector_stats = []
    min_days = 30  # Lower threshold for more sectors
    
    for sector in sectors:
        ret_col = f'{sector}_ret'
        
        if ret_col not in sector_returns.columns:
            continue
            
        returns = sector_returns[ret_col]
        
        if len(returns) >= min_days:
            # Calculate metrics using corrected formula
            metrics = compute_daily_metrics(returns)
            
            sector_stats.append({
                'sector': sector,
                'annualized_return_arith': metrics['ann_return_arith'],
                'annualized_return_geom': metrics['ann_return_geom'],
                'annualized_vol': metrics['ann_vol'],
                'sharpe_ratio': metrics['sharpe'],
                'max_drawdown': metrics['max_drawdown'],
                'days': metrics['days'],
                'non_zero_days': metrics['non_zero_days']
            })
    
    sector_stats_df = pd.DataFrame(sector_stats)
    
    if len(sector_stats_df) > 0:
        sector_stats_df = sector_stats_df.sort_values('sharpe_ratio', ascending=False)
        print(f"\nSector Statistics (min {min_days} days):")
        print(sector_stats_df)
        
        print(f"\nTop 5 Sectors by Sharpe Ratio:")
        top_5 = sector_stats_df.head(5)
        for _, row in top_5.iterrows():
            print(f"{row['sector']}: {row['sharpe_ratio']:.3f} (days: {row['days']}, non-zero: {row['non_zero_days']})")
    else:
        sector_stats_df = pd.DataFrame(columns=['sector', 'annualized_return_arith', 'annualized_return_geom', 'annualized_vol', 'sharpe_ratio', 'max_drawdown', 'days', 'non_zero_days'])
        print(f"\nNo sectors with sufficient data (min {min_days} days)")
    
    # Save results
    output_path = Path("data/clean/sector_stats.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sector_stats_df.to_csv(output_path, index=False)
    
    print(f"\nSaved sector stats to: {output_path}")
    print(f"Sector stats rows: {len(sector_stats_df)}")

if __name__ == "__main__":
    main()
