# baseline.py - compare each user-day with that user's OWN earlier days
import numpy as np
import pandas as pd
from pathlib import Path

OUT_DIR = Path(r"D:\ueba-data\output")

feat = pd.read_csv(OUT_DIR / "features_daily.csv", parse_dates=["day"])
feat = feat.sort_values(["user", "day"]).reset_index(drop=True)

MIN_HISTORY = 10   # need at least 10 earlier active days before judging a day

g = feat.groupby("user")
feat["past_days"] = g.cumcount()   # 0 for a user's first day, 1 for the second, ...


def past_stat(col, how):
    """Mean or std of this user's EARLIER days. shift(1) leaves today out."""
    return g[col].transform(lambda s: getattr(s.shift(1).expanding(), how)())


# (column, smallest spread we allow). The floor stops a tiny spread
# in a short history from producing huge z-scores.
SETTINGS = [("first_logon", 0.5), ("usb_connects", 1.0), ("files_copied", 1.0)]

z_cols = []
for col, floor in SETTINGS:
    mean = past_stat(col, "mean")
    std = past_stat(col, "std").fillna(0).clip(lower=floor)
    z = (feat[col] - mean) / std
    z[feat["past_days"] < MIN_HISTORY] = np.nan    # not enough history yet
    feat[f"{col}_z"] = z
    z_cols.append(f"{col}_z")

# First-ever USB use, after the user already had enough history without any USB
usb_before = g["usb_connects"].transform(lambda s: s.shift(1).fillna(0).cumsum())
feat["first_usb_use"] = (
    (feat["usb_connects"] > 0) & (usb_before == 0) & (feat["past_days"] >= MIN_HISTORY)
).astype(int)

# --- Check our own work ---
print("user-days:", len(feat))
print("user-days with enough history:", (feat["past_days"] >= MIN_HISTORY).sum())
first = feat[feat["first_usb_use"] == 1]
print("first-time USB days:", len(first), "| users:", first["user"].nunique())
print()
print(feat[z_cols].describe(percentiles=[0.5, 0.9, 0.99]).T)
print()
for c in z_cols:
    print(c, "- days with |z| > 3:", (feat[c].abs() > 3).sum())

feat.to_csv(OUT_DIR / "features_baseline.csv", index=False)
print("saved to", OUT_DIR / "features_baseline.csv")