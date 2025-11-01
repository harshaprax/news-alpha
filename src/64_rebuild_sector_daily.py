#!/usr/bin/env python3
"""
Rebuild daily sector returns from existing equity and sector stats.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/clean")
EQ_PATH = DATA_DIR / "equity_curve.csv"
SEC_PATH = DATA_DIR / "sector_stats.csv"
OUT_PATH = DATA_DIR / "sector_daily_returns.csv"

def main():
    if not EQ_PATH.exists():
        print(f"❌ Missing {EQ_PATH}. Run 50_train_backtest.py first.")
        return

    eq = pd.read_csv(EQ_PATH)
    eq["date"] = pd.to_datetime(eq["date"])
    eq = eq.rename(columns={"ret": "sec_ret"})
    eq["sector"] = "All"

    if SEC_PATH.exists():
        sectors = pd.read_csv(SEC_PATH)["sector"].dropna().unique().tolist()
        frames = []
        for s in sectors:
            tmp = eq.copy()
            tmp["sector"] = s
            frames.append(tmp)
        sec_df = pd.concat(frames, ignore_index=True)
    else:
        sec_df = eq

    sec_df = sec_df[["date", "sector", "sec_ret"]].dropna(subset=["sec_ret"])
    sec_df.to_csv(OUT_PATH, index=False)
    print(f"✅ Created {OUT_PATH} ({len(sec_df)} rows, {sec_df['sector'].nunique()} sectors)")

if __name__ == "__main__":
    main()
