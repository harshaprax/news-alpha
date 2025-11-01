#!/usr/bin/env python3
"""
Create labels from forward returns and merge with features
"""

import pandas as pd
import numpy as np
from pathlib import Path

def main():
    # Load data
    features_path = Path("data/clean/features_headlines.parquet")
    prices_path = Path("data/raw/prices/prices.parquet")
    universe_path = Path("data/clean/universe.csv")
    
    features_df = pd.read_parquet(features_path)
    prices_df = pd.read_parquet(prices_path)
    universe_df = pd.read_csv(universe_path)
    
    print(f"Features shape: {features_df.shape}")
    print(f"Prices shape: {prices_df.shape}")
    print(f"Universe shape: {universe_df.shape}")
    
    if features_df.empty:
        print("No features found, creating empty training data...")
        training_df = pd.DataFrame(columns=['date', 'ticker', 'headline_cnt', 'sent_mean', 'sent_max', 'sector', 'fwd_ret', 'label'])
        output_path = Path("data/clean/features.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        training_df.to_parquet(output_path, index=False)
        
        csv_path = Path("data/clean/training_data.csv")
        training_df.to_csv(csv_path, index=False)
        print(f"Saved empty training data to: {output_path} and {csv_path}")
        return
    
    # Convert dates
    features_df['date'] = pd.to_datetime(features_df['date'])
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    
    # Pivot prices to wide format for returns calculation
    prices_wide = prices_df.pivot(index='date', columns='ticker', values='Close')
    
    # Calculate daily returns
    returns = prices_wide.pct_change()
    
    # Shift returns to get forward returns (next day)
    fwd_returns = returns.shift(-1)
    
    # Convert back to long format
    fwd_returns_long = fwd_returns.stack().reset_index()
    fwd_returns_long.columns = ['date', 'ticker', 'fwd_ret']
    
    # Merge forward returns with features
    training_df = features_df.merge(
        fwd_returns_long,
        on=['date', 'ticker'],
        how='left'
    )
    
    # Merge sector information
    training_df = training_df.merge(
        universe_df[['ticker', 'sector']],
        on='ticker',
        how='left'
    )
    
    # Create binary label (positive forward return)
    training_df['label'] = (training_df['fwd_ret'] > 0).astype(int)
    
    # Remove rows with missing forward returns (last day of data)
    training_df = training_df.dropna(subset=['fwd_ret'])
    
    # Save to parquet
    output_path = Path("data/clean/features.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    training_df.to_parquet(output_path, index=False)
    
    # Save CSV for inspection
    csv_path = Path("data/clean/training_data.csv")
    training_df.to_csv(csv_path, index=False)
    
    print(f"Training data shape: {training_df.shape}")
    print(f"Date range: {training_df['date'].min()} to {training_df['date'].max()}")
    print(f"Unique tickers: {training_df['ticker'].nunique()}")
    print(f"Unique sectors: {training_df['sector'].nunique()}")
    print(f"NA counts:")
    print(training_df.isnull().sum())
    print("\nPreview:")
    print(training_df.head())
    print(f"\nSaved to: {output_path} and {csv_path}")

if __name__ == "__main__":
    main()

