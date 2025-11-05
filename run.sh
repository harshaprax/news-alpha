#!/usr/bin/env bash
set -e

echo "Building S&P 500 universe..."
python src/12_build_universe_sp500.py

echo "Fetching price data..."
python src/10_fetch_prices.py

echo "Fetching headlines from GDELT..."
python src/21_fetch_headlines_gdelt.py

echo "Creating alias mapping..."
python src/30_alias_map.py

echo "Making features..."
python src/40_make_features.py

echo "Making labels..."
python src/45_make_labels.py

echo "Training model and backtesting (unbalanced mode)..."
python src/50_train_backtest.py

echo "Running statistical tests..."
python src/65_stats_tests.py

echo "Generating charts..."
python src/60_charts.py

echo ""
echo "✅ Pipeline complete!"
echo ""
echo "Output files:"
echo "  - data/clean/equity_curve.csv"
echo "  - data/clean/sector_stats.csv"
echo "  - data/clean/sector_ttest.csv"
echo "  - reports/figures/01_cum_return.png"
echo "  - reports/figures/02_sector_sharpe.png"
echo ""
echo "Optional: Run balanced mode for robustness check:"
echo "  python src/50_train_backtest.py --balance-sectors"
echo "  python src/60_charts_comparison.py"
