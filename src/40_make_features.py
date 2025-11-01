#!/usr/bin/env python3
"""
Create features from headlines using VADER sentiment analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

def main():
    # Download VADER lexicon if not already downloaded
    try:
        nltk.data.find('vader_lexicon')
    except LookupError:
        print("Downloading VADER lexicon...")
        nltk.download('vader_lexicon')
    
    # Initialize VADER
    sia = SentimentIntensityAnalyzer()
    
    # Load data
    prices_path = Path("data/raw/prices/prices.parquet")
    headlines_path = Path("data/raw/headlines/headlines.parquet")
    alias_path = Path("data/clean/alias_map.parquet")
    
    prices_df = pd.read_parquet(prices_path)
    headlines_df = pd.read_parquet(headlines_path)
    alias_df = pd.read_parquet(alias_path)
    
    print(f"Prices shape: {prices_df.shape}")
    print(f"Headlines shape: {headlines_df.shape}")
    print(f"Alias map shape: {alias_df.shape}")
    
    if headlines_df.empty:
        print("No headlines found, creating empty features...")
        # Create empty features DataFrame
        features_df = pd.DataFrame(columns=['date', 'ticker', 'headline_cnt', 'sent_mean', 'sent_max'])
        output_path = Path("data/clean/features_headlines.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        features_df.to_parquet(output_path, index=False)
        print(f"Saved empty features to: {output_path}")
        return
    
    # Convert published_at to timezone-aware UTC
    headlines_df['published_at'] = pd.to_datetime(headlines_df['published_at'])
    
    # Check if already timezone-aware
    if headlines_df['published_at'].dt.tz is None:
        headlines_df['published_at'] = headlines_df['published_at'].dt.tz_localize('UTC')
    else:
        # Already timezone-aware, convert to UTC if needed
        headlines_df['published_at'] = headlines_df['published_at'].dt.tz_convert('UTC')
    
    # Convert to US/Eastern
    headlines_df['published_at_et'] = headlines_df['published_at'].dt.tz_convert('US/Eastern')
    
    # Leakage guard: only headlines published <= 15:30 same day
    headlines_df['date'] = headlines_df['published_at_et'].dt.date
    headlines_df['time'] = headlines_df['published_at_et'].dt.time
    
    # Filter for headlines published before 15:30 ET
    cutoff_time = pd.Timestamp('15:30:00').time()
    headlines_df = headlines_df[headlines_df['time'] <= cutoff_time]
    
    print(f"Headlines after leakage guard: {len(headlines_df)}")
    
    # Lowercase titles for matching
    headlines_df['title_lower'] = headlines_df['title'].str.lower()
    
    # Normalize titles: remove punctuation, compress spaces
    headlines_df['title_normalized'] = headlines_df['title_lower'].str.replace(r'[^\w\s]', ' ', regex=True)
    headlines_df['title_normalized'] = headlines_df['title_normalized'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Map tickers by checking if any alias substring exists in title
    ticker_matches = []
    
    for _, row in headlines_df.iterrows():
        title_normalized = row['title_normalized']
        matched_tickers = []
        
        for _, alias_row in alias_df.iterrows():
            alias = alias_row['alias'].lower()
            mode = alias_row['mode']
            
            if mode == 'word':
                # Use word boundary matching for brand names
                import re
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, title_normalized):
                    matched_tickers.append(alias_row['ticker'])
            else:  # mode == 'contains'
                # Use substring matching
                if alias in title_normalized:
                    matched_tickers.append(alias_row['ticker'])
        
        # Remove duplicates
        matched_tickers = list(set(matched_tickers))
        
        for ticker in matched_tickers:
            ticker_matches.append({
                'date': row['date'],
                'ticker': ticker,
                'title': row['title'],
                'published_at_et': row['published_at_et']
            })
    
    if not ticker_matches:
        print("No ticker matches found, creating empty features...")
        features_df = pd.DataFrame(columns=['date', 'ticker', 'headline_cnt', 'sent_mean', 'sent_max'])
        output_path = Path("data/clean/features_headlines.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        features_df.to_parquet(output_path, index=False)
        print(f"Saved empty features to: {output_path}")
        return
    
    matches_df = pd.DataFrame(ticker_matches)
    print(f"Ticker matches: {len(matches_df)}")
    
    # Calculate match hit-rate
    total_headlines = len(headlines_df)
    unique_matched_dates = len(set([row['date'] for row in ticker_matches]))
    hit_rate = unique_matched_dates / total_headlines if total_headlines > 0 else 0
    print(f"Match hit-rate: {hit_rate:.1%} ({unique_matched_dates} headlines matched out of {total_headlines})")
    
    # Compute VADER sentiment
    matches_df['sentiment'] = matches_df['title'].apply(
        lambda x: sia.polarity_scores(x)['compound']
    )
    
    # Aggregate to ticker-day features
    features_df = matches_df.groupby(['date', 'ticker']).agg({
        'title': 'count',
        'sentiment': ['mean', 'max']
    }).reset_index()
    
    # Flatten column names
    features_df.columns = ['date', 'ticker', 'headline_cnt', 'sent_mean', 'sent_max']
    
    # Convert date back to datetime
    features_df['date'] = pd.to_datetime(features_df['date'])
    
    # Save to parquet
    output_path = Path("data/clean/features_headlines.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_parquet(output_path, index=False)
    
    print(f"Features shape: {features_df.shape}")
    print(f"Date range: {features_df['date'].min()} to {features_df['date'].max()}")
    print(f"Unique tickers: {features_df['ticker'].nunique()}")
    print("\nPreview:")
    print(features_df.head())
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
