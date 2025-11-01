#!/usr/bin/env python3
"""Train logistic regression, run daily backtest, compute robust metrics."""

from pathlib import Path
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

TOP_N = 5                # target number of picks per day
COST_BPS_RT = 10         # round-trip trading cost in bps
TRAIN_Q = 0.80           # 80% time split
DATA_DIR = Path("data/clean")
OUT_EQUITY = DATA_DIR / "equity_curve.csv"
OUT_SECTOR = DATA_DIR / "sector_stats.csv"
OUT_SECTOR_DAILY = DATA_DIR / "sector_daily_returns.csv"


def main():
    df = pd.read_parquet(DATA_DIR / "features.parquet").sort_values("date").copy()
    df["date"] = pd.to_datetime(df["date"])

    # One-hot encode sector for the model
    sector_dum = pd.get_dummies(df["sector"], prefix="sector", drop_first=True)
    X = pd.concat([df[["headline_cnt", "sent_mean", "sent_max"]], sector_dum], axis=1).fillna(0.0)
    y = df["label"].astype(int)

    # Chronological split
    split_date = df["date"].quantile(TRAIN_Q)
    train_mask = df["date"] <= split_date
    test_mask  = df["date"] >  split_date

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]
    test = df[test_mask].copy()

    # Scale features (optional but fine)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # Train logistic regression
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_s, y_train)

    # Eval
    acc = accuracy_score(y_test, clf.predict(X_test_s))
    print(f"Test accuracy: {acc:.3f}  |  Train:{train_mask.sum()} Test:{test_mask.sum()} rows")

    # Predict probs
    test["p_up"] = clf.predict_proba(X_test_s)[:, 1]

    # Backtest parameters
    cost = COST_BPS_RT / 10000.0

    # Daily portfolio returns (+ keep picked tickers for diagnostics)
    daily_rows, picks_rows = [], []
    for d, g in test.groupby("date", sort=True):
        if g.empty:
            daily_rows.append({"date": d, "ret": 0.0, "selected_tickers": ""})
            continue

        k = min(TOP_N, len(g))
        top = g.nlargest(k, "p_up")

        gross = top["fwd_ret"].mean()
        net = gross - cost
        daily_rows.append({
            "date": d,
            "ret": float(net),
            "selected_tickers": ",".join(top["ticker"].tolist())
        })

        # Store per-pick for sector daily returns
        for _, r in top.iterrows():
            picks_rows.append({"date": d, "ticker": r["ticker"], "sector": r["sector"], "ret": float(r["fwd_ret"] - cost)})

    daily_df = pd.DataFrame(daily_rows)
    cal = pd.DataFrame({"date": pd.bdate_range(test["date"].min(), test["date"].max())})
    equity_df = cal.merge(daily_df, on="date", how="left").fillna({"ret": 0.0, "selected_tickers": ""})
    equity_df["equity"] = (1.0 + equity_df["ret"]).cumprod()
    equity_df["cum_ret"] = equity_df["equity"] - 1.0

    # Portfolio metrics
    pm = compute_daily_metrics(equity_df["ret"])
    print("\n=== Portfolio Metrics (daily-based) ===")
    print(f"Days: {pm['days']}  |  Non-zero days: {pm['non_zero_days']}")
    print(f"Annualized Return (arith): {pm['ann_return_arith']:.2%}" if pd.notna(pm['ann_return_arith']) else "Annualized Return (arith): n/a")
    print(f"Annualized Return (geom):  {pm['ann_return_geom']:.2%}"  if pd.notna(pm['ann_return_geom'])  else "Annualized Return (geom): n/a")
    print(f"Annualized Volatility:     {pm['ann_vol']:.2%}"          if pd.notna(pm['ann_vol'])          else "Annualized Volatility: n/a")
    print(f"Sharpe Ratio:              {pm['sharpe']:.2f}"           if pd.notna(pm['sharpe'])           else "Sharpe Ratio: n/a")
    print(f"Max Drawdown:              {pm['max_drawdown']:.2%}"     if pd.notna(pm['max_drawdown'])     else "Max Drawdown: n/a")

    # Sector metrics (daily with zeros)
    sector_stats_rows = []
    if picks_rows:
        picked_df = pd.DataFrame(picks_rows)
        sec_daily = (picked_df.groupby(["date","sector"], as_index=False)["ret"]
                     .mean().rename(columns={"ret":"sec_ret"}))
        all_days = pd.bdate_range(equity_df["date"].min(), equity_df["date"].max())
        sectors = sorted(sec_daily["sector"].dropna().unique().tolist())
        grid = pd.MultiIndex.from_product([all_days, sectors], names=["date","sector"])
        sec_df = (pd.DataFrame(index=grid).reset_index()
                    .merge(sec_daily, on=["date","sector"], how="left")
                    .fillna({"sec_ret": 0.0}))
        for s, g in sec_df.groupby("sector"):
            m = compute_daily_metrics(g["sec_ret"])
            m["sector"] = s
            sector_stats_rows.append(m)
    sector_stats = (pd.DataFrame(sector_stats_rows)
                    .sort_values("sharpe", ascending=False)
                    .reset_index(drop=True))
    # Optional stability filter
    sector_stats = sector_stats[sector_stats["days"] >= 60].reset_index(drop=True)

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    equity_df.to_csv(OUT_EQUITY, index=False)
    sector_stats.to_csv(OUT_SECTOR, index=False)
    if picks_rows:
        sec_df = sec_df.sort_values(["date", "sector"]).reset_index(drop=True)
        sec_df.to_csv(OUT_SECTOR_DAILY, index=False)

    print(f"\nSaved:\n- {OUT_EQUITY}\n- {OUT_SECTOR}")
    if picks_rows:
        print(f"- {OUT_SECTOR_DAILY}")
if __name__ == "__main__":
    main()
