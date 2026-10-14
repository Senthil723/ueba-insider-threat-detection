# check_answers.py - count the r4.2 insiders per scenario (counts only)
import pandas as pd
from pathlib import Path

ANSWERS = Path(r"D:\ueba-data\answers\insiders.csv")

df = pd.read_csv(ANSWERS)
print("columns:", list(df.columns))
print("rows in file (all releases):", len(df))

# Keep only the r4.2 release
r42 = df[df["dataset"] == 4.2]
print("rows for r4.2:", len(r42))
print("distinct r4.2 insider users:", r42["user"].nunique())

print()
print("r4.2 insiders per scenario:")
print(r42["scenario"].value_counts().sort_index())