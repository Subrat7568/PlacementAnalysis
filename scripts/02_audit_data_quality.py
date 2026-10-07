import os
import pandas as pd, numpy as np, re
pd.set_option("display.width", 200, "display.max_columns", None)
RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "student_placement_salary_elite_v2.csv")
df = pd.read_csv(RAW)
print("Columns:", list(df.columns))
print("Requested columns present?", {c: c in df.columns for c in ["Branch","Package","Placement_Date"]})
print("Case-insensitive matches:", [c for c in df.columns if c.lower() in ("branch","package","placement_date")])
print("Any date-like column?", [c for c in df.columns if re.search("date|year|month|time", c, re.I)])

print("\n=== (1) DUPLICATES ===")
print("Exact duplicate rows (all cols):", df.duplicated().sum())
print("Duplicate student_id:", df.student_id.duplicated().sum())
feat = df.drop(columns="student_id")
print("Duplicate rows ignoring student_id:", feat.duplicated().sum())
# near-duplicates: same values after rounding numerics
r = feat.copy()
for c in ["cgpa","coding_score","communication_score","aptitude_score","resume_score","salary_lpa"]:
    r[c] = (r[c]/ (1 if c=="cgpa" else 5)).round(0) if c!="salary_lpa" else (r[c]/5).round(0)
print("Near-duplicates (numerics bucketed, ignoring id):", r.duplicated().sum())
# near-dups on the profile columns only (excluding outcomes)
prof = ["cgpa","branch","college_tier","python_skill","dsa_skill","ml_skill","web_dev_skill","coding_score","communication_score","aptitude_score","internships","projects","backlogs"]
print("Duplicate on profile columns only:", df.duplicated(subset=prof).sum())
# rows matching on all but 1-2 fields (Hamming-style) among key columns
key = ["cgpa","branch","college_tier","coding_score","aptitude_score","communication_score","resume_score"]
print("Duplicate on 7 key cols:", df.duplicated(subset=key).sum())
k = df.groupby(["cgpa","branch"]).size()
print("Same cgpa+branch pairs (expected by chance):", (k>1).sum(), "groups; max group size", k.max())

print("\n=== (2) MISSING VALUES ===")
m = pd.DataFrame({"missing":df.isna().sum(), "pct":(df.isna().mean()*100).round(2)})
print(m[m.missing>0] if (m.missing>0).any() else "none"); print(m.T.to_string())
for c in df.select_dtypes("object").columns.tolist()+[c for c in df.columns if df[c].dtype.name=="str"]:
    blanks = df[c].astype(str).str.strip().isin(["","nan","NaN","NA","N/A","null","None","-","?"]).sum()
    print(f"  string blanks/placeholder in {c}: {blanks} (incl. real NaN)")
print("Placeholder numerics -1/999/9999:", {c:int(df[c].isin([-1,999,9999]).sum()) for c in df.select_dtypes('number')})
print("Missing by placed status:"); print(df.groupby("placed")[["company_type","job_role"]].agg(lambda s: s.isna().sum()))
print("salary_lpa == 0:", (df.salary_lpa==0).sum(), "| all unplaced:", (df.loc[df.salary_lpa==0,"placed"]==0).all())

print("\n=== (3) FORMATTING ===")
for c in ["branch","company_type","job_role"]:
    s = df[c].dropna()
    print(f"\n{c}: {s.nunique()} distinct raw | {s.str.strip().str.lower().nunique()} after strip+lower")
    print("  leading/trailing space:", (s!=s.str.strip()).sum(), "| double spaces:", s.str.contains("  ").sum(), "| mixed-case variants:", s.str.strip().str.lower().nunique()!=s.nunique())
    print(s.value_counts().to_dict())
print("\nsalary_lpa (Package equivalent): dtype", df.salary_lpa.dtype)
sal = df.salary_lpa[df.salary_lpa>0]
print("  decimals >2 places:", (sal.round(2)!=sal).sum(), "| negatives:", (df.salary_lpa<0).sum(), "| min/max (placed):", sal.min(), sal.max())
print("  non-numeric strings in raw file:", "none (pandas parsed as float64)")
raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
print("  raw text check - values with letters/symbols in salary_lpa:", raw.salary_lpa.str.contains(r"[^0-9.]").sum())
print("  raw text - decimals places distribution:", raw.salary_lpa.str.split(".").str[1].str.len().value_counts(dropna=False).to_dict())
print("  raw text - student_id pattern violations:", (~raw.student_id.str.fullmatch(r"S\d+")).sum())
print("  raw text - other numeric cols with non-numeric text:", {c:int(raw[c].str.contains(r"[^0-9.\-]").sum()) for c in raw.columns if c not in ["student_id","branch","company_type","job_role"]})
