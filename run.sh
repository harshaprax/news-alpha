#!/usr/bin/env bash
set -e
python src/12_build_universe_sp500.py
python src/10_fetch_prices.py
python src/21_fetch_headlines_gdelt.py
python src/30_alias_map.py
python src/40_make_features.py
python src/45_make_labels.py
python src/50_train_backtest.py
python src/60_charts.py
echo "Done. See data/clean/ and reports/figures/"
