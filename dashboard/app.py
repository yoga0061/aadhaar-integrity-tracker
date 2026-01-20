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
# LOAD OUTPUTS
# --------------------------------------------------
def load(fp, label):
    if not os.path.exists(fp):
        st.error(f"Missing required output: {label}")
        st.stop()
    return pd.read_parquet(fp)

risk = load(path("outputs","center_risk_scores.parquet"), "Center Risk Scores")
district = load(path("outputs","district_risk_index.parquet"), "District Risk Index")
updates = load(path("outputs","update_type_summary.parquet"), "Update Summary")

html_fp = path("outputs","aadhaar_integrity_full_report.html")

# --------------------------------------------------
# SIDEBAR FILTERS
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
# FEATURE 4: DISTRICT SUMMARY CARDS
# --------------------------------------------------
st.subheader("🏙️ District Risk Snapshot")

top_district = district.sort_values("avg_risk_score", ascending=False).iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("Highest Risk District", top_district["district"])
c2.metric("Avg Risk Score", f"{top_district['avg_risk_score']:.1f}")
c3.metric("Critical Centers", int(top_district["critical_centers"]))

# --------------------------------------------------
# FEATURE 1: TOP 10 HIGH-RISK CENTERS
# --------------------------------------------------
st.subheader("🚨 Top 10 Centers Needing Immediate Audit")

top10 = risk.sort_values("risk_score", ascending=False).head(10)

st.dataframe(
    top10[["state","district","pincode","risk_score","severity"]],
    use_container_width=True
)

# --------------------------------------------------
# FEATURE 5: DOWNLOAD TOP RISK CENTERS
# --------------------------------------------------
st.download_button(
    "⬇️ Download Top 10 Risky Centers (CSV)",
    data=top10.to_csv(index=False),
    file_name="top_10_risky_centers.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FEATURE 2: EXPLAINABLE RISK
# --------------------------------------------------
st.subheader("🧠 Why is this Center Risky?")

selected = st.selectbox(
    "Select a Center (by Pincode)",
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
# FEATURE 6: RISK COMPOSITION (EXPLAINABILITY)
# --------------------------------------------------
st.subheader("🧮 Risk Composition")

risk_components = pd.DataFrame({
    "Component": ["Anomaly Frequency", "Spike Magnitude"],
    "Contribution": [
        row["anomaly_days"],
        row["max_spike"]
    ]
})

st.plotly_chart(
    px.pie(
        risk_components,
        names="Component",
        values="Contribution",
        title="Risk Contribution Breakdown"
    ),
    use_container_width=True
)

# --------------------------------------------------
# FEATURE 3: AUTO POLICY RECOMMENDATION
# --------------------------------------------------
st.subheader("🏛️ Recommended Action for UIDAI")

if row["severity"] == "Critical":
    st.error("🔴 Immediate audit, operator verification, and system access review recommended.")
elif row["severity"] == "Medium":
    st.warning("🟠 Increase monitoring frequency and conduct random inspections.")
else:
    st.success("🟢 Routine monitoring sufficient.")

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------
st.subheader("📍 Risk Score Distribution")

st.plotly_chart(
    px.histogram(risk, x="risk_score", color="severity", nbins=30),
    use_container_width=True
)

# --------------------------------------------------
# UPDATE TYPE ANOMALIES
# --------------------------------------------------
st.subheader("⚠️ Anomalies by Update Type")

st.plotly_chart(
    px.bar(updates, x="update_type", y="anomaly_days"),
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
