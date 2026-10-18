# Triage Guide (draft)

How an analyst could handle the alerts this tool produces. An alert means
"unusual for this user", not "malicious". Everything below is a hypothesis to
check, not a conclusion.

## Alert types

### 1. First-ever USB use (T1052.001)
- Meaning: the user had many active days with no USB use, then plugged one in.
- Check: is the device approved or on an asset list? What was copied?
  Did the user have a new task or role?
- Often harmless: new equipment, a presentation, a one-off file transfer.
- Escalate if: it combines with other signals below, or the files are
  sensitive.

### 2. Burst of USB connects or file copies (T1052.001)
- Meaning: far more USB connects or copied files than that user's usual.
- Check: file types and names, project or migration tickets, whether the
  copying happened on the user's own PC.
- Often harmless: handover, backup, migration.
- Escalate if: the volume is large, the files look unrelated to the user's
  work, or it repeats on several days.

### 3. Unusual first logon time (T1078)
- Meaning: the first logon of the day is far from this user's usual time.
- Check: which PC, a maintenance window or on-call duty, other logons that day.
- Often harmless: overnight work, a time zone change, working late.
- Escalate if: it happens with USB activity or on a PC the user does not
  normally use.

### 4. Combined signals
- Meaning: two or more of the above on the same day (the top alerts in
  version 1 show this pattern).
- Treat as higher priority than a single signal, then follow the checks above.

### 5. Low-confidence alert
- Meaning: the user had fewer than 30 earlier active days, so their
  baseline is thin.
- Check: whether the user is new or changed role. Do not escalate on the
  score alone.

### 6. Regular USB user with a busier day
- Meaning: a user who already uses USB regularly shows several times their
  usual USB connects or files copied (for example about 3 times the usual).
- Why it is hard: in version 1 the alerts around ranks 41 to 50 are mostly
  this pattern, and about 3 of 10 of them were not planted insiders. The
  alert text alone cannot tell the two apart.
- Check: file types and names, project or migration tickets, whether the
  device is approved, and whether the same burst repeats on other days.
- Escalate if: the files look unrelated to the user's work, or the pattern
  repeats and grows.

## Suggested priority (my suggestion, not validated)
- High: 2 or more alert types on one day, with normal confidence.
- Medium: one alert type with a large deviation, normal confidence.
- Low: any low-confidence alert, or one mild signal.

## What this tool cannot tell you
- Intent. It sees unusual behavior, not malice.
- What was inside the copied files.
- Behavior outside logon, USB and file-copy logs, for example email or web.
- Most of the sysadmin keylogger scenario, which these logs barely show.

## What to record for each alert
Reason shown, checks done, who confirmed it, outcome (benign, needs follow-up,
escalated), and the time taken.