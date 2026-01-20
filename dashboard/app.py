import sys
import os

# --------------------------------------------------
# PATH SETUP (allow Streamlit to access src/)
# --------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(BASE_DIR, "..", "src")
sys.path.append(SRC_DIR)

import streamlit as st
import pandas as pd
import plotly.express as px

from utils import path
from pipeline.run_pipeline import run_analysis_pipeline   # ✅ your pipeline

# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Aadhaar Integrity Dashboard",
    layout="wide"
)

st.title("🛡️ Aadhaar Integrity Dashboard")

# --------------------------------------------------
# ENSURE OUTPUT DIRECTORY EXISTS
# --------------------------------------------------
os.makedirs(path("outputs"), exist_ok=True)

# --------------------------------------------------
# SAFE LOAD OR GENERATE FUNCTION
# --------------------------------------------------
def load_or_generate(fp: str):
    """
    Loads a parquet file.
    If missing (Streamlit Cloud), runs pipeline to generate outputs.
    """
    if not os.path.exists(fp):
        with st.spinner("🔄 Generating analytics data (first-time setup)..."):
            run_analysis_pipeline()

    if not os.path.exists(fp):
        st.error(f"Pipeline did not generate required file: {fp}")
        st.stop()

    return pd.read_parquet(fp)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
risk_path = path("outputs", "center_risk_scores.parquet")
updates_path = path("outputs", "update_type_summary.parquet")

risk = load_or_generate(risk_path)
updates = load_or_generate(updates_path)

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
# DATA PREVIEW (OPTIONAL, JUDGES LOVE THIS)
# --------------------------------------------------
with st.expander("🔍 View Sample Risk Data"):
    st.dataframe(risk.head(20))

with st.expander("🔍 View Update Summary"):
    st.dataframe(updates.head(20))
