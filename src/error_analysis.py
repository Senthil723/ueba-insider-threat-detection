# error_analysis.py - why were some non-insiders ranked high? (no user IDs printed)
import pandas as pd
from pathlib import Path

OUT_DIR = Path(r"D:\ueba-data\output")
ANSWERS = Path(r"D:\ueba-data\answers\insiders.csv")

alerts = pd.read_csv(OUT_DIR / "alerts_users.csv", parse_dates=["day"])
scored = pd.read_csv(OUT_DIR / "features_scored.csv", parse_dates=["day"])
key = pd.read_csv(ANSWERS)
key = key[key["dataset"] == 4.2][["user", "scenario"]]

alerts = alerts.merge(key, on="user", how="left")
alerts["is_insider"] = alerts["scenario"].notna()

# --- Part 1: non-insiders inside the top 50 (false positives) ---
fp = alerts.head(50)
fp = fp[~fp["is_insider"]][["user", "day", "rank", "anomaly_score", "top_signal"]]
print("non-insiders in top 50:", len(fp))

# What is each user's normal, over all their scored days? (context only)
typical = scored.groupby("user").agg(
    typical_first_logon=("first_logon", "median"),
    typical_usb_per_day=("usb_connects", "mean"),
    typical_files_per_day=("files_copied", "mean"),
    days_scored=("day", "size"),
).reset_index()

# The flagged day itself
day_cols = ["user", "day", "first_logon", "first_logon_z", "usb_connects",
            "usb_connects_z", "files_copied", "files_copied_z",
            "first_usb_use", "past_days"]
detail = fp.merge(scored[day_cols], on=["user", "day"]).merge(typical, on="user")
detail.index = [f"FP-{i + 1}" for i in range(len(detail))]
print()
print(detail.drop(columns=["user", "day"]).round(2).T.to_string())

# --- Part 2: where did the scenario 3 insiders rank? (ranks, no IDs) ---
s3 = alerts[alerts["scenario"] == 3]
print()
print("scenario 3 ranks:", sorted(s3["rank"].tolist()))
print("scenario 3 main signal on their top day:")
print(s3["top_signal"].value_counts().to_string())