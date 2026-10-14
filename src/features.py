# features.py - build one row per user per day from the three logs
import pandas as pd
from pathlib import Path

DATA_DIR = Path(r"D:\ueba-data\r4.2")
OUT_DIR = Path(r"D:\ueba-data\output")      # outside the GitHub repo
OUT_DIR.mkdir(exist_ok=True)

FMT = "%m/%d/%Y %H:%M:%S"                   # confirmed month/day/year


def load(name, cols):
    """Read one log and add 'day' and 'hour_frac' columns."""
    df = pd.read_csv(DATA_DIR / name, usecols=cols)
    df["date"] = pd.to_datetime(df["date"], format=FMT)
    df["day"] = df["date"].dt.normalize()                       # midnight of that day
    df["hour_frac"] = df["date"].dt.hour + df["date"].dt.minute / 60   # 7:30 -> 7.5
    return df


logon = load("logon.csv", ["date", "user", "pc", "activity"])
device = load("device.csv", ["date", "user", "activity"])
files = load("file.csv", ["date", "user"])

# --- Logon features per user per day ---
logon_on = logon[logon["activity"] == "Logon"]
f_logon = logon_on.groupby(["user", "day"]).agg(
    logon_count=("activity", "size"),      # how many logons that day
    first_logon=("hour_frac", "min"),      # earliest logon time
    last_logon=("hour_frac", "max"),       # latest logon time
    pcs_used=("pc", "nunique"),            # how many different PCs
).reset_index()

# --- USB features: count of Connect events per user per day ---
f_usb = (
    device[device["activity"] == "Connect"]
    .groupby(["user", "day"]).size().reset_index(name="usb_connects")
)

# --- File features: files copied to USB per user per day ---
f_file = files.groupby(["user", "day"]).size().reset_index(name="files_copied")

# --- Combine. 'outer' keeps a day even if a user appears in only one log ---
feat = (
    f_logon.merge(f_usb, on=["user", "day"], how="outer")
           .merge(f_file, on=["user", "day"], how="outer")
)
for col in ["logon_count", "pcs_used", "usb_connects", "files_copied"]:
    feat[col] = feat[col].fillna(0).astype(int)
feat = feat.sort_values(["user", "day"]).reset_index(drop=True)

# --- Check our own work ---
print("rows (user-days):", len(feat))
print("users:", feat["user"].nunique())
print("logon total check:", feat["logon_count"].sum(), "should equal", len(logon_on))
print("user-days with USB use:", (feat["usb_connects"] > 0).sum())
print()
print(feat.drop(columns=["user", "day"]).describe().T)

feat.to_csv(OUT_DIR / "features_daily.csv", index=False)
print("saved to", OUT_DIR / "features_daily.csv")