from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
df = pd.read_csv(DATA_DIR / "sector_ttest_weekly.csv")
print(df)
