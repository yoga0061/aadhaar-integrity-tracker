import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.append(SRC_DIR)

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import path

st.set_page_config(
    page_title="Aadhaar Sentinel – Integrity Dashboard",
    layout="wide"
)

st.markdown(
    """
    <div style="
        background:#F5F7FA;
        padding:16px;
        border-left:6px solid #1A237E;
        color:#000000;
        font-size:16px;
    ">
        <b>🛡️ Aadhaar Sentinel</b><br>
        Integrity intelligence platform for monitoring enrolment behavior,
        detecting anomalies, and supporting proactive audit decisions.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ Aadhaar Sentinel – Integrity Intelligence Dashboard")

def load_parquet(fp, label):
    if not os.path.exists(fp):
        st.error(f"Missing required file: {label}")
        st.stop()
    return pd.read_parquet(fp)

def load_csv(fp, label):
    if not os.path.exists(fp):
        st.error(f"Missing required file: {label}")
        st.stop()
    return pd.read_csv(fp)

risk = load_parquet(path("outputs","center_risk_scores.parquet"), "Center Risk Scores")
district = load_parquet(path("outputs","district_risk_index.parquet"), "District Risk Index")
activity = load_parquet(path("outputs","daily_center_activity.parquet"), "Daily Center Activity")
anomalies = load_parquet(path("outputs","anomalies.parquet"), "Anomalies")
updates = load_parquet(path("outputs","update_type_summary.parquet"), "Update Type Summary")

policy = load_csv(path("outputs","policy_recommendations.csv"), "Policy Recommendations")
insights = load_csv(path("outputs","insights.csv"), "Insights")
audit = load_csv(path("outputs","audit_report.csv"), "Audit Report")

html_fp = path("outputs","aadhaar_integrity_report.html")

st.sidebar.header("🔎 Filters")

state = st.sidebar.selectbox(
    "Select State",
    ["All"] + sorted(risk["state"].unique())
)

if state != "All":
    risk = risk[risk["state"] == state]
    district = district[district["state"] == state]
    activity = activity[activity["state"] == state]
    anomalies = anomalies[anomalies["state"] == state]
    audit = audit[audit["state"] == state]

c1, c2, c3 = st.columns(3)
c1.metric("Critical Centers", (risk["severity"]=="Critical").sum())
c2.metric("Medium Risk Centers", (risk["severity"]=="Medium").sum())
c3.metric("Total Centers Monitored", len(risk))

st.subheader("🏙️ Highest Risk District Snapshot")

top_district = district.sort_values("avg_risk_score", ascending=False).iloc[0]

critical_count = risk[
    (risk["district"] == top_district["district"]) &
    (risk["severity"] == "Critical")
].shape[0]

d1, d2, d3 = st.columns(3)
d1.metric("District", top_district["district"])
d2.metric("Avg Risk Score", f"{top_district['avg_risk_score']:.2f}")
d3.metric("Critical Centers", critical_count)

st.subheader("🚨 Top 10 Centers Needing Immediate Audit")

top10 = risk.sort_values("risk_score", ascending=False).head(10)

st.dataframe(
    top10[["state","district","pincode","risk_score","severity"]],
    use_container_width=True
)

st.download_button(
    "⬇️ Download Top 10 Risky Centers (CSV)",
    data=top10.to_csv(index=False),
    file_name="top_10_risky_centers.csv",
    mime="text/csv"
)

st.subheader("🧠 Why is this Center Risky?")

selected_pin = st.selectbox(
    "Select Center (Pincode)",
    top10["pincode"].astype(str)
)

row = risk[risk["pincode"].astype(str) == selected_pin].iloc[0]

st.info(
    f"""
    **Risk Explanation**
    - Anomaly Days: {int(row['anomaly_days'])}
    - Max Daily Spike: {int(row['max_spike'])}
    - Risk Score: {row['risk_score']:.2f}
    """
)

st.subheader("🧠 System Confidence Indicator")

confidence = min(
    100,
    int((row["anomaly_days"] / max(1, risk["anomaly_days"].max())) * 100)
)

st.progress(confidence)
st.caption(f"Confidence Score: {confidence}/100 based on anomaly consistency")

st.subheader("⏳ Center Activity Timeline")

center_ts = activity[activity["pincode"].astype(str) == selected_pin]

st.plotly_chart(
    px.line(
        center_ts,
        x="date",
        y="daily_updates",
        title=f"Daily Activity Trend – Pincode {selected_pin}"
    ),
    use_container_width=True
)

st.subheader("🧾 Common Anomaly Reasons")

reason_counts = anomalies["anomaly_reason"].value_counts().reset_index()
reason_counts.columns = ["Reason","Count"]

st.plotly_chart(
    px.bar(reason_counts, x="Reason", y="Count"),
    use_container_width=True
)

st.subheader("🗺️ District Risk Heatmap")

heatmap_df = district.pivot_table(
    index="district",
    columns="state",
    values="avg_risk_score",
    fill_value=0
)

st.plotly_chart(
    px.imshow(
        heatmap_df,
        aspect="auto",
        color_continuous_scale="Reds",
        title="District-wise Average Risk Score"
    ),
    use_container_width=True
)

st.subheader("🏛️ Policy Recommendations")
st.dataframe(policy, use_container_width=True)

st.subheader("💡 Key System Insights")

for _, r in insights.iterrows():
    st.markdown(f"• **{r.iloc[0]}**")

st.subheader("🚨 Live Audit Queue")

audit_queue = audit[audit["severity"].isin(["Critical","Medium"])] \
    .sort_values("risk_score", ascending=False)

st.dataframe(
    audit_queue.head(25),
    use_container_width=True
)

st.subheader("📦 Evidence Pack for Auditors")

st.download_button(
    "⬇️ Audit Report (CSV)",
    data=audit.to_csv(index=False),
    file_name="audit_report.csv",
    mime="text/csv"
)

st.download_button(
    "⬇️ Policy Recommendations (CSV)",
    data=policy.to_csv(index=False),
    file_name="policy_recommendations.csv",
    mime="text/csv"
)

st.download_button(
    "⬇️ Insights (CSV)",
    data=insights.to_csv(index=False),
    file_name="insights.csv",
    mime="text/csv"
)

st.subheader("📄 Full Audit Report")

if os.path.exists(html_fp):
    with open(html_fp, "rb") as f:
        st.download_button(
            "⬇️ Download Full HTML Integrity Report",
            data=f,
            file_name="aadhaar_integrity_report.html",
            mime="text/html"
        )

st.markdown(
    """
    <hr>
    <center>
    <small>
    Aadhaar Sentinel • Secure • Privacy-First • Integrity Intelligence
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
