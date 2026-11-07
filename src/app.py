# app.py - local analyst dashboard for the UEBA alert results
# Run from the project folder with:  streamlit run src/app.py
# Local use only: the dataset licence does not allow publishing the data.
import pandas as pd
import streamlit as st
from pathlib import Path
from sklearn.metrics import roc_auc_score

# Folders where the earlier scripts saved their results (outside the repo)
OUT_DIR = Path(r"D:\ueba-data\output")
ANSWERS = Path(r"D:\ueba-data\answers\insiders.csv")

# Links to the MITRE pages checked earlier
MITRE_LINKS = {
    "T1078": "https://attack.mitre.org/techniques/T1078/",
    "T1052.001": "https://attack.mitre.org/techniques/T1052/001/",
}

st.set_page_config(page_title="UEBA Insider Threat Dashboard", layout="wide")


# ---------- loading (cached so the files are read only once) ----------
@st.cache_data
def load_alerts():
    df = pd.read_csv(OUT_DIR / "alerts_explained.csv", parse_dates=["day"])
    return df.sort_values("rank").reset_index(drop=True)


@st.cache_data
def load_daily():
    return pd.read_csv(OUT_DIR / "features_daily.csv", parse_dates=["day"])


@st.cache_data
def load_key():
    key = pd.read_csv(ANSWERS)
    return key[key["dataset"] == 4.2][["user"]].assign(is_insider=1)


def hhmm(x):
    """7.75 -> '07:45'"""
    if pd.isna(x):
        return "n/a"
    h = int(x)
    m = int(round((x - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return f"{h:02d}:{m:02d}"


# ---------- check the result files exist ----------
needed = [OUT_DIR / "alerts_explained.csv", OUT_DIR / "features_daily.csv"]
missing = [p.name for p in needed if not p.exists()]
if missing:
    st.error(
        "Missing result files: " + ", ".join(missing)
        + ". Run features.py, baseline.py, model.py and explain.py first."
    )
    st.stop()

alerts = load_alerts()


def severity(rank):
    """Triage bands by rank. A SOC convention for this project, not a model output."""
    if rank <= 10:
        return "Critical"
    if rank <= 50:
        return "High"
    if rank <= 100:
        return "Medium"
    return "Low"


alerts["severity"] = alerts["rank"].map(severity)

# ---------- sidebar ----------
st.sidebar.header("Filters")
anonymize = st.sidebar.checkbox(
    "Anonymize user IDs", value=True,
    help="Shows User-001, User-002 ... (by rank) instead of dataset IDs. "
         "Keep this on when taking screenshots.",
)
conf_choice = st.sidebar.selectbox("Confidence", ["all", "normal", "low"])
sev_choice = st.sidebar.multiselect(
    "Severity", ["Critical", "High", "Medium", "Low"],
    default=["Critical", "High", "Medium", "Low"],
)
min_score = st.sidebar.slider(
    "Minimum anomaly score",
    float(alerts["anomaly_score"].min()), float(alerts["anomaly_score"].max()),
    float(alerts["anomaly_score"].min()), step=0.005,
)
top_n = st.sidebar.number_input(
    "Show at most this many alerts", min_value=10, max_value=1000, value=50, step=10
)


def label(rank, user):
    return f"User-{int(rank):03d}" if anonymize else user


view = alerts[alerts["anomaly_score"] >= min_score]
view = view[view["severity"].isin(sev_choice)]
if conf_choice != "all":
    view = view[view["confidence"] == conf_choice]
view = view.head(int(top_n))

# ---------- header ----------
st.title("UEBA Insider Threat Dashboard")
st.caption(
    "Synthetic CERT r4.2 data, local use only. An alert means **unusual for "
    "this user**, not malicious. Check the context before escalating."
)

tab_over, tab_queue, tab_detail, tab_eval = st.tabs(
    ["Overview", "Alert queue", "Alert detail", "Evaluation"]
)

# ---------- tab 0: SOC overview ----------
with tab_over:
    sev_counts = view["severity"].value_counts()
    daily_all = load_daily()
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Users monitored", daily_all["user"].nunique())
    k2.metric("Alerts in view", len(view))
    k3.metric("Critical", int(sev_counts.get("Critical", 0)))
    k4.metric("High", int(sev_counts.get("High", 0)))
    k5.metric("Low confidence", int((view["confidence"] == "low").sum()))
    st.caption(
        "Severity bands follow rank: Critical = top 10, High = 11-50, Medium = "
        "51-100, Low = the rest. This is a triage convention, not model output."
    )

    if view.empty:
        st.info("No alerts match the filters. Change them in the sidebar.")
    else:
        o1, o2 = st.columns(2)
        with o1:
            st.subheader("Alerts by severity")
            order = ["Critical", "High", "Medium", "Low"]
            st.bar_chart(sev_counts.reindex(order).fillna(0))
            st.subheader("Alerts by main signal")
            st.bar_chart(view["top_signal"].value_counts())
        with o2:
            st.subheader("Alerts by flagged month")
            by_month = view.groupby(view["day"].dt.to_period("M").astype(str)).size()
            st.bar_chart(by_month)
            st.subheader("Alerts by MITRE technique")
            techs = (
                view["mitre"].astype(str).str.split(", ").explode().value_counts()
            )
            st.bar_chart(techs)

        st.subheader("Top 10 riskiest users in view")
        top10 = view.head(10)
        st.dataframe(
            pd.DataFrame({
                "Rank": top10["rank"],
                "User": [label(r, u) for r, u in zip(top10["rank"], top10["user"])],
                "Severity": top10["severity"],
                "Day": top10["day"].dt.date,
                "Score": top10["anomaly_score"].round(3),
                "Why flagged": top10["reasons"],
            }),
            hide_index=True,
        )

    st.subheader("Company-wide activity over time")
    st.caption("All users together, per week. Spikes are a starting point for questions.")
    org = daily_all.groupby("day").agg(
        active_users=("user", "nunique"),
        usb_connects=("usb_connects", "sum"),
        files_copied=("files_copied", "sum"),
    )
    # weekly view: weekends no longer pull the line to zero; drop partial first/last weeks
    org = org.resample("W").agg(
        {"active_users": "mean", "usb_connects": "sum", "files_copied": "sum"}
    ).iloc[1:-1]
    a1, a2, a3 = st.columns(3)
    with a1:
        st.caption("Average active users per day, by week")
        st.line_chart(org["active_users"])
    with a2:
        st.caption("USB connects per week")
        st.line_chart(org["usb_connects"])
    with a3:
        st.caption("Files copied to USB per week")
        st.line_chart(org["files_copied"])

# ---------- tab 1: alert queue ----------
with tab_queue:
    c1, c2, c3 = st.columns(3)
    c1.metric("Alerts shown", len(view))
    c2.metric("Low-confidence in view", int((view["confidence"] == "low").sum()))
    c3.metric("Users ranked in total", len(alerts))

    shown = pd.DataFrame({
        "Rank": view["rank"],
        "User": [label(r, u) for r, u in zip(view["rank"], view["user"])],
        "Severity": view["severity"],
        "Day": view["day"].dt.date,
        "Score": view["anomaly_score"].round(3),
        "Confidence": view["confidence"],
        "Why flagged": view["reasons"],
        "MITRE": view["mitre"],
    })
    st.dataframe(shown, hide_index=True)
    st.download_button(
        "Download these alerts as CSV",
        data=shown.to_csv(index=False).encode("utf-8"),
        file_name="alerts_view.csv",
        mime="text/csv",
        help="Respects the Anonymize setting. Keep it on if you share the file.",
    )

# ---------- tab 2: alert detail ----------
with tab_detail:
    if view.empty:
        st.info("No alerts match the filters. Change them in the sidebar.")
    else:
        lookup = {int(r): label(r, u) for r, u in zip(view["rank"], view["user"])}
        choice = st.selectbox(
            "Choose an alert", options=list(lookup.keys()),
            format_func=lambda r: f"#{r}  {lookup[r]}",
        )
        row = alerts[alerts["rank"] == choice].iloc[0]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rank", int(row["rank"]))
        m2.metric("Anomaly score", f"{row['anomaly_score']:.3f}")
        m3.metric("Flagged day", str(row["day"].date()))
        m4.metric("Confidence", row["confidence"])

        if row["confidence"] == "low":
            st.warning(
                "Low confidence: this user had few earlier active days, so the "
                "baseline is thin. Do not escalate on the score alone."
            )

        left, right = st.columns(2)
        with left:
            st.subheader("Why it was flagged")
            for reason in str(row["reasons"]).split("; "):
                st.markdown(f"- {reason}")

            st.subheader("Flagged day vs the user's usual")
            compare = pd.DataFrame({
                "Signal": ["First logon", "USB connects", "Files copied to USB"],
                "Flagged day": [
                    hhmm(row["first_logon"]),
                    str(int(row["usb_connects"])),
                    str(int(row["files_copied"])),
                ],
                "Usual (earlier days)": [
                    hhmm(row["usual_first_logon"]),
                    "n/a" if pd.isna(row["usual_usb_connects"]) else f"{row['usual_usb_connects']:.1f}",
                    "n/a" if pd.isna(row["usual_files_copied"]) else f"{row['usual_files_copied']:.1f}",
                ],
            })
            st.dataframe(compare, hide_index=True)

        with right:
            st.subheader("What an analyst would check")
            for check in str(row["checks"]).split(" | "):
                st.markdown(f"- {check}")

            st.subheader("MITRE ATT&CK (resembles, not proof)")
            for tid in str(row["mitre"]).split(", "):
                if tid in MITRE_LINKS:
                    st.markdown(f"- [{tid}]({MITRE_LINKS[tid]})")
                else:
                    st.markdown(f"- {tid}")
            st.caption("See docs/triage-guide.md for escalation guidance.")

        # ----- activity timeline around the flagged day -----
        st.subheader("Activity around the flagged day")
        days_before = st.slider("Days before the flagged day", 14, 180, 60)
        daily = load_daily()
        u = daily[daily["user"] == row["user"]].sort_values("day")
        start = row["day"] - pd.Timedelta(days=days_before)
        end = row["day"] + pd.Timedelta(days=7)
        win = u[(u["day"] >= start) & (u["day"] <= end)].set_index("day")

        if win.empty:
            st.info("No activity rows in this window.")
        else:
            t1, t2, t3 = st.columns(3)
            with t1:
                st.caption("First logon hour (24-hour clock)")
                st.line_chart(win["first_logon"])
            with t2:
                st.caption("USB connects per day")
                st.bar_chart(win["usb_connects"])
            with t3:
                st.caption("Files copied to USB per day")
                st.bar_chart(win["files_copied"])
            st.caption(
                f"The flagged day is {row['day'].date()}. Days with no activity "
                "are not in the data and appear as gaps."
            )

# ---------- tab 3: evaluation ----------
with tab_eval:
    st.subheader("How well did the ranking match the answer key?")
    st.caption(
        "Counts only. The answer key is used for evaluation, never for training "
        "or for choosing settings. Dense-needle synthetic data: real-world "
        "precision would be much lower."
    )
    if not ANSWERS.exists():
        st.info("Answer key not found, so the evaluation is hidden.")
    else:
        key = load_key()
        ev = alerts[["user", "rank", "anomaly_score"]].merge(key, on="user", how="left")
        ev["is_insider"] = ev["is_insider"].fillna(0).astype(int)
        ev = ev.sort_values("rank")
        n, n_ins = len(ev), int(ev["is_insider"].sum())

        rows = []
        for k in (10, 25, 50, 100, 200):
            found = int(ev.head(k)["is_insider"].sum())
            rows.append({
                "Top k": k,
                "Insiders found": found,
                "Precision": round(found / k, 2),
                "Recall": round(found / n_ins, 2) if n_ins else 0.0,
                "Random picking finds": round(k * n_ins / n, 1),
            })
        e1, e2, e3 = st.columns(3)
        e1.metric("Users ranked", n)
        e2.metric("Planted insiders", n_ins)
        if 0 < n_ins < n:
            e3.metric("ROC AUC", f"{roc_auc_score(ev['is_insider'], ev['anomaly_score']):.3f}")
        table = pd.DataFrame(rows)
        st.dataframe(table, hide_index=True)
        st.bar_chart(table.set_index("Top k")[["Insiders found", "Random picking finds"]])