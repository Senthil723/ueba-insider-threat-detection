# Behavioral Insider Threat Detection (UEBA)

A personal project that learns each user's normal behavior from activity logs
and ranks users whose behavior changes in ways that resemble insider data theft.
Built with Python, pandas and scikit-learn.

Author: Senthilmurugan

## What it does

Insiders already have legitimate access, so rule-based tools often miss them.
UEBA (User and Entity Behavior Analytics) compares each user with **their own**
history instead of one global rule. This project:

1. Builds one feature row per user per day from logon, USB and file-copy logs.
2. Compares each day with that user's earlier days (per-user z-scores).
3. Scores days with an Isolation Forest and ranks users by their highest daily score.
4. Evaluates the ranking against the dataset's answer key.
5. Analyses false positives and what an analyst would check.

## Data

CERT Insider Threat Test Dataset, release r4.2 (Carnegie Mellon University
SEI/CERT with ExactData, LLC). **Synthetic data**, not from a real company.
It is a "dense needle" dataset: 70 of the 1,000 users are planted insiders,
far more than a real organization would have.

I use three logs: `logon.csv`, `device.csv` and `file.csv`, covering about
17 months. The answer key is used **only for evaluation**, never for training
or for choosing settings.

> Copyright (c) 2011 ExactData, LLC, All Rights Reserved. The data is **not**
> redistributed in this repository. Download it from KiltHub (search "Insider
> Threat Test Dataset") and follow the licence file inside the download.
> The MIT licence in this repository covers my code only.

## Behaviors targeted

| Behavior | Resembles (MITRE ATT&CK) |
|----------|--------------------------|
| Logins at unusual hours for that user | T1078 Valid Accounts |
| Sudden or first-time USB use | T1052.001 Exfiltration over USB |
| Many more files copied to USB than usual | T1052.001 Exfiltration over USB |

The mapping says what the behavior resembles. It does not prove an attack.

## Results (version 1)

The design was fixed and committed **before** the first comparison with the
answer key (see the commit history and `docs/design-decisions.md`).

1,000 users, 70 insiders. Users are ranked by their highest daily anomaly score.

| Top k | Insiders found | Precision | Recall | Random picking finds |
|-------|----------------|-----------|--------|----------------------|
| 10    | 10             | 1.00      | 0.14   | 0.7  |
| 25    | 24             | 0.96      | 0.34   | 1.8  |
| 50    | 46             | 0.92      | 0.66   | 3.5  |
| 100   | 59             | 0.59      | 0.84   | 7.0  |
| 200   | 68             | 0.34      | 0.97   | 14.0 |

ROC AUC: 0.979.

### By dataset attack scenario

| Scenario (as described by the dataset) | Insiders | In top 100 | Median rank |
|----------------------------------------|----------|------------|-------------|
| 1: after-hours USB use, then leaves | 30 | 29 | 16 |
| 2: job searching, then heavy USB use | 30 | 29 | 42 |
| 3: sysadmin keylogger and mass email | 10 | 1 | 172 |

Scenario 3 is mostly invisible in these three logs, and the results show it.

### Comparison with simpler methods

| Method | Top 10 | Top 25 | Top 50 | Top 100 | AUC |
|--------|--------|--------|--------|---------|-----|
| Global rule: total files copied | 0 | 1 | 1 | 5 | 0.818 |
| Global rule: total USB connects | 0 | 0 | 2 | 13 | 0.844 |
| Global rule: odd-hour first logons | 0 | 2 | 12 | 12 | 0.699 |
| Per-user z-score only (max of 3 signals) | 10 | 14 | 20 | 30 | 0.914 |
| Per-user z-score only (sum of 3 signals) | 10 | 20 | 25 | 41 | 0.939 |
| **Isolation Forest v1** | **10** | **24** | **46** | **59** | **0.979** |

The per-user baseline gave most of the gain over global rules, and Isolation
Forest added more. The forest also received a first-ever-USB-use flag that the
z-score variants did not, so the gain is not credited to the model alone.

### False positives

Four of the top 50 users were not planted insiders. Two had very short
baselines (11 and 13 earlier days). Two were real deviations from long
baselines, so they would still deserve a look from an analyst. Details are in
`docs/false-positive-analysis.md`.

## Limitations

- Synthetic, dense-needle data: real-world precision would be far lower
  because real insiders are much rarer. These numbers are not a real-world estimate.
- Results come from a single run on one dataset.
- Scoring is at the user level, not the day level.
- Logon, USB and file-copy logs cannot see most of scenario 3.
- Features follow the behaviors the dataset readme lists as detectable.
- Minimum history of 10 days is too low for stable scores in a user's first weeks.

## How to run

Requirements: Python 3.13, pandas and scikit-learn
(`pip install -r requirements.txt`).

1. Download the r4.2 data and the answer key, and extract only `logon.csv`,
   `device.csv`, `file.csv` and `insiders.csv`.
2. Set the folder paths at the top of each script (they point to my local
   folders; change them to yours).
3. Run in this order:

```
python src/features.py          # one row per user per day
python src/baseline.py          # per-user z-scores
python src/model.py             # Isolation Forest scores and ranked users
python src/evaluate.py          # compare with the answer key (counts only)
python src/error_analysis.py    # false positives, scenario 3
python src/naive_baseline.py    # global-rule comparison
python src/zscore_baseline.py   # z-score-only comparison
```

## Repository layout

```
docs/        scope, design decisions, results, false-positive analysis, learning log
src/         pipeline scripts
```

## Roadmap (planned, not built yet)

- Phase 2: LDAP role and unusual-PC features, web browsing logs, a second model.
- Phase 3: plain-language alert explanations and a triage guide.
- Phase 4: a local analyst dashboard (Streamlit). Local only, because of the
  data licence.