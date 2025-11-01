# News-Sentiment by Sector

This project analyzes which sectors are most predictable by recent headlines using sentiment analysis and machine learning.

## Setup

1. Create virtual environment:
```bash
python -m venv .venv
```

2. Activate virtual environment:
- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Download NLTK VADER lexicon:
```bash
python -c "import nltk; nltk.download('vader_lexicon')"
```

## Running the Pipeline

Run the complete pipeline:
```bash
bash run.sh
```

Or run scripts individually on Windows.

## Key Features

- **Leakage Guard**: Only headlines published ≤ 15:30 US/Eastern are used for next-day predictions
- **Trading Costs**: 10 bps round-trip cost included in backtest
- **Time Split**: 80% train / 20% test by chronological order
- **Sector Analysis**: One-hot encoded sectors with per-sector performance stats

## Deliverables

- `data/clean/training_data.csv`: Full dataset for inspection
- `data/clean/equity_curve.csv`: Daily returns and cumulative performance
- `data/clean/sector_stats.csv`: Per-sector performance metrics
- `reports/figures/01_cum_return.png`: Equity curve chart
- `reports/figures/02_sector_sharpe.png`: Sector Sharpe ratios

## Data Sources

- Stock prices: Yahoo Finance (yfinance)
- News headlines: GDELT Events API
- Sectors: Custom universe of ~60-80 large-cap US stocks

