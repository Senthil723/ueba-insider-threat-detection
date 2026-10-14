# Learning Log

Short notes in my own words, written while building the project.

## 1. What is precision at k?
Precision at k tells me how many of the top k alerts were real insiders.
In my version 1 results, 46 of my top 50 users were planted insiders,
so precision at 50 is 46 / 50 = 0.92. A SOC analyst feels this directly:
low precision means many investigations of innocent people.

## 2. Why is 0.92 not a real-world number?
The r4.2 dataset is synthetic and "dense needle": 70 of the 1,000 users
(7%) are insiders. In a real company, insiders are far rarer, so the same
method would produce many more false alerts for each real insider.
The planted attacks also change behavior that the dataset readme lists as
detectable (logon time, USB use), so they are easier to spot than real
attacks. The 0.92 only shows the method works on this dataset.

## 3. Why did the tool miss scenario 3?
Scenario 3 is a system administrator who installs a keylogger, logs in as
his supervisor and sends a mass email. My three logs (logon, USB, file copy)
only show a small part of that, so only 1 of the 10 scenario 3 insiders
was in my top 100. To catch it I would need email data, the user's role
from LDAP, and features such as logging in on someone else's PC.

## 4. Other notes
- A z-score says how far today is from that user's own average.
- I left today out of each user's baseline so a spike can't hide itself.
- I wrote my design choices down and committed them before I looked at the
  answer key, so the results are not tuned on the labels.