#!/usr/bin/env python3
"""
Fetch headlines from GDELT Events API with monthly loops for better coverage
"""

import pandas as pd
import requests
from pathlib import Path
from datetime import datetime, timedelta
import time
from tqdm import tqdm

def generate_monthly_windows(start_date, end_date):
    """Generate monthly date windows"""
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    windows = []
    while current <= end:
        # Start of month
        month_start = current.replace(day=1)
        
        # End of month
        if current.month == 12:
            month_end = current.replace(year=current.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current.replace(month=current.month + 1, day=1) - timedelta(days=1)
        
        # Don't go past our end date
        month_end = min(month_end, end)
        
        windows.append((month_start.strftime('%Y%m%d%H%M%S'), 
                       month_end.strftime('%Y%m%d%H%M%S')))
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    return windows

def fetch_headlines_for_month(start_datetime, end_datetime):
    """Fetch headlines for a single month"""
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    params = {
        'query': 'sourcecountry:US',
        'mode': 'artlist',
        'maxrecords': 250,
        'format': 'json',
        'startdatetime': start_datetime,
        'enddatetime': end_datetime
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'articles' not in data:
            return pd.DataFrame()
            
        articles = data['articles']
        
        # Convert to DataFrame
        headlines_df = pd.DataFrame(articles)
        
        # Rename columns
        column_mapping = {
            'seendate': 'published_at',
            'title': 'title',
            'domain': 'domain',
            'url': 'url'
        }
        
        headlines_df = headlines_df.rename(columns=column_mapping)
        
        # Keep only required columns
        headlines_df = headlines_df[['published_at', 'title', 'domain', 'url']]
        
        return headlines_df
        
    except Exception as e:
        print(f"Error fetching headlines for {start_datetime}: {e}")
        return pd.DataFrame()

def main():
    # Configuration
    START_DATE = "2015-01-01"
    END_DATE = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Fetching headlines from {START_DATE} to {END_DATE}")
    print("Generating monthly windows...")
    
    # Generate monthly windows
    windows = generate_monthly_windows(START_DATE, END_DATE)
    print(f"Created {len(windows)} monthly windows")
    
    all_headlines = []
    
    # Fetch headlines for each month
    for start_dt, end_dt in tqdm(windows, desc="Fetching headlines"):
        month_df = fetch_headlines_for_month(start_dt, end_dt)
        
        if not month_df.empty:
            all_headlines.append(month_df)
        
        # Rate limiting
        time.sleep(0.5)
    
    if not all_headlines:
        print("No headlines fetched, creating empty file...")
        headlines_df = pd.DataFrame(columns=['published_at', 'title', 'domain', 'url'])
    else:
        # Concatenate all months
        headlines_df = pd.concat(all_headlines, ignore_index=True)
        
        # Basic cleaning
        headlines_df = headlines_df.dropna(subset=['title'])
        
        # Normalize titles for deduplication
        headlines_df['title_normalized'] = headlines_df['title'].str.lower().str.strip()
        headlines_df['published_at'] = pd.to_datetime(headlines_df['published_at'])
        
        # Drop duplicates by normalized title + published date
        headlines_df = headlines_df.drop_duplicates(subset=['title_normalized', 'published_at'])
        
        # Remove the normalized column
        headlines_df = headlines_df.drop(columns=['title_normalized'])
        
        # Filter to English headlines if language column exists
        if 'language' in headlines_df.columns:
            headlines_df = headlines_df[headlines_df['language'] == 'English']
    
    # Save to parquet
    output_path = Path("data/raw/headlines/headlines.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headlines_df.to_parquet(output_path, index=False)
    
    print(f"\nTotal headlines: {len(headlines_df)}")
    
    if not headlines_df.empty:
        print(f"Date range: {headlines_df['published_at'].min()} to {headlines_df['published_at'].max()}")
        
        # Print rows per year
        headlines_df['year'] = headlines_df['published_at'].dt.year
        yearly_counts = headlines_df['year'].value_counts().sort_index()
        print(f"\nHeadlines per year:")
        for year, count in yearly_counts.items():
            print(f"  {year}: {count}")
    
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
