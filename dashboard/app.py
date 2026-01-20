import sys
import os

# Allow Streamlit to access src/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import path

st.set_page_config(layout="wide")
st.title("🛡️ Aadhaar Integrity Dashboard")

# ---------- SAFE FILE CHECK ----------
def load_parquet(fp):
    if not os.path.exists(fp):
        st.error(f"Missing required file: {fp}")
        st.stop()
    return pd.read_parquet(fp)

# ---------- LOAD DATA ----------
risk_path = path("outputs", "center_risk_scores.parquet")
updates_path = path("outputs", "update_type_summary.parquet")

risk = load_parquet(risk_path)
updates = load_parquet(updates_path)

# ---------- METRICS ----------
st.metric(
    "Critical Locations",
    int((risk["severity"] == "Critical").sum())
)

# ---------- RISK DISTRIBUTION ----------
st.subheader("Center-Level Risk Distribution")
fig1 = px.histogram(
    risk,
    x="risk_score",
    color="severity",
    title="Risk Score Distribution by Severity"
)
st.plotly_chart(fig1, use_container_width=True)

# ---------- UPDATE TYPE ANOMALIES ----------
st.subheader("Anomalies by Update Type")
fig2 = px.bar(
    updates,
    x="update_type",
    y="anomaly_days",
    title="Anomaly Count by Update Category"
)
st.plotly_chart(fig2, use_container_width=True)
