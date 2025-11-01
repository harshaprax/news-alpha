#!/usr/bin/env python3
"""
Fetch stock prices from Yahoo Finance for all tickers in universe.csv
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime

def main():
    # Read universe
    universe_path = Path("data/clean/universe.csv")
    universe = pd.read_csv(universe_path)
    tickers = universe['ticker'].tolist()
    
    print(f"Fetching prices for {len(tickers)} tickers...")
    
    # Download prices from 2015-01-01 to today (longer history for power)
    start_date = "2015-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    prices = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False
    )
    
    # Convert to long format
    if len(tickers) == 1:
        # Single ticker case
        prices_df = prices.reset_index()
        prices_df['ticker'] = tickers[0]
        prices_df = prices_df.rename(columns={'Date': 'date'})[['date', 'ticker', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
    else:
        # Multiple tickers case - yfinance already gives us the right structure
        prices_df = prices.stack(future_stack=True).reset_index()
        
        # The stacked data has columns: [Date, Ticker, Adj Close, Close, High, Low, Open, Volume]
        # We need to reshape this to long format
        print(f"Stacked columns: {prices_df.columns.tolist()}")
        prices_df.columns = ['date', 'ticker', 'Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']
        
        # Melt to get long format
        prices_df = prices_df.melt(
            id_vars=['date', 'ticker'],
            value_vars=['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume'],
            var_name='metric',
            value_name='value'
        )
        
        # Pivot to get wide format with metrics as columns
        prices_df = prices_df.pivot_table(
            index=['date', 'ticker'], 
            columns='metric', 
            values='value'
        ).reset_index()
        prices_df.columns.name = None
    
    # Rename columns
    prices_df['date'] = pd.to_datetime(prices_df['date']).dt.tz_localize(None)
    prices_df = prices_df[['date', 'ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
    prices_df = prices_df.sort_values(['ticker','date']).dropna()
    
    # Save to parquet
    output_path = Path("data/raw/prices/prices.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prices_df.to_parquet(output_path, index=False)
    
    print(f"Prices shape: {prices_df.shape}")
    print(f"Date range: {prices_df['date'].min()} to {prices_df['date'].max()}")
    print("\nPreview:")
    print(prices_df.head())
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
