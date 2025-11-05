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

### Optional: Balanced Sector Training (Robustness Check)

By default, the pipeline uses unbalanced data (reflects real-world media coverage). To run with balanced sectors:

```bash
python src/50_train_backtest.py --balance-sectors
```

This will:
- Downsample all sectors to the minimum sector size
- Generate outputs with `_balanced` suffix (e.g., `sector_stats_balanced.csv`)
- Useful for showing results are robust to sample size differences

**Note**: The unbalanced default is the main analysis (real-world conditions). Balanced mode is a supplementary robustness check.

## Key Features

- **Leakage Guard**: Only headlines published ≤ 15:30 US/Eastern are used for next-day predictions
- **Trading Costs**: 10 bps round-trip cost included in backtest
- **Time Split**: 80% train / 20% test by chronological order
- **Sector Analysis**: One-hot encoded sectors with per-sector performance stats
- **Sector Balancing**: Optional `--balance-sectors` flag for robustness checks (default: unbalanced, reflects real-world media coverage)

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

## Sector Imbalance Note

The data intentionally reflects real-world media coverage differences. Some sectors (Technology, Financials) have many more headlines and stronger predictive signals than others (Utilities, Real Estate). This imbalance is **expected and should be interpreted as part of the findings** rather than a data quality issue. Use `--balance-sectors` for a robustness check that controls for sample size.

