# explore.py - first look at the CERT r4.2 logs
import pandas as pd
from pathlib import Path

# Folder where we extracted the data (outside the GitHub project)
DATA_DIR = Path(r"D:\ueba-data\r4.2")

# The three logs that match our scope
FILES = ["logon.csv", "device.csv", "file.csv"]

for name in FILES:
    df = pd.read_csv(DATA_DIR / name)

    print("=" * 60)
    print("FILE:", name)
    print("rows, columns:", df.shape)       # how big is it?
    print("columns:", list(df.columns))     # what information does it hold?

    # Show the first 3 rows. file.csv has a long text column called
    # "content", so we hide it to keep the output readable.
    print(df.head(3).drop(columns=["content"], errors="ignore").to_string())

    print("missing values per column:")
    print(df.isna().sum())