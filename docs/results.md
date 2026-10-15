# Results: Version 1 (design fixed before evaluation)

Dataset: CERT Insider Threat Test Dataset r4.2 (synthetic, "dense needle").
1,000 users, 70 planted insiders (30 / 30 / 10 across scenarios 1, 2, 3).
Users are ranked by their highest daily Isolation Forest anomaly score.

| Top k | Insiders found | Precision | Recall | Expected from random picking |
|-------|----------------|-----------|--------|------------------------------|
| 10    | 10             | 1.00      | 0.14   | 0.7  |
| 25    | 24             | 0.96      | 0.34   | 1.8  |
| 50    | 46             | 0.92      | 0.66   | 3.5  |
| 100   | 59             | 0.59      | 0.84   | 7.0  |
| 200   | 68             | 0.34      | 0.97   | 14.0 |

ROC AUC: 0.979

| Dataset scenario | Insiders | In top 100 | Median rank |
|------------------|----------|------------|-------------|
| 1                | 30       | 29         | 16          |
| 2                | 30       | 29         | 42          |
| 3                | 10       | 1          | 172         |

## Limitations
- Synthetic, dense-needle data: real-world precision would be much lower
  because real insiders are far rarer.
- Logon, USB and file-copy logs cannot see most of scenario 3 (keylogger
  and mass email), and the results confirm it.
- Scoring is at the user level, not the day level.
- Features follow the behaviors the dataset readme lists as fair game.
- These are single-run results with no tuning.


## Baseline comparison (version 1)

Same 1,000 users and 70 insiders. Naive rules were fixed before running
(after-hours means a first logon before 06:00 or at/after 18:00).
Ties in the naive rankings were broken randomly (seed 42).

| Method | Top 10 | Top 25 | Top 50 | Top 100 | AUC |
|--------|--------|--------|--------|---------|-----|
| Isolation Forest v1 | 10 | 24 | 46 | 59 | 0.979 |
| Naive: total files copied | 0 | 1 | 1 | 5 | 0.818 |
| Naive: total USB connects | 0 | 0 | 2 | 13 | 0.844 |
| Naive: odd-hour first logons | 0 | 2 | 12 | 12 | 0.699 |
| Random picking (expected) | 0.7 | 1.8 | 3.5 | 7.0 | 0.5 |

Notes
- The per-user baseline approach ranks far more insiders at the top of
  the queue than global rules on this dataset.
- A high AUC does not guarantee a useful top of the queue: "total files
  copied" has AUC 0.818 but found 1 insider in its top 50.
- Isolation Forest uses each user's worst day; naive rules use totals.
- Not tested yet: whether the per-user z-scores alone (no model) perform as
  well as the Isolation Forest.

  
## Per-user z-score ranking vs Isolation Forest (version 1)

Same 1,000 users and 70 insiders. Rules were fixed before running:
daily score = max or sum of three signals (absolute logon-time z-score,
USB z-score, files-copied z-score); user score = the user's highest day.
Ties broken randomly (seed 42). No model, no training.

| Method | Top 10 | Top 25 | Top 50 | Top 100 | AUC |
|--------|--------|--------|--------|---------|-----|
| z-score only: max of 3 signals | 10 | 14 | 20 | 30 | 0.914 |
| z-score only: sum of 3 signals | 10 | 20 | 25 | 41 | 0.939 |
| Isolation Forest v1 | 10 | 24 | 46 | 59 | 0.979 |
| Random picking (expected) | 0.7 | 1.8 | 3.5 | 7.0 | 0.5 |

Notes
- Per-user z-scores alone already beat the global rules in the earlier
  comparison; Isolation Forest improved the ranking further on this dataset.
- The forest also received a first-ever-USB-use flag that the z-score
  variants did not, so the gain cannot be credited to the model alone.
- Single run on synthetic, dense-needle data. Not a real-world estimate.