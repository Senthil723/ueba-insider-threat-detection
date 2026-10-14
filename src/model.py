# model.py - score every user-day with Isolation Forest, then rank users
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

OUT_DIR = Path(r"D:\ueba-data\output")
feat = pd.read_csv(OUT_DIR / "features_baseline.csv", parse_dates=["day"])

# Only score days where the user has enough earlier history
MIN_HISTORY = 10
feat = feat[feat["past_days"] >= MIN_HISTORY].copy()

# Only INCREASES in USB use and file copies matter for theft, so clip at 0.
# Logon time stays two-sided: too early and too late are both unusual.
feat["usb_connects_z"] = feat["usb_connects_z"].clip(lower=0)
feat["files_copied_z"] = feat["files_copied_z"].clip(lower=0)

MODEL_COLS = ["first_logon_z", "usb_connects_z", "files_copied_z", "first_usb_use"]

# The few days with no logon have no logon z-score: treat as "no deviation known"
print("missing z-scores filled with 0:", int(feat[MODEL_COLS].isna().sum().sum()))
feat[MODEL_COLS] = feat[MODEL_COLS].fillna(0)

# Fixed settings. They are written in docs/design-decisions.md and
# must NOT be tuned by looking at the answer key.
model = IsolationForest(
    n_estimators=200,        # number of random trees
    contamination="auto",    # let scikit-learn pick the internal threshold
    random_state=42,         # same result every run
    n_jobs=-1,               # use all CPU cores
)
model.fit(feat[MODEL_COLS])

# score_samples is HIGHER for normal days, so flip the sign:
# higher anomaly_score = more unusual
feat["anomaly_score"] = -model.score_samples(feat[MODEL_COLS])

# Which signal pushed the day the most? (seed of the "why flagged" text)
signals = feat[["first_logon_z", "usb_connects_z", "files_copied_z"]].abs()
feat["top_signal"] = signals.idxmax(axis=1)
feat.loc[feat["first_usb_use"] == 1, "top_signal"] = "first_usb_use"

# User risk = the user's single highest daily score (a design choice)
idx = feat.groupby("user")["anomaly_score"].idxmax()
alerts = (
    feat.loc[idx, ["user", "day", "anomaly_score", "top_signal"]]
    .sort_values("anomaly_score", ascending=False)
    .reset_index(drop=True)
)
alerts["rank"] = alerts.index + 1

print("user-days scored:", len(feat))
print("users ranked:", len(alerts))
print()
print("daily anomaly score percentiles:")
print(feat["anomaly_score"].describe(percentiles=[0.5, 0.9, 0.99, 0.999]))
print()
print("top 10 alerts (user IDs are in the saved file, not printed):")
print(alerts.head(10).drop(columns="user").to_string(index=False))

feat.to_csv(OUT_DIR / "features_scored.csv", index=False)
alerts.to_csv(OUT_DIR / "alerts_users.csv", index=False)
print("saved to", OUT_DIR)