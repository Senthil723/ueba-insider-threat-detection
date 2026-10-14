# evaluate.py - compare the ranked users with the answer key (counts only)
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score

OUT_DIR = Path(r"D:\ueba-data\output")
ANSWERS = Path(r"D:\ueba-data\answers\insiders.csv")

alerts = pd.read_csv(OUT_DIR / "alerts_users.csv")    # already sorted by rank
key = pd.read_csv(ANSWERS)
key = key[key["dataset"] == 4.2][["user", "scenario"]]

# Mark which ranked users are true insiders
alerts = alerts.merge(key, on="user", how="left")
alerts["is_insider"] = alerts["scenario"].notna().astype(int)

n_users = len(alerts)
n_insiders = int(alerts["is_insider"].sum())
print("users ranked:", n_users, "| insiders among them:", n_insiders)
print()

# --- Precision and recall at the top of the queue ---
# precision = what share of the top-k alerts are real insiders
# recall    = what share of all insiders appear in the top-k
for k in [10, 25, 50, 100, 200]:
    found = int(alerts.head(k)["is_insider"].sum())
    random_found = k * n_insiders / n_users
    print(f"top {k:>3}: found {found:>2} | precision {found / k:.2f} "
          f"| recall {found / n_insiders:.2f} | random picking finds {random_found:.1f}")

# --- One summary number: 0.5 = random, 1.0 = perfect ---
auc = roc_auc_score(alerts["is_insider"], alerts["anomaly_score"])
print()
print(f"ROC AUC: {auc:.3f}")

# --- How did each dataset scenario do? (a random user has median rank ~500) ---
print()
for s in sorted(key["scenario"].unique()):
    sub = alerts[alerts["scenario"] == s]
    print(f"scenario {s}: insiders {len(sub)} | in top 100: "
          f"{int((sub['rank'] <= 100).sum())} | median rank {sub['rank'].median():.0f}")

# --- False-positive view: what drove the top 50, split by insider or not ---
print()
print("Top 50 by main signal (0 = not an insider, 1 = insider):")
print(alerts.head(50).groupby(["top_signal", "is_insider"]).size().unstack(fill_value=0))