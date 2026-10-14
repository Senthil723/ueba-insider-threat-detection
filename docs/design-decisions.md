# Design Decisions (fixed before evaluation)

These choices were made before comparing any alerts with the answer key.
They are not tuned on the answer key.

- Baseline: each user's own earlier days (today excluded).
- Minimum history: 10 active days before a day is scored.
- Spread floors: 0.5 hours for logon time, 1.0 for USB and file counts.
- USB and file z-scores clipped at 0 (only increases matter for theft).
- Model: Isolation Forest, 200 trees, contamination="auto", random_state=42.
- Features: logon-time z-score, USB z-score, files-copied z-score, first-ever USB use.
- User risk score: the user's highest daily anomaly score.