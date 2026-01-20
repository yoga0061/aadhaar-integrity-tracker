import sys
import os

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.append(SRC_DIR)

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import path

# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Aadhaar Sentinel – Integrity Dashboard",
    layout="wide"
)

# --------------------------------------------------
# DEMO MODE BANNER
# --------------------------------------------------
st.markdown(
    """
    <div style="
        background-color:#E3F2FD;
        padding:16px;
        border-left:6px solid #0D47A1;
        margin-bottom:20px;
        font-size:16px;">
        <b>🎯 Demo Mode – UIDAI Hackathon Evaluation</b><br>
        This dashboard visualizes <b>precomputed, anonymized Aadhaar integrity analytics</b>.
        Heavy anomaly detection and risk scoring pipelines are executed offline and consumed here
        for stable, audit-ready monitoring.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ Aadhaar Sentinel: Center-Level Integrity Intelligence Dashboard")

# --------------------------------------------------
# SAFE FILE LOADER
# --------------------------------------------------
def load_file(fp: str, label: str):
    if not os.path.exists(fp):
        st.error(f"❌ Missing required output: {label}")
        st.stop()
    return fp

# --------------------------------------------------
# OUTPUT FILE PATHS
# --------------------------------------------------
risk_fp = load_file(
    path("outputs", "center_risk_scores.parquet"),
    "Center Risk Scores"
)

district_fp = load_file(
    path("outputs", "district_risk_index.parquet"),
    "District Risk Index"
)

updates_fp = load_file(
    path("outputs", "update_type_summary.parquet"),
    "Update Type Summary"
)

html_fp = path("outputs", "aadhaar_integrity_full_report.html")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return (
        pd.read_parquet(risk_fp),
        pd.read_parquet(district_fp),
        pd.read_parquet(updates_fp),
    )

risk, district, updates = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Filters")

state_filter = st.sidebar.multiselect(
    "Select State(s)",
    sorted(risk["state"].unique())
)

severity_filter = st.sidebar.multiselect(
    "Select Severity",
    ["Low", "Medium", "Critical"],
    default=["Critical", "Medium"]
)

filtered_risk = risk.copy()

if state_filter:
    filtered_risk = filtered_risk[filtered_risk["state"].isin(state_filter)]

if severity_filter:
    filtered_risk = filtered_risk[filtered_risk["severity"].isin(severity_filter)]

# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------
st.subheader("📊 Key Integrity Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Critical Centers",
        int((filtered_risk["severity"] == "Critical").sum())
    )

with col2:
    st.metric(
        "Medium Risk Centers",
        int((filtered_risk["severity"] == "Medium").sum())
    )

with col3:
    st.metric(
        "Total Centers Monitored",
        len(filtered_risk)
    )

# --------------------------------------------------
# CENTER RISK DISTRIBUTION
# --------------------------------------------------
st.subheader("📍 Center-Level Risk Distribution")

fig1 = px.histogram(
    filtered_risk,
    x="risk_score",
    color="severity",
    nbins=30,
    title="Risk Score Distribution by Severity"
)

st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# DISTRICT RISK TABLE
# --------------------------------------------------
st.subheader("🗺️ District-Level Risk Overview")

district_view = (
    district.sort_values("avg_risk_score", ascending=False)
)

st.dataframe(
    district_view,
    use_container_width=True
)

# --------------------------------------------------
# UPDATE TYPE ANOMALIES
# --------------------------------------------------
st.subheader("⚠️ Anomalies by Update Category")

fig2 = px.bar(
    updates,
    x="update_type",
    y="anomaly_days",
    title="Detected Anomalies by Update Type"
)

st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# HTML REPORT DOWNLOAD
# --------------------------------------------------
st.subheader("📄 Audit-Ready Report")

if os.path.exists(html_fp):
    with open(html_fp, "rb") as f:
        st.download_button(
            label="⬇️ Download Full HTML Audit Report",
            data=f,
            file_name="aadhaar_integrity_full_report.html",
            mime="text/html"
        )
else:
    st.warning("HTML audit report not found.")

# --------------------------------------------------
# DATA EXPLORATION (OPTIONAL)
# --------------------------------------------------
with st.expander("🔍 View Sample Center-Level Risk Data"):
    st.dataframe(filtered_risk.head(50))

with st.expander("🔍 View Update Type Summary Data"):
    st.dataframe(updates.head(20))

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    """
    <hr>
    <center>
    <small>
    Aadhaar Sentinel – UIDAI Hackathon 2026<br>
    Privacy-by-design • Anonymized metadata • Audit-first architecture
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
