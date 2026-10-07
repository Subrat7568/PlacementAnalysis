# Data Dictionary — `data/processed/student_placement_cleaned.csv`

| Column | Type | Description |
|---|---|---|
| `student_id` | string | Unique student identifier (`S0`, `S1`, ...) |
| `cgpa` | float | Cumulative GPA, 5.0–10.0 scale |
| `branch` | string | Engineering branch (standardized to full names) |
| `college_tier` | int (1–3) | College ranking tier; 1 = highest |
| `python_skill` | int (0/1) | Has Python skill flag |
| `dsa_skill` | int (0/1) | Has data structures & algorithms skill flag |
| `ml_skill` | int (0/1) | Has machine learning skill flag |
| `web_dev_skill` | int (0/1) | Has web development skill flag |
| `coding_score` | float | Coding test score, 0–100 |
| `communication_score` | float | Communication assessment score, 4–10 |
| `aptitude_score` | float | Aptitude test score, 40–100 |
| `internships` | int | Number of internships completed |
| `projects` | int | Number of academic/personal projects |
| `backlogs` | int | Number of academic backlogs |
| `resume_score` | float | Resume score, **capped at 100** (see `resume_score_raw`) |
| `resume_score_raw` | float | Original resume score before capping; some values exceed 100 (max 132.1) |
| `resume_over_100` | int (0/1) | Flag: 1 if `resume_score_raw` exceeded 100 |
| `placed` | int (0/1) | Placement outcome — target variable for prediction tasks |
| `company_type` | string | `MNC`, `Startup`, `Mid-size`, `Top Tech`, or `Not placed` |
| `job_role` | string | `Software Engineer`, `Data Scientist`, `Analyst`, `Web Developer`, or `Not placed` |
| `salary_lpa` | float | Package in LPA; `NaN` for unplaced students |

## Notes for modeling

- **Leakage warning:** `company_type`, `job_role`, and `salary_lpa` are only
  known *after* a student is placed. Do not use them as input features when
  predicting `placed` — they would leak the answer.
- `skill_score` from the raw file was dropped (it was exactly the sum of the
  four skill flag columns — redundant).
- Suggested feature set for predicting `placed`: `cgpa`, `branch`,
  `college_tier`, the four skill flags, `coding_score`, `communication_score`,
  `aptitude_score`, `internships`, `projects`, `backlogs`, `resume_score`,
  `resume_over_100`.
