# naive_baseline.py - simple global rules to compare with the Isolation Forest
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score

OUT_DIR = Path(r"D:\ueba-data\output")
ANSWERS = Path(r"D:\ueba-data\answers\insiders.csv")

feat = pd.read_csv(OUT_DIR / "features_daily.csv", parse_dates=["day"])
key = pd.read_csv(ANSWERS)
key = key[key["dataset"] == 4.2][["user"]].assign(is_insider=1)

# One row per user, three crude global scores (no per-user baseline)
users = feat.groupby("user").agg(
    total_files=("files_copied", "sum"),
    total_usb=("usb_connects", "sum"),
).reset_index()

# Fixed after-hours rule: first logon before 06:00 or at/after 18:00
odd = feat[(feat["first_logon"] < 6) | (feat["first_logon"] >= 18)]
odd = odd.groupby("user").size().reset_index(name="odd_hour_days")
users = users.merge(odd, on="user", how="left").fillna({"odd_hour_days": 0})

users = users.merge(key, on="user", how="left").fillna({"is_insider": 0})
users["is_insider"] = users["is_insider"].astype(int)

# Version 1 Isolation Forest ranking, for side-by-side comparison
v1 = pd.read_csv(OUT_DIR / "alerts_users.csv")[["user", "anomaly_score"]]
users = users.merge(v1, on="user", how="left")

# Random tie-break so equal scores do not get an arbitrary but fixed order
rng = np.random.default_rng(42)
users["tie"] = rng.random(len(users))

n, n_ins = len(users), int(users["is_insider"].sum())
print("users:", n, "| insiders:", n_ins)
print()

methods = [
    ("Isolation Forest v1", "anomaly_score"),
    ("naive: total files copied", "total_files"),
    ("naive: total USB connects", "total_usb"),
    ("naive: odd-hour first logons", "odd_hour_days"),
]

print(f"{'method':<30}{'top10':>6}{'top25':>6}{'top50':>6}{'top100':>7}{'AUC':>8}")
for name, col in methods:
    ranked = users.sort_values([col, "tie"], ascending=False)
    found = [int(ranked.head(k)["is_insider"].sum()) for k in (10, 25, 50, 100)]
    auc = roc_auc_score(users["is_insider"], users[col])
    print(f"{name:<30}{found[0]:>6}{found[1]:>6}{found[2]:>6}{found[3]:>7}{auc:>8.3f}")

print()
print("random picking would find:",
      [round(k * n_ins / n, 1) for k in (10, 25, 50, 100)])