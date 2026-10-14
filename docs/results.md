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