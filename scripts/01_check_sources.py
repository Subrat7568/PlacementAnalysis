"""
01_check_sources.py
--------------------
Checks how many raw data source files exist in data/raw/ and whether they
need to be merged (e.g. on a shared key like student_id). If there is only
one source file, this is a no-op and simply loads + profiles it.

Run from the project root:
    python scripts/01_check_sources.py
"""
import glob
import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")) +
               glob.glob(os.path.join(RAW_DIR, "*.xls*")))
print("Source files found:", [os.path.basename(f) for f in files])

frames = {os.path.basename(f): pd.read_csv(f) for f in files}
for name, d in frames.items():
    print(f"\n{name}: shape={d.shape}")
    if "student_id" in d.columns:
        print("  unique student_id:", d["student_id"].nunique(),
              "| duplicated ids:", d["student_id"].duplicated().sum())

if len(frames) == 1:
    print("\nOnly ONE source file -> no merge/join needed.")
    df = next(iter(frames.values()))
else:
    dfs = list(frames.values())
    df = dfs[0]
    for d in dfs[1:]:
        df = df.merge(d, on="student_id", how="outer", validate="one_to_one")

print("\nResulting table shape:", df.shape)
print(df.head())
