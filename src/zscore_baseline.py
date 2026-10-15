# zscore_baseline.py - per-user z-scores with NO machine learning model
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score

OUT_DIR = Path(r"D:\ueba-data\output")
ANSWERS = Path(r"D:\ueba-data\answers\insiders.csv")

# features_scored.csv already holds the version 1 z-scores
# (USB and file z-scores clipped at 0, 10-day minimum history)
feat = pd.read_csv(OUT_DIR / "features_scored.csv", parse_dates=["day"])

# The three signals, all "bigger = more unusual"
logon_dev = feat["first_logon_z"].abs()      # too early AND too late both count
usb_dev = feat["usb_connects_z"]
file_dev = feat["files_copied_z"]

# Two daily scores, fixed before running
feat["score_max"] = pd.concat([logon_dev, usb_dev, file_dev], axis=1).max(axis=1)
feat["score_sum"] = logon_dev + usb_dev + file_dev

# User score = the user's single highest day (same rule as the Isolation Forest)
users = feat.groupby("user").agg(
    zmax=("score_max", "max"),
    zsum=("score_sum", "max"),
).reset_index()

# Isolation Forest version 1 score, for side-by-side comparison
v1 = pd.read_csv(OUT_DIR / "alerts_users.csv")[["user", "anomaly_score"]]
users = users.merge(v1, on="user", how="left")

# Answer key (used only to score the rankings)
key = pd.read_csv(ANSWERS)
key = key[key["dataset"] == 4.2][["user"]].assign(is_insider=1)
users = users.merge(key, on="user", how="left").fillna({"is_insider": 0})
users["is_insider"] = users["is_insider"].astype(int)

# Random tie-break with a fixed seed
users["tie"] = np.random.default_rng(42).random(len(users))

n, n_ins = len(users), int(users["is_insider"].sum())
print("users:", n, "| insiders:", n_ins)
print()

methods = [
    ("Isolation Forest v1", "anomaly_score"),
    ("z-score only: max of 3 signals", "zmax"),
    ("z-score only: sum of 3 signals", "zsum"),
]

print(f"{'method':<34}{'top10':>6}{'top25':>6}{'top50':>6}{'top100':>7}{'AUC':>8}")
for name, col in methods:
    ranked = users.sort_values([col, "tie"], ascending=False)
    found = [int(ranked.head(k)["is_insider"].sum()) for k in (10, 25, 50, 100)]
    auc = roc_auc_score(users["is_insider"], users[col])
    print(f"{name:<34}{found[0]:>6}{found[1]:>6}{found[2]:>6}{found[3]:>7}{auc:>8.3f}")

print()
print("random picking would find:",
      [round(k * n_ins / n, 1) for k in (10, 25, 50, 100)])