import sys
import os

# --------------------------------------------------
# PATH SETUP (CRITICAL)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

sys.path.insert(0, SRC_DIR)

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px

# Import your existing analysis scripts from src/
import preprocessing
import clean_and_merge_raw_data
import anomaly_detection
import risk_scoring
import consolidate_results

# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Aadhaar Integrity Dashboard",
    layout="wide"
)

st.title("🛡️ Aadhaar Integrity Dashboard")

# --------------------------------------------------
# OUTPUT PATHS
# --------------------------------------------------
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CENTER_RISK_FP = os.path.join(OUTPUT_DIR, "center_risk_scores.parquet")
UPDATE_SUMMARY_FP = os.path.join(OUTPUT_DIR, "update_type_summary.parquet")

# --------------------------------------------------
# PIPELINE RUNNER (CORE FIX)
# --------------------------------------------------
def run_analysis_pipeline():
    """
    Runs the full Aadhaar Integrity analytics pipeline.
    Must generate required parquet files in outputs/.
    """

    st.info("⚙️ Running analytics pipeline (first-time setup)...")

    # Each of these files MUST have a run() function
    preprocessing.run()
    clean_and_merge_raw_data.run()
    anomaly_detection.run()
    risk_scoring.run()              # → center_risk_scores.parquet
    consolidate_results.run()       # → update_type_summary.parquet

    st.success("✅ Analytics pipeline completed")

# --------------------------------------------------
# SAFE LOAD OR GENERATE
# --------------------------------------------------
def load_or_generate(fp: str):
    if not os.path.exists(fp):
        with st.spinner("🔄 Generating analytics data..."):
            run_analysis_pipeline()

    if not os.path.exists(fp):
        st.error(f"Required file not generated: {fp}")
        st.stop()

    return pd.read_parquet(fp)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
risk = load_or_generate(CENTER_RISK_FP)
updates = load_or_generate(UPDATE_SUMMARY_FP)

# --------------------------------------------------
# METRICS
# --------------------------------------------------
st.subheader("📊 Key Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Critical Locations",
        int((risk["severity"] == "Critical").sum())
    )

with col2:
    st.metric(
        "High Risk Centers",
        int((risk["severity"] == "High").sum())
    )

with col3:
    st.metric(
        "Total Centers Analysed",
        len(risk)
    )

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------
st.subheader("📍 Center-Level Risk Distribution")

fig1 = px.histogram(
    risk,
    x="risk_score",
    color="severity",
    title="Risk Score Distribution by Severity",
    nbins=30
)

st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# UPDATE TYPE ANOMALIES
# --------------------------------------------------
st.subheader("⚠️ Anomalies by Update Type")

fig2 = px.bar(
    updates,
    x="update_type",
    y="anomaly_days",
    title="Anomaly Count by Update Category",
    color="update_type"
)

st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# DATA PREVIEW (OPTIONAL, GOOD FOR JUDGES)
# --------------------------------------------------
with st.expander("🔍 View Sample Risk Data"):
    st.dataframe(risk.head(20))

with st.expander("🔍 View Update Summary"):
    st.dataframe(updates.head(20))
