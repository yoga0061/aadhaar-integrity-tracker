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
# LOAD FILES SAFELY
# --------------------------------------------------
def load_parquet(fp, label):
    if not os.path.exists(fp):
        st.error(f"Missing required output: {label}")
        st.stop()
    return pd.read_parquet(fp)

def load_csv(fp, label):
    if not os.path.exists(fp):
        st.error(f"Missing required output: {label}")
        st.stop()
    return pd.read_csv(fp)

risk = load_parquet(path("outputs","center_risk_scores.parquet"), "Center Risk Scores")
district = load_parquet(path("outputs","district_risk_index.parquet"), "District Risk Index")
policy = load_csv(path("outputs","policy_recommendations.csv"), "Policy Recommendations")
insights = load_csv(path("outputs","insights.csv"), "Insights")

html_fp = path("outputs","aadhaar_integrity_full_report.html")

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

# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Critical Centers", (risk["severity"]=="Critical").sum())
col2.metric("Medium Risk Centers", (risk["severity"]=="Medium").sum())
col3.metric("Total Centers", len(risk))

# --------------------------------------------------
# DISTRICT SNAPSHOT (ROBUST)
# --------------------------------------------------
st.subheader("🏙️ Highest Risk District Snapshot")

top_district = district.sort_values("avg_risk_score", ascending=False).iloc[0]

critical_count = risk[
    (risk["district"] == top_district["district"]) &
    (risk["severity"] == "Critical")
].shape[0]

c1, c2, c3 = st.columns(3)
c1.metric("District", top_district["district"])
c2.metric("Avg Risk Score", f"{top_district['avg_risk_score']:.2f}")
c3.metric("Critical Centers", critical_count)

# --------------------------------------------------
# TOP 10 HIGH-RISK CENTERS
# --------------------------------------------------
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

# --------------------------------------------------
# EXPLAINABLE RISK
# --------------------------------------------------
st.subheader("🧠 Why is this Center Risky?")

selected = st.selectbox(
    "Select Center (by Pincode)",
    top10["pincode"].astype(str)
)

row = risk[risk["pincode"].astype(str) == selected].iloc[0]

st.info(
    f"""
    **Risk Explanation**
    - Anomaly Days: {int(row['anomaly_days'])}
    - Maximum Daily Spike: {int(row['max_spike'])}
    - Risk Score: {row['risk_score']:.2f}
    """
)

# --------------------------------------------------
# POLICY RECOMMENDATIONS PANEL (NEW)
# --------------------------------------------------
st.subheader("🏛️ Policy Recommendations")

st.dataframe(
    policy,
    use_container_width=True
)

# --------------------------------------------------
# AUTO INSIGHTS PANEL (NEW)
# --------------------------------------------------
st.subheader("💡 Key System Insights")

for _, r in insights.iterrows():
    st.markdown(f"• **{r.iloc[0]}**")

# --------------------------------------------------
# DISTRICT RISK HEATMAP (NEW, SAFE)
# --------------------------------------------------
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
        title="District-wise Average Risk Score Heatmap"
    ),
    use_container_width=True
)

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------
st.subheader("📍 Risk Score Distribution")

st.plotly_chart(
    px.histogram(risk, x="risk_score", color="severity", nbins=30),
    use_container_width=True
)

# --------------------------------------------------
# HTML REPORT DOWNLOAD
# --------------------------------------------------
st.subheader("📄 Full Audit Report")

if os.path.exists(html_fp):
    with open(html_fp, "rb") as f:
        st.download_button(
            "⬇️ Download HTML Integrity Report",
            data=f,
            file_name="aadhaar_integrity_full_report.html",
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
