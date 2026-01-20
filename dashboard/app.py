import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest

st.set_page_config(layout="wide")
st.title("🛡️ Aadhaar Integrity & Anomaly Monitoring Dashboard")

st.markdown("""
**🎯 Demo Mode**  
This app generates all analytics dynamically during execution using anonymized data.
""")

# ---------------- LOAD RAW DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/updates.csv")

# ---------------- RUN ANALYSIS ----------------
@st.cache_data
def run_analysis(df):
    # Aggregate
    daily = df.groupby(["state","district","pincode","update_type"])["daily_updates"].sum().reset_index()

    # Anomaly detection
    iso = IsolationForest(contamination=0.01, random_state=42)
    daily["anomaly"] = iso.fit_predict(daily[["daily_updates"]]) == -1

    # Risk scoring
    risk = daily.groupby(["state","district","pincode"]).agg(
        total_days=("daily_updates","count"),
        anomaly_days=("anomaly","sum"),
        max_spike=("daily_updates","max")
    ).reset_index()

    risk["risk_score"] = (
        0.6 * (risk["anomaly_days"] / risk["total_days"]) +
        0.4 * (risk["max_spike"] / risk["max_spike"].max())
    ) * 100

    risk["severity"] = risk["risk_score"].apply(
        lambda x: "Critical" if x >= 60 else "Medium" if x >= 30 else "Low"
    )

    return daily, risk

# ---------------- UI ----------------
if st.button("▶️ Run Integrity Analysis"):
    with st.spinner("Running analytics..."):
        df = load_data()
        daily, risk = run_analysis(df)
    st.success("Analysis completed")

    st.metric("Critical Locations", (risk["severity"]=="Critical").sum())

    st.plotly_chart(
        px.histogram(risk, x="risk_score", color="severity"),
        use_container_width=True
    )

    st.subheader("District Risk Overview")
    st.dataframe(
        risk.groupby(["state","district"])["risk_score"].mean().reset_index()
        .sort_values("risk_score", ascending=False),
        use_container_width=True
    )
