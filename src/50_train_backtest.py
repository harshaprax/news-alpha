#!/usr/bin/env python3
"""Train logistic regression, run daily backtest, compute robust metrics."""

from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

def compute_daily_metrics(daily_returns: pd.Series) -> dict:
    r = pd.to_numeric(daily_returns, errors="coerce").fillna(0.0).astype(float)
    n = len(r)
    if n == 0:
        return {
            "ann_return_arith": np.nan,
            "ann_return_geom": np.nan,
            "ann_vol": np.nan,
            "sharpe": np.nan,
            "max_drawdown": np.nan,
            "days": 0,
            "non_zero_days": 0,
        }
    mu_d = r.mean()
    sd_d = r.std(ddof=1)
    ann_return_arith = mu_d * 252.0
    ann_vol = sd_d * np.sqrt(252.0)
    sharpe = (ann_return_arith / ann_vol) if ann_vol > 0 else np.nan
    equity = (1.0 + r).cumprod()
    total = equity.iloc[-1] - 1.0
    ann_return_geom = (1.0 + total) ** (252.0 / n) - 1.0
    peak = equity.cummax()
    max_dd = (equity / peak - 1.0).min()
    return {
        "ann_return_arith": ann_return_arith,
        "ann_return_geom": ann_return_geom,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "days": n,
        "non_zero_days": int((r != 0).sum()),
    }

TOP_N_PER_SECTOR = 1     # pick top 1 stock from each sector per day
COST_BPS_RT = 10         # round-trip trading cost in bps
TRAIN_Q = 0.80           # 80% time split
DATA_DIR = Path("data/clean")
OUT_EQUITY = DATA_DIR / "equity_curve.csv"
OUT_SECTOR = DATA_DIR / "sector_stats.csv"
OUT_SECTOR_DAILY = DATA_DIR / "sector_daily_returns.csv"

# Define all sectors (excluding Benchmark) - must be consistent across runs
ALL_SECTORS = sorted([
    'Technology', 'Financials', 'Healthcare', 'Energy', 
    'Consumer Discretionary', 'Consumer Staples', 'Industrials',
    'Communication Services', 'Utilities', 'Materials', 'Real Estate'
])


def balance_sectors_by_sampling(df_train: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    """
    Balance sectors by downsampling to the minimum sector size.
    This is useful as a robustness check to ensure results aren't driven by sample size.
    
    Args:
        df_train: Training DataFrame with 'sector' column
        random_state: Random seed for reproducibility
        
    Returns:
        Balanced DataFrame with equal samples per sector
    """
    sector_counts = df_train['sector'].value_counts()
    min_samples = sector_counts.min()
    
    print(f"\nBalancing sectors: min samples = {min_samples}")
    print(f"Original sector counts:\n{sector_counts}")
    
    balanced_samples = []
    for sector in sector_counts.index:
        sector_data = df_train[df_train['sector'] == sector]
        if len(sector_data) > min_samples:
            # Downsample to min_samples
            sector_data = sector_data.sample(n=min_samples, random_state=random_state)
        balanced_samples.append(sector_data)
    
    df_balanced = pd.concat(balanced_samples, ignore_index=True).sort_values('date')
    
    print(f"\nBalanced sector counts:\n{df_balanced['sector'].value_counts()}")
    print(f"Original size: {len(df_train)}, Balanced size: {len(df_balanced)}")
    
    return df_balanced


def main():
    parser = argparse.ArgumentParser(description='Train and backtest logistic regression model')
    parser.add_argument('--balance-sectors', action='store_true',
                       help='Balance sectors in training set (downsample to min sector size). '
                            'Useful as robustness check. Default: False (unbalanced, reflects real-world coverage)')
    args = parser.parse_args()
    
    df = pd.read_parquet(DATA_DIR / "features.parquet").sort_values("date").copy()
    df["date"] = pd.to_datetime(df["date"])

    # Chronological split
    split_date = df["date"].quantile(TRAIN_Q)
    train_mask = df["date"] <= split_date
    test_mask  = df["date"] >  split_date

    df_train = df[train_mask].copy()
    test = df[test_mask].copy()
    
    # Optional sector balancing (for robustness check)
    train_size_before = len(df_train)
    if args.balance_sectors:
        print(f"\n{'='*60}")
        print("BALANCING SECTORS (Robustness Check Mode)")
        print(f"{'='*60}")
        df_train = balance_sectors_by_sampling(df_train, random_state=42)
        train_size_after = len(df_train)
        reduction_pct = (1 - train_size_after / train_size_before) * 100
        print(f"\n⚠️  Using BALANCED training set:")
        print(f"   Training size: {train_size_before} → {train_size_after} ({reduction_pct:.1f}% reduction)")
        print(f"   This will train a different model than unbalanced mode!")
        # Modify output filenames to indicate balanced version
        global OUT_EQUITY, OUT_SECTOR, OUT_SECTOR_DAILY
        OUT_EQUITY = DATA_DIR / "equity_curve_balanced.csv"
        OUT_SECTOR = DATA_DIR / "sector_stats_balanced.csv"
        OUT_SECTOR_DAILY = DATA_DIR / "sector_daily_returns_balanced.csv"
    else:
        print(f"\n✓ Using UNBALANCED training set (reflects real-world media coverage)")
        print(f"   Training size: {train_size_before} rows")

    # One-hot encode sector for the model
    # Get all unique sectors from both train and test to ensure consistent encoding
    all_sectors = sorted(set(df_train["sector"].dropna().unique()) | set(test["sector"].dropna().unique()))
    
    # Create consistent sector column names (drop_first means first sector is omitted)
    first_sector = all_sectors[0]
    sector_cols = [f"sector_{s}" for s in all_sectors[1:]]  # Skip first sector due to drop_first=True
    
    # Create sector dummies for training set
    sector_dum_train = pd.get_dummies(df_train["sector"], prefix="sector", drop_first=True)
    # Add any missing sector columns as zeros
    for col in sector_cols:
        if col not in sector_dum_train.columns:
            sector_dum_train[col] = 0
    
    # Create feature matrix for training
    feature_cols = ["headline_cnt", "sent_mean", "sent_max"]
    X_train = pd.concat([df_train[feature_cols], sector_dum_train], axis=1)
    # Ensure columns are in consistent order
    X_train = X_train[feature_cols + sector_cols].fillna(0.0)
    y_train = df_train["label"].astype(int)
    
    # Encode test set with same sector dummies (must match training exactly)
    sector_dum_test = pd.get_dummies(test["sector"], prefix="sector", drop_first=True)
    # Add any missing sector columns as zeros to match training
    for col in sector_cols:
        if col not in sector_dum_test.columns:
            sector_dum_test[col] = 0
    
    # Create feature matrix for test (must match training column order exactly)
    X_test = pd.concat([test[feature_cols], sector_dum_test], axis=1)
    X_test = X_test[feature_cols + sector_cols].fillna(0.0)  # Same column order as training
    y_test = test["label"].astype(int)

    # Scale features (optional but fine)
    # Convert to numpy arrays to avoid sklearn feature name validation issues
    # (Column order is already guaranteed to match above)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train.values)
    X_test_s  = scaler.transform(X_test.values)

    # Train logistic regression
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_s, y_train)

    # Eval
    acc = accuracy_score(y_test, clf.predict(X_test_s))
    if args.balance_sectors:
        print(f"\n⚠️  BALANCED MODE - Test accuracy: {acc:.3f}  |  Train:{len(df_train)} Test:{len(test)} rows")
        print(f"   (Training set was downsampled to balance sectors)")
    else:
        print(f"\n✓ UNBALANCED MODE - Test accuracy: {acc:.3f}  |  Train:{len(df_train)} Test:{len(test)} rows")

    # Predict probs
    test["p_up"] = clf.predict_proba(X_test_s)[:, 1]

    # Backtest parameters
    cost = COST_BPS_RT / 10000.0

    # Daily portfolio returns - pick top 1 stock from each sector
    # This ensures all sectors are represented every day
    daily_rows, picks_rows = [], []
    for d, g in test.groupby("date", sort=True):
        if g.empty:
            daily_rows.append({"date": d, "ret": 0.0, "selected_tickers": ""})
            # Add zero picks for all sectors to maintain consistency
            for sector in ALL_SECTORS:
                picks_rows.append({"date": d, "ticker": "", "sector": sector, "ret": 0.0})
            continue

        # Pick top 1 stock from each sector - ensures all sectors represented
        sector_picks = []
        picked_sectors = set()
        
        for sector in ALL_SECTORS:
            sector_data = g[g["sector"] == sector]
            if not sector_data.empty:
                # Get top stock from this sector
                top_sector = sector_data.nlargest(TOP_N_PER_SECTOR, "p_up")
                sector_picks.append(top_sector)
                picked_sectors.add(sector)
        
        if sector_picks:
            # Combine all sector picks
            top = pd.concat(sector_picks, ignore_index=True)
            total_picks = len(top)
            
            gross = top["fwd_ret"].mean()
            net = gross - cost
            daily_rows.append({
                "date": d,
                "ret": float(net),
                "selected_tickers": ",".join(top["ticker"].tolist())
            })

            # Store per-pick for sector daily returns (real picks)
            for _, r in top.iterrows():
                picks_rows.append({"date": d, "ticker": r["ticker"], "sector": r["sector"], "ret": float(r["fwd_ret"] - cost)})
            
            # For sectors that had no stocks available on this day, add zero entries
            # This ensures ALL sectors are represented in picks_rows
            for sector in ALL_SECTORS:
                if sector not in picked_sectors:
                    picks_rows.append({"date": d, "ticker": "", "sector": sector, "ret": 0.0})
        else:
            # No picks available for any sector (unlikely but handle gracefully)
            daily_rows.append({"date": d, "ret": 0.0, "selected_tickers": ""})
            for sector in ALL_SECTORS:
                picks_rows.append({"date": d, "ticker": "", "sector": sector, "ret": 0.0})

    daily_df = pd.DataFrame(daily_rows)
    cal = pd.DataFrame({"date": pd.bdate_range(test["date"].min(), test["date"].max())})
    equity_df = cal.merge(daily_df, on="date", how="left").fillna({"ret": 0.0, "selected_tickers": ""})
    equity_df["equity"] = (1.0 + equity_df["ret"]).cumprod()
    equity_df["cum_ret"] = equity_df["equity"] - 1.0

    # Portfolio metrics
    pm = compute_daily_metrics(equity_df["ret"])
    mode_label = "BALANCED" if args.balance_sectors else "UNBALANCED"
    print(f"\n=== Portfolio Metrics ({mode_label} mode, daily-based) ===")
    print(f"Days: {pm['days']}  |  Non-zero days: {pm['non_zero_days']}")
    print(f"Annualized Return (arith): {pm['ann_return_arith']:.2%}" if pd.notna(pm['ann_return_arith']) else "Annualized Return (arith): n/a")
    print(f"Annualized Return (geom):  {pm['ann_return_geom']:.2%}"  if pd.notna(pm['ann_return_geom'])  else "Annualized Return (geom): n/a")
    print(f"Annualized Volatility:     {pm['ann_vol']:.2%}"          if pd.notna(pm['ann_vol'])          else "Annualized Volatility: n/a")
    print(f"Sharpe Ratio:              {pm['sharpe']:.2f}"           if pd.notna(pm['sharpe'])           else "Sharpe Ratio: n/a")
    print(f"Max Drawdown:              {pm['max_drawdown']:.2%}"     if pd.notna(pm['max_drawdown'])     else "Max Drawdown: n/a")

    # Sector metrics (daily with zeros) - ensure ALL sectors are included
    sector_stats_rows = []
    all_days = pd.bdate_range(equity_df["date"].min(), equity_df["date"].max())
    
    if picks_rows:
        picked_df = pd.DataFrame(picks_rows)
        # Calculate daily returns per sector (including zero entries)
        # Group by date and sector, taking mean return (zeros for missing sectors)
        sec_daily = (picked_df.groupby(["date","sector"], as_index=False)["ret"]
                     .mean().rename(columns={"ret":"sec_ret"}))
        
        # Create full grid with ALL_SECTORS for ALL_DAYS - ensures consistency
        grid = pd.MultiIndex.from_product([all_days, ALL_SECTORS], names=["date","sector"])
        sec_df = (pd.DataFrame(index=grid).reset_index()
                    .merge(sec_daily, on=["date","sector"], how="left")
                    .fillna({"sec_ret": 0.0}))
        
        # Calculate metrics for ALL sectors (guaranteed to exist in grid)
        for s in ALL_SECTORS:
            g = sec_df[sec_df["sector"] == s]
            m = compute_daily_metrics(g["sec_ret"])
            m["sector"] = s
            sector_stats_rows.append(m)
    else:
        # No picks at all (shouldn't happen, but handle gracefully)
        for s in ALL_SECTORS:
            m = compute_daily_metrics(pd.Series([0.0] * len(all_days)))
            m["sector"] = s
            sector_stats_rows.append(m)
    
    sector_stats = (pd.DataFrame(sector_stats_rows)
                    .sort_values("sharpe", ascending=False)
                    .reset_index(drop=True))
    
    # Ensure all sectors are present - no filtering out sectors
    # All sectors should have at least some data (even if zeros)
    assert len(sector_stats) == len(ALL_SECTORS), f"Expected {len(ALL_SECTORS)} sectors, got {len(sector_stats)}"
    
    # Verify no NaN values in key columns
    for col in ['sharpe', 'ann_return_arith', 'ann_vol']:
        if col in sector_stats.columns:
            sector_stats[col] = sector_stats[col].fillna(0.0)

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    equity_df.to_csv(OUT_EQUITY, index=False)
    sector_stats.to_csv(OUT_SECTOR, index=False)
    if picks_rows:
        sec_df = sec_df.sort_values(["date", "sector"]).reset_index(drop=True)
        sec_df.to_csv(OUT_SECTOR_DAILY, index=False)

    mode_label = "BALANCED" if args.balance_sectors else "UNBALANCED"
    print(f"\n=== Saved {mode_label} mode outputs ===")
    print(f"- {OUT_EQUITY}")
    print(f"- {OUT_SECTOR}")
    if picks_rows:
        print(f"- {OUT_SECTOR_DAILY}")
    if args.balance_sectors:
        print(f"\n💡 Compare these with the UNBALANCED versions:")
        print(f"   - equity_curve.csv (unbalanced)")
        print(f"   - sector_stats.csv (unbalanced)")
        print(f"   - sector_daily_returns.csv (unbalanced)")
if __name__ == "__main__":
    main()
