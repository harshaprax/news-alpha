#!/usr/bin/env python3
"""
Build S&P 500 universe from Wikipedia and map to simplified sectors
"""

import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

def main():
    print("Fetching S&P 500 list from Wikipedia...")
    
    try:
        # Fetch S&P 500 table from Wikipedia
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        if not table:
            print("Could not find S&P 500 table")
            return
            
        # Extract data
        rows = table.find_all('tr')[1:]  # Skip header
        data = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                ticker = cells[0].text.strip()
                company = cells[1].text.strip()
                sector = cells[3].text.strip()
                
                # Clean ticker (handle special cases)
                ticker = ticker.replace('.', '-')  # BRK.B -> BRK-B
                
                data.append({
                    'ticker': ticker,
                    'company': company,
                    'gics_sector': sector
                })
        
        df = pd.DataFrame(data)
        print(f"Found {len(df)} companies")
        
    except Exception as e:
        print(f"Error fetching from Wikipedia: {e}")
        print("Using fallback S&P 500 list...")
        
        # Fallback: use a smaller curated list
        fallback_data = [
            # Technology
            ('AAPL', 'Apple Inc.', 'Technology'),
            ('MSFT', 'Microsoft Corporation', 'Technology'),
            ('NVDA', 'NVIDIA Corporation', 'Technology'),
            ('GOOGL', 'Alphabet Inc.', 'Communication Services'),
            ('META', 'Meta Platforms Inc.', 'Communication Services'),
            ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary'),
            ('TSLA', 'Tesla Inc.', 'Consumer Discretionary'),
            ('AVGO', 'Broadcom Inc.', 'Technology'),
            ('ORCL', 'Oracle Corporation', 'Technology'),
            ('CRM', 'Salesforce Inc.', 'Technology'),
            ('AMD', 'Advanced Micro Devices Inc.', 'Technology'),
            ('INTC', 'Intel Corporation', 'Technology'),
            ('ADBE', 'Adobe Inc.', 'Technology'),
            ('NFLX', 'Netflix Inc.', 'Communication Services'),
            ('PYPL', 'PayPal Holdings Inc.', 'Financials'),
            # Financials
            ('JPM', 'JPMorgan Chase & Co.', 'Financials'),
            ('BAC', 'Bank of America Corporation', 'Financials'),
            ('WFC', 'Wells Fargo & Company', 'Financials'),
            ('GS', 'Goldman Sachs Group Inc.', 'Financials'),
            ('MS', 'Morgan Stanley', 'Financials'),
            ('V', 'Visa Inc.', 'Financials'),
            ('MA', 'Mastercard Incorporated', 'Financials'),
            ('C', 'Citigroup Inc.', 'Financials'),
            ('AXP', 'American Express Company', 'Financials'),
            ('BLK', 'BlackRock Inc.', 'Financials'),
            # Healthcare
            ('JNJ', 'Johnson & Johnson', 'Healthcare'),
            ('PFE', 'Pfizer Inc.', 'Healthcare'),
            ('UNH', 'UnitedHealth Group Incorporated', 'Healthcare'),
            ('MRK', 'Merck & Co. Inc.', 'Healthcare'),
            ('ABBV', 'AbbVie Inc.', 'Healthcare'),
            ('TMO', 'Thermo Fisher Scientific Inc.', 'Healthcare'),
            ('ABT', 'Abbott Laboratories', 'Healthcare'),
            ('DHR', 'Danaher Corporation', 'Healthcare'),
            ('BMY', 'Bristol Myers Squibb Company', 'Healthcare'),
            ('AMGN', 'Amgen Inc.', 'Healthcare'),
            # Energy
            ('XOM', 'Exxon Mobil Corporation', 'Energy'),
            ('CVX', 'Chevron Corporation', 'Energy'),
            ('COP', 'ConocoPhillips', 'Energy'),
            ('SLB', 'Schlumberger Limited', 'Energy'),
            ('EOG', 'EOG Resources Inc.', 'Energy'),
            ('KMI', 'Kinder Morgan Inc.', 'Energy'),
            ('PSX', 'Phillips 66', 'Energy'),
            ('MPC', 'Marathon Petroleum Corporation', 'Energy'),
            ('VLO', 'Valero Energy Corporation', 'Energy'),
            ('WMB', 'Williams Companies Inc.', 'Energy'),
            # Consumer Discretionary
            ('HD', 'Home Depot Inc.', 'Consumer Discretionary'),
            ('MCD', 'McDonald\'s Corporation', 'Consumer Discretionary'),
            ('NKE', 'Nike Inc.', 'Consumer Discretionary'),
            ('LOW', 'Lowe\'s Companies Inc.', 'Consumer Discretionary'),
            ('SBUX', 'Starbucks Corporation', 'Consumer Discretionary'),
            ('TJX', 'TJX Companies Inc.', 'Consumer Discretionary'),
            ('BKNG', 'Booking Holdings Inc.', 'Consumer Discretionary'),
            ('CMG', 'Chipotle Mexican Grill Inc.', 'Consumer Discretionary'),
            ('LMT', 'Lockheed Martin Corporation', 'Industrials'),
            ('BA', 'Boeing Company', 'Industrials'),
            # Consumer Staples
            ('WMT', 'Walmart Inc.', 'Consumer Staples'),
            ('COST', 'Costco Wholesale Corporation', 'Consumer Staples'),
            ('KO', 'Coca-Cola Company', 'Consumer Staples'),
            ('PEP', 'PepsiCo Inc.', 'Consumer Staples'),
            ('PG', 'Procter & Gamble Company', 'Consumer Staples'),
            ('CL', 'Colgate-Palmolive Company', 'Consumer Staples'),
            ('KMB', 'Kimberly-Clark Corporation', 'Consumer Staples'),
            ('GIS', 'General Mills Inc.', 'Consumer Staples'),
            ('K', 'Kellogg Company', 'Consumer Staples'),
            ('SYY', 'Sysco Corporation', 'Consumer Staples'),
            # Industrials
            ('CAT', 'Caterpillar Inc.', 'Industrials'),
            ('HON', 'Honeywell International Inc.', 'Industrials'),
            ('GE', 'General Electric Company', 'Industrials'),
            ('UPS', 'United Parcel Service Inc.', 'Industrials'),
            ('RTX', 'Raytheon Technologies Corporation', 'Industrials'),
            ('MMM', '3M Company', 'Industrials'),
            ('DE', 'Deere & Company', 'Industrials'),
            ('ITW', 'Illinois Tool Works Inc.', 'Industrials'),
            ('EMR', 'Emerson Electric Co.', 'Industrials'),
            ('FDX', 'FedEx Corporation', 'Industrials'),
            # Utilities
            ('NEE', 'NextEra Energy Inc.', 'Utilities'),
            ('DUK', 'Duke Energy Corporation', 'Utilities'),
            ('SO', 'Southern Company', 'Utilities'),
            ('EXC', 'Exelon Corporation', 'Utilities'),
            ('AEP', 'American Electric Power Company Inc.', 'Utilities'),
            ('XEL', 'Xcel Energy Inc.', 'Utilities'),
            ('SRE', 'Sempra Energy', 'Utilities'),
            ('PEG', 'Public Service Enterprise Group Incorporated', 'Utilities'),
            ('WEC', 'WEC Energy Group Inc.', 'Utilities'),
            ('ES', 'Eversource Energy', 'Utilities'),
            # Communication Services
            ('DIS', 'Walt Disney Company', 'Communication Services'),
            ('T', 'AT&T Inc.', 'Communication Services'),
            ('VZ', 'Verizon Communications Inc.', 'Communication Services'),
            ('CMCSA', 'Comcast Corporation', 'Communication Services'),
            ('CHTR', 'Charter Communications Inc.', 'Communication Services'),
            ('TMUS', 'T-Mobile US Inc.', 'Communication Services'),
            ('NFLX', 'Netflix Inc.', 'Communication Services'),
            ('GOOGL', 'Alphabet Inc.', 'Communication Services'),
            ('META', 'Meta Platforms Inc.', 'Communication Services'),
            ('TWTR', 'Twitter Inc.', 'Communication Services'),
            # Materials
            ('LIN', 'Linde plc', 'Materials'),
            ('NEM', 'Newmont Corporation', 'Materials'),
            ('FCX', 'Freeport-McMoRan Inc.', 'Materials'),
            ('APD', 'Air Products and Chemicals Inc.', 'Materials'),
            ('SHW', 'Sherwin-Williams Company', 'Materials'),
            ('ECL', 'Ecolab Inc.', 'Materials'),
            ('DD', 'DuPont de Nemours Inc.', 'Materials'),
            ('DOW', 'Dow Inc.', 'Materials'),
            ('PPG', 'PPG Industries Inc.', 'Materials'),
            ('IFF', 'International Flavors & Fragrances Inc.', 'Materials'),
            # Real Estate
            ('PLD', 'Prologis Inc.', 'Real Estate'),
            ('AMT', 'American Tower Corporation', 'Real Estate'),
            ('SPG', 'Simon Property Group Inc.', 'Real Estate'),
            ('CCI', 'Crown Castle Inc.', 'Real Estate'),
            ('EQIX', 'Equinix Inc.', 'Real Estate'),
            ('PSA', 'Public Storage', 'Real Estate'),
            ('EXR', 'Extra Space Storage Inc.', 'Real Estate'),
            ('AVB', 'AvalonBay Communities Inc.', 'Real Estate'),
            ('EQR', 'Equity Residential', 'Real Estate'),
            ('MAA', 'Mid-America Apartment Communities Inc.', 'Real Estate'),
            # Benchmark
            ('SPY', 'SPDR S&P 500 ETF Trust', 'Benchmark')
        ]
        
        df = pd.DataFrame(fallback_data, columns=['ticker', 'company', 'gics_sector'])
        print(f"Using fallback list with {len(df)} companies")
    
    # Map GICS sectors to simplified sectors
    sector_mapping = {
        'Information Technology': 'Technology',
        'Technology': 'Technology',
        'Financials': 'Financials',
        'Financial Services': 'Financials',
        'Health Care': 'Healthcare',
        'Healthcare': 'Healthcare',
        'Energy': 'Energy',
        'Consumer Discretionary': 'Consumer Discretionary',
        'Consumer Staples': 'Consumer Staples',
        'Industrials': 'Industrials',
        'Utilities': 'Utilities',
        'Communication Services': 'Communication Services',
        'Communication': 'Communication Services',
        'Materials': 'Materials',
        'Real Estate': 'Real Estate',
        'Benchmark': 'Benchmark'
    }
    
    df['sector'] = df['gics_sector'].map(sector_mapping).fillna('Other')
    
    # Remove duplicates and clean
    df = df.drop_duplicates(subset=['ticker'])
    df = df[df['ticker'].str.len() <= 5]  # Remove weird tickers
    
    # Save universe
    output_path = Path("data/clean/universe.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    universe_df = df[['ticker', 'sector']].copy()
    universe_df.to_csv(output_path, index=False)
    
    # Print sector counts
    print(f"\nSector distribution:")
    sector_counts = universe_df['sector'].value_counts()
    for sector, count in sector_counts.items():
        print(f"  {sector}: {count}")
    
    print(f"\nTotal tickers: {len(universe_df)}")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()

