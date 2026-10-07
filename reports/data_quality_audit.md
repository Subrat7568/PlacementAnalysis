# Data Quality Audit

Source file: `data/raw/student_placement_salary_elite_v2.csv` (9,000 rows × 20 columns)
Audit script: `scripts/02_audit_data_quality.py`

This audit was run **before any cleaning**, to decide what actually needed fixing
rather than cleaning on assumption.

## 1. Duplicates

| Check | Result |
|---|---|
| Exact duplicate rows | 0 |
| Duplicate `student_id` | 0 |
| Duplicate rows ignoring `student_id` | 0 |
| Near-duplicates (numeric columns bucketed) | 0 |

No duplicate-removal was needed. The dataset has one clean row per student.

## 2. Missing values

| Column | Missing | % | Cause |
|---|---|---|---|
| `company_type` | 1,298 | 14.42% | Null exactly for unplaced students (expected) |
| `job_role` | 1,298 | 14.42% | Same as above |
| `salary_lpa` | 0 nulls, but 1,298 rows = **0.0** | 14.42% | Disguised missing value — 0 used in place of NaN for unplaced students |

No other column had missing, blank, or placeholder values (checked for `""`, `"NA"`,
`"null"`, `-1`, `999`, `9999`, etc. — none found).

## 3. Formatting

| Column | Distinct values | Issues |
|---|---|---|
| `branch` | 6 | None — no case variants, no stray whitespace |
| `company_type` | 4 | None |
| `job_role` | 4 | None |
| `salary_lpa` | numeric (float64) | No letters/symbols, no negatives; decimal-place variation is cosmetic only |

Branch abbreviation styles are mixed (`IT`, `ECE`, `CSE`, `EEE` vs. `Civil`,
`Mechanical`) but internally consistent — standardized to full names in cleaning.

## 4. Columns requested but not present in this file

A later request asked to standardize `Branch`, `Package`, and `Placement_Date`.
Only `branch` (lowercase) exists. There is **no `Package` column** (closest
equivalent: `salary_lpa`, already numeric) and **no `Placement_Date` /
year / batch column of any kind**. This means:
- No year-over-year trend analysis is possible with this file.
- The dashboard substitutes **placement rate by college tier** for the missing
  time trend, since tier is the only ordinal dimension in the data.

## 5. Other things worth flagging to a reviewer

- `resume_score` exceeds 100 in 303 rows (max 132.1) — kept as `resume_score_raw`,
  capped at 100 in `resume_score`, flagged via `resume_over_100`.
- `skill_score` is exactly the sum of the four skill flag columns in all 9,000
  rows — redundant, dropped in the cleaned file.
- Salary values (32.8–129.4 LPA for placed students) are far above typical
  Indian campus placement packages. The unit/source has not been confirmed
  with whoever provided the file — treat absolute salary figures with caution.
- Several categorical relationships that should exist in real placement data
  (branch → job role, skills → job role, cgpa → college tier) are statistically
  flat or near-random in this file, consistent with the data being simulated
  rather than collected from real placements.

## Cleaning decisions applied (`scripts/03_clean_data.py`)

| Issue | Decision |
|---|---|
| Salary = 0 for unplaced students | Converted to `NaN` |
| `company_type` / `job_role` null for unplaced | Filled with `"Not placed"` |
| `resume_score` > 100 | Capped at 100; original kept in `resume_score_raw`; flagged in `resume_over_100` |
| `skill_score` (redundant) | Dropped |
| `branch` abbreviations | Standardized to full names |
| Duplicates | Removal logic included; 0 rows removed |

**Leakage note:** `company_type`, `job_role`, and `salary_lpa` are only known
*after* placement. They must be excluded from any model predicting `placed`.
