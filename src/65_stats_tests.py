from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# Shared data directory convention
DATA_DIR = Path("data/clean")
DATA_DIR.mkdir(parents=True, exist_ok=True)

IN = DATA_DIR / "sector_daily_returns.csv"
OUT_TTEST = {
    "daily": DATA_DIR / "sector_ttest.csv",
    "weekly": DATA_DIR / "sector_ttest_weekly.csv",
}
OUT_PAIRWISE = {
    "daily": DATA_DIR / "sector_pairwise_best_vs_rest.csv",
    "weekly": DATA_DIR / "sector_pairwise_best_vs_rest_weekly.csv",
}

ANNUALIZE = {"daily": 252.0, "weekly": 52.0}


def bh_fdr(pvals: pd.Series) -> pd.Series:
    """Benjamini-Hochberg FDR correction (two-sided)."""
    if pvals.empty:
        return pd.Series(dtype=float)
    p = pvals.values.astype(float)
    n = len(p)
    order = np.argsort(p)
    ranked = np.empty(n)
    ranked[order] = np.arange(1, n + 1)
    q = p * n / ranked
    q_sorted = np.minimum.accumulate(np.sort(q)[::-1])[::-1]
    q_adj = np.empty(n)
    q_adj[order] = q_sorted
    return pd.Series(np.clip(q_adj, 0, 1), index=pvals.index)


def one_sample_tstats(x: pd.Series) -> dict:
    """Test mean(x) != 0; return mean, std, n, t, p, CI95."""
    r = pd.to_numeric(x, errors="coerce").fillna(0.0).astype(float)
    n = len(r)
    mu = r.mean()
    sd = r.std(ddof=1)
    if n < 2 or sd == 0:
        return dict(n=n, mean=mu, std=sd, t=np.nan, p=np.nan, ci_lo=np.nan, ci_hi=np.nan)
    se = sd / np.sqrt(n)
    t = mu / se
    p = 2 * stats.t.sf(np.abs(t), df=n - 1)
    q = stats.t.ppf(0.975, df=n - 1)
    ci_lo, ci_hi = mu - q * se, mu + q * se
    return dict(n=n, mean=mu, std=sd, t=t, p=p, ci_lo=ci_lo, ci_hi=ci_hi)


def two_sample_tstats(a: pd.Series, b: pd.Series):
    """Welch's t-test for mean(a) != mean(b)."""
    a = pd.to_numeric(a, errors="coerce").fillna(0.0).astype(float)
    b = pd.to_numeric(b, errors="coerce").fillna(0.0).astype(float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return t, p, a.mean(), b.mean(), len(a), len(b)


def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Compound daily returns into weekly simple returns (Friday close)."""
    weekly = (
        df.set_index("date")
        .groupby("sector")["sec_ret"]
        .resample("W-FRI")
        .apply(lambda r: (1.0 + r).prod() - 1.0)
        .reset_index()
    )
    weekly["date"] = pd.to_datetime(weekly["date"])
    return weekly


def run_one_sample_tests(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    rows = []
    for sector, group in df.groupby("sector"):
        res = one_sample_tstats(group["sec_ret"])
        res["sector"] = sector
        rows.append(res)
    if not rows:
        return pd.DataFrame()
    tt = pd.DataFrame(rows).set_index("sector")
    tt["p_fdr"] = bh_fdr(tt["p"])
    ann_factor = ANNUALIZE[freq]
    tt["ann_mean_arith"] = tt["mean"] * ann_factor
    tt["ann_ci_lo"] = tt["ci_lo"] * ann_factor
    tt["ann_ci_hi"] = tt["ci_hi"] * ann_factor
    tt = tt.reset_index().sort_values("p_fdr")
    tt.to_csv(OUT_TTEST[freq], index=False)
    print(f"Saved per-sector {freq} t-tests -> {OUT_TTEST[freq]}")
    return tt


def run_pairwise_tests(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    means = df.groupby("sector")["sec_ret"].mean().sort_values(ascending=False)
    if len(means) < 2:
        print(f"Not enough sectors for pairwise {freq} tests.")
        return pd.DataFrame()

    best = means.index[0]
    best_returns = df.loc[df["sector"] == best, "sec_ret"]
    rows = []
    for sector in means.index[1:]:
        other_returns = df.loc[df["sector"] == sector, "sec_ret"]
        t, p, mean_best, mean_other, n_best, n_other = two_sample_tstats(best_returns, other_returns)
        rows.append(
            {
                "best": best,
                "other": sector,
                "t": t,
                "p": p,
                "mean_best": mean_best,
                "mean_other": mean_other,
                "n_best": n_best,
                "n_other": n_other,
            }
        )
    if not rows:
        return pd.DataFrame()
    pw = pd.DataFrame(rows)
    pw["p_fdr"] = bh_fdr(pw["p"])
    ann_factor = ANNUALIZE[freq]
    pw["ann_mean_best"] = pw["mean_best"] * ann_factor
    pw["ann_mean_other"] = pw["mean_other"] * ann_factor
    pw = pw.sort_values("p_fdr")
    pw.to_csv(OUT_PAIRWISE[freq], index=False)
    print(f"Saved pairwise best-vs-rest {freq} tests -> {OUT_PAIRWISE[freq]}")
    return pw


def format_console(tt: pd.DataFrame) -> pd.DataFrame:
    show = tt[["sector", "n", "mean", "t", "p", "p_fdr", "ann_mean_arith", "ann_ci_lo", "ann_ci_hi"]].copy()
    show["mean"] = show["mean"].map(lambda x: f"{x:.4%}")
    show["ann_mean_arith"] = show["ann_mean_arith"].map(lambda x: f"{x:.2%}")
    show["ann_ci_lo"] = show["ann_ci_lo"].map(lambda x: f"{x:.2%}")
    show["ann_ci_hi"] = show["ann_ci_hi"].map(lambda x: f"{x:.2%}")
    return show


def main():
    if not IN.exists():
        print(f"Missing {IN}. Run src/50_train_backtest.py first.")
        return

    df = pd.read_csv(IN, parse_dates=["date"]).sort_values(["date", "sector"])

    datasets = {
        "daily": df,
        "weekly": aggregate_weekly(df),
    }

    console_tables = {}
    for freq, freq_df in datasets.items():
        if freq_df.empty:
            print(f"No data for {freq} frequency; skipping.")
            continue
        tt = run_one_sample_tests(freq_df, freq)
        if not tt.empty:
            console_tables[freq] = format_console(tt)
        run_pairwise_tests(freq_df, freq)

    for freq, table in console_tables.items():
        print(f"\nPer-sector one-sample t-tests vs 0 ({freq} returns):")
        print(table.to_string(index=False))


if __name__ == "__main__":
    main()
