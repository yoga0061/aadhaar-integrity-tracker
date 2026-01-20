import sys
import os

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.append(SRC_DIR)

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Aadhaar Sentinel – Integrity Dashboard",
    layout="wide"
)

st.markdown(
    """
    <div style="
        background:#E3F2FD;
        padding:16px;
        border-left:6px solid #0D47A1;
        color:#000000;
        font-size:16px;
    ">
        <b>🎯 Demo Mode – UIDAI Hackathon 2026</b><br>
        Precomputed, anonymized Aadhaar integrity analytics for audit decision-making.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ Aadhaar Sentinel – Integrity Intelligence Dashboard")

# --------------------------------------------------
# SAFE LOADERS
# --------------------------------------------------
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

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
risk = load_parquet(path("outputs","center_risk_scores.parquet"), "Center Risk Scores")
district = load_parquet(path("outputs","district_risk_index.parquet"), "District Risk Index")
activity = load_parquet(path("outputs","daily_center_activity.parquet"), "Daily Center Activity")
anomalies = load_parquet(path("outputs","anomalies.parquet"), "Anomalies")
updates = load_parquet(path("outputs","update_type_summary.parquet"), "Update Summary")

policy = load_csv(path("outputs","policy_recommendations.csv"), "Policy Recommendations")
insights = load_csv(path("outputs","insights.csv"), "Insights")
audit = load_csv(path("outputs","audit_report.csv"), "Audit Report")

html_fp = path("outputs","aadhaar_integrity_report.html")

# --------------------------------------------------
# SIDEBAR FILTER
# --------------------------------------------------
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

# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Critical Centers", (risk["severity"]=="Critical").sum())
c2.metric("Medium Risk Centers", (risk["severity"]=="Medium").sum())
c3.metric("Total Centers Monitored", len(risk))

# --------------------------------------------------
# DISTRICT SNAPSHOT
# --------------------------------------------------
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

# --------------------------------------------------
# DISTRICT RISK HEATMAP + TOP 5 + LEGEND
# --------------------------------------------------
st.subheader("🗺️ District Risk Intelligence")

left, right = st.columns([3, 1])

with left:
    heatmap_df = district.copy()

    fig = px.imshow(
        heatmap_df.pivot_table(
            index="district",
            columns="state",
            values="avg_risk_score",
            fill_value=0
        ),
        aspect="auto",
        color_continuous_scale="YlOrRd",
        zmin=heatmap_df["avg_risk_score"].min(),
        zmax=heatmap_df["avg_risk_score"].max(),
        title="District-wise Average Risk Score",
        labels=dict(color="Avg Risk Score")
    )

    fig.update_traces(
        hovertemplate=
        "<b>District:</b> %{y}<br>" +
        "<b>State:</b> %{x}<br>" +
        "<b>Avg Risk Score:</b> %{z:.2f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("🔴 Darker color indicates higher integrity risk and audit priority.")

with right:
    st.markdown("### 🚨 Top 5 High-Risk Districts")

    top5 = district.sort_values(
        "avg_risk_score", ascending=False
    ).head(5)

    for _, r in top5.iterrows():
        st.markdown(
            f"""
            **{r['district']}**  
            State: {r['state']}  
            Avg Risk: `{r['avg_risk_score']:.2f}`
            """
        )

    st.markdown("---")
    st.markdown("### 🎯 Severity Legend")
    st.markdown("🔴 **Critical** : Immediate audit required")
    st.markdown("🟠 **Medium** : Increased monitoring")
    st.markdown("🟢 **Low** : Routine observation")

# --------------------------------------------------
# TOP 10 RISKY CENTERS
# --------------------------------------------------
st.subheader("🚨 Top 10 Centers Needing Immediate Audit")

top10 = risk.sort_values("risk_score", ascending=False).head(10)

st.dataframe(
    top10[["state","district","pincode","risk_score","severity"]],
    use_container_width=True
)

# --------------------------------------------------
# POLICY RECOMMENDATIONS
# --------------------------------------------------
st.subheader("🏛️ Policy Recommendations")

st.dataframe(policy, use_container_width=True)

# --------------------------------------------------
# AUTO INSIGHTS
# --------------------------------------------------
st.subheader("💡 Key System Insights")

for _, r in insights.iterrows():
    st.markdown(f"• **{r.iloc[0]}**")

# --------------------------------------------------
# LIVE AUDIT QUEUE
# --------------------------------------------------
st.subheader("🚨 Live Audit Queue")

audit_queue = audit[audit["severity"].isin(["Critical","Medium"])] \
    .sort_values("risk_score", ascending=False)

st.dataframe(audit_queue.head(25), use_container_width=True)

# --------------------------------------------------
# HTML REPORT DOWNLOAD
# --------------------------------------------------
st.subheader("📄 Full Audit Report")

if os.path.exists(html_fp):
    with open(html_fp, "rb") as f:
        st.download_button(
            "⬇️ Download Full HTML Integrity Report",
            data=f,
            file_name="aadhaar_integrity_report.html",
            mime="text/html"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    """
    <hr>
    <center>
    <small>
    Aadhaar Sentinel • Privacy-by-Design • UIDAI Hackathon 2026
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
