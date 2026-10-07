"""
04_analysis.py
---------------
Core findings used in the dashboard and report:
  1. Average package by branch
  2. Hiring frequency by company type
  3. Placement rate by college tier (substitute for a year-over-year trend,
     since the dataset has no date/year column)

Run from the project root:
    python scripts/04_analysis.py
"""
import os
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "processed",
                     "student_placement_cleaned.csv")

d = pd.read_csv(DATA)

print("=== Overview ===")
print("Total students:", len(d))
print("Placed:", (d.placed == 1).sum(), f"({(d.placed==1).mean()*100:.1f}%)")
print("Average package (placed, LPA):", round(d.salary_lpa.mean(), 2))

print("\n=== (1) Average package by branch ===")
t1 = (d[d.placed == 1].groupby("branch")["salary_lpa"]
      .agg(avg_package_lpa="mean", placed_count="count")
      .round(2).sort_values("avg_package_lpa", ascending=False))
print(t1)

print("\n=== (2) Students hired by company type ===")
t2 = d[d.placed == 1]["company_type"].value_counts()
print(t2)

print("\n=== (3) Placement rate by college tier ===")
t3 = (d.groupby("college_tier")["placed"].mean() * 100).round(2)
print(t3)
