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

# Import pipeline scripts
import clean_and_merge_raw_data
import preprocessing
import anomaly_detection
import risk_scoring
import district_analysis
import consolidate_results
import export_html_report

from utils import path

# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Aadhaar Integrity Dashboard", layout="wide")

st.title("🛡️ Aadhaar Integrity & Anomaly Monitoring Dashboard")

st.markdown(
    """
    <div style="
        background-color:#E3F2FD;
        padding:15px;
        border-left:6px solid #0D47A1;
        margin-bottom:20px;">
        <b>🎯 Demo Mode (Hackathon)</b><br>
        This app executes the full Aadhaar integrity analytics pipeline
        and displays results in real time using anonymized data.
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# PIPELINE EXECUTION (CACHED)
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def run_pipeline():
    """
    Runs the complete analytics pipeline.
    Cached so it runs only once unless inputs change.
    """
    clean_and_merge_raw_data.main()
    preprocessing.main()
    anomaly_detection.main()
    risk_scoring.main()
    district_analysis.main()
    consolidate_results.main()
    export_html_report.main()

# --------------------------------------------------
# RUN BUTTON
# --------------------------------------------------
if st.button("▶️ Run Aadhaar Integrity Analysis"):
    with st.spinner("Running full analytics pipeline..."):
        run_pipeline()
    st.success("✅ Analysis completed successfully!")

# --------------------------------------------------
# CHECK OUTPUTS
# --------------------------------------------------
risk_fp = path("outputs", "center_risk_scores.parquet")
district_fp = path("outputs", "district_risk_index.parquet")
updates_fp = path("outputs", "update_type_summary.parquet")
html_fp = path("outputs", "aadhaar_integrity_full_report.html")

if not os.path.exists(risk_fp):
    st.info("Click ▶️ Run Aadhaar Integrity Analysis to generate outputs.")
    st.stop()

# --------------------------------------------------
# LOAD OUTPUTS
# --------------------------------------------------
risk = pd.read_parquet(risk_fp)
district = pd.read_parquet(district_fp)
updates = pd.read_parquet(updates_fp)

# --------------------------------------------------
# METRICS
# --------------------------------------------------
st.subheader("📊 Key Indicators")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Critical Locations", (risk["severity"] == "Critical").sum())
with col2:
    st.metric("Medium Risk Locations", (risk["severity"] == "Medium").sum())
with col3:
    st.metric("Total Centers", len(risk))

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------
st.subheader("📍 Center-Level Risk Distribution")
fig1 = px.histogram(risk, x="risk_score", color="severity", nbins=30)
st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# DISTRICT TABLE
# --------------------------------------------------
st.subheader("🗺️ District-Level Risk Overview")
st.dataframe(
    district.sort_values("avg_risk_score", ascending=False),
    use_container_width=True
)

# --------------------------------------------------
# UPDATE TYPE ANOMALIES
# --------------------------------------------------
st.subheader("⚠️ Anomalies by Update Type")
fig2 = px.bar(updates, x="update_type", y="anomaly_days")
st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# HTML REPORT DOWNLOAD
# --------------------------------------------------
st.subheader("📄 Audit-Ready Report")
if os.path.exists(html_fp):
    with open(html_fp, "rb") as f:
        st.download_button(
            "⬇️ Download Full HTML Audit Report",
            data=f,
            file_name="aadhaar_integrity_full_report.html",
            mime="text/html"
        )

# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------
with st.expander("🔍 View Sample Center Risk Data"):
    st.dataframe(risk.head(20))
