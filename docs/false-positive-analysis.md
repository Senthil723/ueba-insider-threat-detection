# False Positive Analysis (version 1)

Four of the top 50 ranked users were not planted insiders. They are labeled
FP-1 to FP-4. No user IDs or dates are shown.

| | Rank | Main signal | Flagged day vs the user's normal | Earlier days available |
|---|---|---|---|---|
| FP-1 | 17 | early logon | logon about 1:16 AM (usual about 7:45); 4 files copied (usual 0.7/day) | 11 |
| FP-2 | 43 | files copied | 15 files (usual 4.2/day); 4 USB connects | 13 |
| FP-3 | 44 | early logon | logon about 2:58 AM (usual about 7:45); 5 USB connects (usual 2/day) | 299 |
| FP-4 | 50 | files copied | 5 files (usual 0.64/day); 3 USB connects | 185 |

## Findings
- FP-1 and FP-2 had thin baselines (11 and 13 earlier days). Minimum
  history of 10 days is too low for stable scores.
- FP-3 and FP-4 are genuine deviations from a long baseline. They are
  unusual behavior, but not planted attacks. Not being in the answer key
  does not prove the behavior is harmless.

## What an analyst would check (hypotheses, not findings)
- Early logon: was it an approved overnight task or maintenance window?
  Which PC was used, and did the user log on elsewhere that day?
- Burst of USB use or file copies: was there a project handoff or
  migration? What file types were copied? Is the USB device approved?
- Thin history: treat the alert as low confidence for the user's first weeks.

## Scenario 3
Ranks of the 10 scenario 3 insiders: 74, 133, 135, 167, 169, 176, 179, 194,
206, 233. Only one is in the top 100. Logon, USB and file logs cannot show
the keylogger or the mass email. Planned: LDAP role and unusual-PC features,
based on the dataset readme and public scenario text, not on insider files.