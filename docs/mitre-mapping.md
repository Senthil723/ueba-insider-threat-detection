# MITRE ATT&CK Mapping

Checked on attack.mitre.org (ATT&CK v19/v20 pages). The mapping says what an
alert resembles. It does not prove an attack or an intent.

| Alert reason | Technique | Fit |
|--------------|-----------|-----|
| First logon far from the user's usual time | T1078 Valid Accounts | Loose. The technique is about adversaries abusing existing account credentials. An insider uses their own account, so the behavior only resembles it. |
| First-ever USB use; burst of USB connects | T1052.001 Exfiltration over USB | Close. The technique covers exfiltration over a USB device. |
| Burst of files copied to USB | T1052.001 Exfiltration over USB | Close. |

Considered and dropped: T1074 Data Staged. Staging happens before data
leaves, and these logs show the copy itself, so it was a weaker fit.

Not covered: scenario 3 techniques (keylogging, using another person's
login to send email). These logs do not contain those events.