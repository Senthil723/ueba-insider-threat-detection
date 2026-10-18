# explain.py - turn the numbers behind each alert into plain-language reasons
import pandas as pd
from pathlib import Path

OUT_DIR = Path(r"D:\ueba-data\output")

Z_MIN = 2.0          # mention a signal only if its z-score is at least this
LOW_CONF_DAYS = 30   # fewer earlier active days than this = low confidence

base = pd.read_csv(OUT_DIR / "features_baseline.csv", parse_dates=["day"])
alerts = pd.read_csv(OUT_DIR / "alerts_users.csv", parse_dates=["day"])

# "Usual" = average of the user's EARLIER days (today is left out)
base = base.sort_values(["user", "day"]).reset_index(drop=True)
g = base.groupby("user")
for col in ["first_logon", "usb_connects", "files_copied"]:
    base[f"usual_{col}"] = g[col].transform(lambda s: s.shift(1).expanding().mean())

keep = ["user", "day", "first_logon", "first_logon_z", "usb_connects", "usb_connects_z",
        "files_copied", "files_copied_z", "first_usb_use", "past_days",
        "usual_first_logon", "usual_usb_connects", "usual_files_copied"]
rows = alerts.merge(base[keep], on=["user", "day"], how="left")


def hhmm(x):
    """7.75 -> '07:45'"""
    h = int(x)
    m = int(round((x - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return f"{h:02d}:{m:02d}"


def explain(r):
    reasons, checks, mitre = [], [], []

    if r["first_usb_use"] == 1:
        reasons.append(f"first USB use after {int(r['past_days'])} earlier active days with none")
        checks.append("is the USB device approved, and what was copied?")
        mitre.append("T1052.001")
    if r["usb_connects_z"] >= Z_MIN:
        reasons.append(f"{int(r['usb_connects'])} USB connects vs usual "
                       f"{r['usual_usb_connects']:.1f} per day")
        checks.append("was there a project or migration that explains the USB use?")
        mitre.append("T1052.001")
    if r["files_copied_z"] >= Z_MIN:
        reasons.append(f"{int(r['files_copied'])} files copied to USB vs usual "
                       f"{r['usual_files_copied']:.1f} per day")
        checks.append("what file types were copied, and are they work-related?")
        mitre.append("T1052.001")
    if abs(r["first_logon_z"]) >= Z_MIN:          # NaN gives False, so it is skipped
        reasons.append(f"first logon at {hhmm(r['first_logon'])} vs usual "
                       f"{hhmm(r['usual_first_logon'])}")
        checks.append("was this an approved overnight task? which PC was used?")
        mitre.append("T1078")
    if not reasons:
        reasons.append("moderate deviation across several signals")
        checks.append("review the user's activity timeline for that day")

    conf = "low" if r["past_days"] < LOW_CONF_DAYS else "normal"
    return pd.Series({
        "reasons": "; ".join(reasons),
        "checks": " | ".join(dict.fromkeys(checks)),     # drop repeated checks
        "mitre": ", ".join(dict.fromkeys(mitre)) or "none",
        "confidence": conf,
    })


rows = pd.concat([rows, rows.apply(explain, axis=1)], axis=1)
rows.to_csv(OUT_DIR / "alerts_explained.csv", index=False)   # has user IDs: stays local

# Print the top 10 WITHOUT user IDs or dates
for _, r in rows.head(10).iterrows():
    print(f"#{int(r['rank'])}  score {r['anomaly_score']:.3f}  |  {r['confidence']} confidence")
    print("   why  :", r["reasons"])
    print("   MITRE:", r["mitre"])
    print("   check:", r["checks"])
    print()

print("low-confidence alerts in the top 50:", int((rows.head(50)["confidence"] == "low").sum()))
print("saved to", OUT_DIR / "alerts_explained.csv")