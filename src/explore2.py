# explore2.py - dates, users, and activity types
import pandas as pd
from pathlib import Path

DATA_DIR = Path(r"D:\ueba-data\r4.2")

# usecols loads only the columns we need (skips the big "content" column)
logon = pd.read_csv(DATA_DIR / "logon.csv", usecols=["date", "user", "pc", "activity"])
device = pd.read_csv(DATA_DIR / "device.csv", usecols=["date", "user", "pc", "activity"])
files = pd.read_csv(DATA_DIR / "file.csv", usecols=["date", "user", "pc", "filename"])

# --- 1. Is the date day/month or month/day? ---
parts = logon["date"].str.slice(0, 5).str.split("/", expand=True).astype(int)
print("largest first number :", parts[0].max())
print("largest second number:", parts[1].max())

# A day can reach 31 but a month never passes 12
if parts[0].max() > 12:
    fmt = "%d/%m/%Y %H:%M:%S"   # first number is the day
else:
    fmt = "%m/%d/%Y %H:%M:%S"   # first number is the month
print("format chosen:", fmt)

# --- 2. Convert text to real dates and summarise each log ---
for name, df in [("logon", logon), ("device", device), ("file", files)]:
    df["date"] = pd.to_datetime(df["date"], format=fmt)
    print(
        name,
        "| from", df["date"].min(),
        "| to", df["date"].max(),
        "| users:", df["user"].nunique(),
        "| PCs:", df["pc"].nunique(),
    )

# --- 3. Activity types and counts ---
print()
print(logon["activity"].value_counts())
print()
print(device["activity"].value_counts())

# --- 4. Logons by hour of day ---
print()
print("Logons by hour of day:")
only_logons = logon[logon["activity"] == "Logon"]
print(only_logons["date"].dt.hour.value_counts().sort_index())