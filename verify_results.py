#!/usr/bin/env python3
"""Verify that balanced and unbalanced results have all sectors and no NaNs"""

import pandas as pd
from pathlib import Path

ALL_SECTORS = sorted([
    'Technology', 'Financials', 'Healthcare', 'Energy', 
    'Consumer Discretionary', 'Consumer Staples', 'Industrials',
    'Communication Services', 'Utilities', 'Materials', 'Real Estate'
])

def verify_file(filepath, label):
    """Verify a sector stats file"""
    print(f"\n{'='*60}")
    print(f"Verifying {label}: {filepath.name}")
    print(f"{'='*60}")
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    df = pd.read_csv(filepath)
    
    # Check number of sectors
    num_sectors = len(df)
    print(f"Sectors in file: {num_sectors}")
    print(f"Expected sectors: {len(ALL_SECTORS)}")
    
    if num_sectors != len(ALL_SECTORS):
        print(f"❌ Sector count mismatch!")
        return False
    else:
        print("✅ Sector count correct")
    
    # Check all sectors present
    file_sectors = set(df['sector'].unique())
    expected_sectors = set(ALL_SECTORS)
    
    missing = expected_sectors - file_sectors
    extra = file_sectors - expected_sectors
    
    if missing:
        print(f"❌ Missing sectors: {missing}")
        return False
    if extra:
        print(f"⚠️  Extra sectors: {extra}")
    
    print("✅ All expected sectors present")
    
    # Check for NaNs
    nan_count = df.isnull().sum().sum()
    print(f"\nNaN values: {nan_count}")
    if nan_count > 0:
        print(f"❌ Found NaNs in these columns:")
        print(df.isnull().sum()[df.isnull().sum() > 0])
        return False
    else:
        print("✅ No NaN values")
    
    # Check key metrics
    print(f"\nTop 3 sectors by Sharpe:")
    top3 = df.nlargest(3, 'sharpe')[['sector', 'sharpe', 'ann_return_arith', 'non_zero_days']]
    for _, row in top3.iterrows():
        print(f"  {row['sector']}: Sharpe={row['sharpe']:.3f}, Return={row['ann_return_arith']:.2%}, Days={row['non_zero_days']}")
    
    print(f"\nBottom 3 sectors by Sharpe:")
    bottom3 = df.nsmallest(3, 'sharpe')[['sector', 'sharpe', 'ann_return_arith', 'non_zero_days']]
    for _, row in bottom3.iterrows():
        print(f"  {row['sector']}: Sharpe={row['sharpe']:.3f}, Return={row['ann_return_arith']:.2%}, Days={row['non_zero_days']}")
    
    return True

def main():
    data_dir = Path("data/clean")
    
    unbal_file = data_dir / "sector_stats.csv"
    bal_file = data_dir / "sector_stats_balanced.csv"
    
    unbal_ok = verify_file(unbal_file, "UNBALANCED")
    bal_ok = verify_file(bal_file, "BALANCED")
    
    # Compare sectors
    if unbal_ok and bal_ok:
        print(f"\n{'='*60}")
        print("COMPARISON")
        print(f"{'='*60}")
        
        df_unbal = pd.read_csv(unbal_file)
        df_bal = pd.read_csv(bal_file)
        
        unbal_sectors = set(df_unbal['sector'].unique())
        bal_sectors = set(df_bal['sector'].unique())
        
        if unbal_sectors == bal_sectors:
            print("✅ Both files have the same sectors")
        else:
            print(f"❌ Sector mismatch!")
            print(f"   Unbalanced has: {unbal_sectors - bal_sectors}")
            print(f"   Balanced has: {bal_sectors - unbal_sectors}")
        
        print(f"\n✅ Verification complete!")
        print(f"   Both files have {len(ALL_SECTORS)} sectors")
        print(f"   No NaNs found")
        print(f"   All sectors represented")

if __name__ == "__main__":
    main()

