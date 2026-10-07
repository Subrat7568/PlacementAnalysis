import os
import pandas as pd, numpy as np

SRC = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "student_placement_salary_elite_v2.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "student_placement_cleaned.csv")

df = pd.read_csv(SRC)

# 1. Unplaced students: salary 0 -> NaN (0 means "no offer", not a real salary)
assert (df.loc[df.placed == 0, "salary_lpa"] == 0).all()
df.loc[df.placed == 0, "salary_lpa"] = np.nan

# 1b. Unplaced students: blank company_type / job_role -> "Not placed" (easier group-bys)
#     salary_lpa stays NaN on purpose. Both columns are post-placement, so they are
#     never used as model features for `placed`.
assert df.loc[df.placed == 0, ["company_type", "job_role"]].isna().all().all()
assert df.loc[df.placed == 1, ["company_type", "job_role"]].notna().all().all()
df[["company_type", "job_role"]] = df[["company_type", "job_role"]].fillna("Not placed")

# 1c. Branch -> consistent full names (abbreviations and short names mixed in raw data)
BRANCH_MAP = {
    "CSE": "Computer Science and Engineering",
    "IT": "Information Technology",
    "ECE": "Electronics and Communication Engineering",
    "EEE": "Electrical and Electronics Engineering",
    "Civil": "Civil Engineering",
    "Mechanical": "Mechanical Engineering",
}
df["branch"] = df["branch"].str.strip()
assert set(df["branch"]) <= set(BRANCH_MAP), set(df["branch"]) - set(BRANCH_MAP)
df["branch"] = df["branch"].map(BRANCH_MAP)

# 1d. Salary: numeric LPA float, 2 decimals (already numeric in raw data; NaN for unplaced)
df["salary_lpa"] = pd.to_numeric(df["salary_lpa"], errors="raise").round(2)

# 1e. Duplicates: exact and ignoring student_id (0 found in audit; enforced here)
n0 = len(df)
df = df.drop_duplicates(subset=[c for c in df.columns if c != "student_id"]).drop_duplicates(subset="student_id")
print("Duplicate rows removed:", n0 - len(df))

# 2. resume_score > 100: keep raw, add capped version + flag
df["resume_score_raw"] = df["resume_score"]
df["resume_over_100"] = (df["resume_score_raw"] > 100).astype(int)
df["resume_score"] = df["resume_score_raw"].clip(upper=100)

# 3. skill_score is exactly the sum of the 4 skill flags -> redundant, drop
skills = ["python_skill", "dsa_skill", "ml_skill", "web_dev_skill"]
assert (df[skills].sum(axis=1) == df["skill_score"]).all()
df = df.drop(columns="skill_score")

# 4. Types: flags/categoricals
for c in skills + ["placed", "resume_over_100"]:
    df[c] = df[c].astype("int8")
df["college_tier"] = pd.Categorical(df["college_tier"], categories=[1, 2, 3], ordered=True)
for c in ["branch", "company_type", "job_role"]:
    df[c] = df[c].astype("category")

df.to_csv(OUT, index=False)

# ---- Feature set for predicting `placed` (no post-placement leakage) ----
LEAKY = ["company_type", "job_role", "salary_lpa"]
DROP_FOR_MODEL = LEAKY + ["student_id", "placed", "resume_score_raw"]
feature_cols = [c for c in df.columns if c not in DROP_FOR_MODEL]
print("Saved:", OUT, df.shape)
print("Model features for `placed`:", feature_cols)
