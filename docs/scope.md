# Project Scope: Behavioral Insider Threat Detection Tool (UEBA)

## 1. Problem Statement
Insider threats come from people who already have legitimate access, so
signature-based tools often miss them. This project builds a small UEBA
(User and Entity Behavior Analytics) pipeline in Python. It learns each
user's normal behavior from activity logs, flags unusual behavior, and
gives each user a daily risk score so a SOC analyst can triage the alerts.

## 2. Goals
- Build per-user, per-day behavioral features from log data using pandas.
- Detect anomalies with an unsupervised model from scikit-learn.
- Produce a daily risk score per user and a ranked alert list.
- Document how an analyst would triage each type of alert.

## 3. Threat Scenarios in Scope
| # | Scenario | Suspicious behavior | MITRE ATT&CK |
|---|----------|--------------------|--------------|
| 1 | After-hours access | Login at 2 AM by a user who normally works 9 to 6 | T1078 Valid Accounts |
| 2 | Removable media use | Sudden USB activity by a user who rarely or never uses it | T1052.001 Exfiltration over USB |
| 3 | Abnormal data movement | Far more file copies than the user's normal | T1074 Data Staged |

## 4. Data
- Planned source: the CERT Insider Threat synthetic dataset from Carnegie
  Mellon University (exact release to be chosen after checking size).
- The data is synthetic, not from a real company. This will be stated in
  the README and on my resume.
- Raw data will not be uploaded to this repository. The README will explain
  where to download it.

## 5. Approach
1. Load, clean and explore the logs.
2. Create features per user per day (for example login hour, number of USB
   events, number of file copies).
3. Build a baseline of normal behavior for each user.
4. Score deviations from the baseline with an anomaly detection model.
5. Convert scores into risk levels and a ranked alert list.

## 6. Output
- A daily risk score per user.
- A ranked alert list showing why each user was flagged.
- Short triage notes: what an analyst should check next for each alert type.

## 7. Out of Scope
- Real-time or streaming detection
- Deep learning models
- Dashboards or web applications
- Cloud deployment
- Any claim about performance on real enterprise networks

## 8. Known Limitations
- An anomaly is not the same as a malicious act. False positives are
  expected, for example an employee working late before a deadline.
- Results come from one synthetic dataset and cannot be generalized to real
  environments.
- The MITRE ATT&CK mapping describes what each scenario resembles. It does
  not prove an attack happened.

## 9. Success Criteria
- The pipeline runs end to end, from raw logs to a ranked alert list.
- Every feature and model choice can be explained.
- The README reports only results that I actually measured, along with the
  limitations.
