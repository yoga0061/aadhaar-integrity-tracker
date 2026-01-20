import sys
import os
import time

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
        Upload Aadhaar activity data → Auto-generate integrity intelligence.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ Aadhaar Sentinel – Integrity Intelligence Dashboard")

# --------------------------------------------------
# SIDEBAR: FILE UPLOAD
# --------------------------------------------------
st.sidebar.header("📤 Upload Data (Optional)")

uploaded_files = st.sidebar.file_uploader(
    "Upload Aadhaar Analysis Files",
    type=["parquet", "csv"],
    accept_multiple_files=True
)

# --------------------------------------------------
# UTILITIES
# --------------------------------------------------
def save_uploaded_files(files):
    os.makedirs(path("outputs"), exist_ok=True)
    for f in files:
        with open(path("outputs", f.name), "wb") as out:
            out.write(f.getbuffer())

def auto_generate_outputs(progress):
    """
    Generate missing outputs from daily_center_activity.parquet
    """
    activity_fp = path("outputs", "daily_center_activity.parquet")

    if not os.path.exists(activity_fp):
        st.error("❌ daily_center_activity.parquet required to auto-generate outputs")
        return

    progress.progress(10)
    time.sleep(0.3)

    activity = pd.read_parquet(activity_fp)

    # ------------------ ANOMALIES ------------------
    progress.progress(25)
    anomalies = activity[
        activity["daily_updates"] >
        activity["daily_updates"].mean() + 3 * activity["daily_updates"].std()
    ].copy()
    anomalies["anomaly_reason"] = "Volume Spike"
    anomalies.to_parquet(path("outputs","anomalies.parquet"), index=False)

    # ------------------ CENTER RISK ----------------
    progress.progress(45)
    grp = activity.groupby(["state","district","pincode"])

    risk = grp["daily_updates"].agg(
        anomaly_days=lambda x: (x > x.mean() + 3*x.std()).sum(),
        max_spike="max",
        total_days="count"
    ).reset_index()

    risk["risk_score"] = (
        0.6 * (risk["anomaly_days"] / risk["total_days"]) +
        0.4 * (risk["max_spike"] / risk["max_spike"].max())
    ) * 100

    risk["severity"] = risk["risk_score"].apply(
        lambda x: "Critical" if x >= 70 else "Medium" if x >= 30 else "Low"
    )

    risk.to_parquet(path("outputs","center_risk_scores.parquet"), index=False)

    # ------------------ DISTRICT RISK --------------
    progress.progress(70)
    district = risk.groupby(["state","district"]).agg(
        avg_risk_score=("risk_score","mean"),
        total_centers=("pincode","count")
    ).reset_index()

    district.to_parquet(path("outputs","district_risk_index.parquet"), index=False)

    progress.progress(100)
    time.sleep(0.3)

# --------------------------------------------------
# RUN ANALYSIS BUTTON
# --------------------------------------------------
if uploaded_files:
    st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded")

    if st.sidebar.button("▶ Run Integrity Analysis"):
        save_uploaded_files(uploaded_files)

        progress = st.sidebar.progress(0)
        st.sidebar.info("Running integrity analytics...")

        required = [
            "center_risk_scores.parquet",
            "anomalies.parquet",
            "district_risk_index.parquet"
        ]

        missing = [
            f for f in required
            if not os.path.exists(path("outputs", f))
        ]

        if missing:
            auto_generate_outputs(progress)

        st.sidebar.success("✅ Analysis completed")
        st.experimental_rerun()

# --------------------------------------------------
# SAFE LOADERS
# --------------------------------------------------
def load_parquet(fp, label):
    if not os.path.exists(fp):
        st.warning(f"{label} not found")
        return None
    return pd.read_parquet(fp)

def load_csv(fp):
    if not os.path.exists(fp):
        return None
    return pd.read_csv(fp)

# --------------------------------------------------
# LOAD OUTPUTS
# --------------------------------------------------
risk = load_parquet(path("outputs","center_risk_scores.parquet"), "Center Risk Scores")
district = load_parquet(path("outputs","district_risk_index.parquet"), "District Risk Index")
activity = load_parquet(path("outputs","daily_center_activity.parquet"), "Daily Activity")
anomalies = load_parquet(path("outputs","anomalies.parquet"), "Anomalies")
audit = load_csv(path("outputs","audit_report.csv"))
policy = load_csv(path("outputs","policy_recommendations.csv"))
insights = load_csv(path("outputs","insights.csv"))

html_fp = path("outputs","aadhaar_integrity_report.html")

if risk is None or district is None:
    st.info("📥 Upload data to generate integrity insights")
    st.stop()

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Critical Centers", (risk["severity"]=="Critical").sum())
c2.metric("Medium Risk Centers", (risk["severity"]=="Medium").sum())
c3.metric("Total Centers", len(risk))

# --------------------------------------------------
# DISTRICT HEATMAP + TOP 5 + LEGEND
# --------------------------------------------------
st.subheader("🗺️ District Risk Intelligence")

left, right = st.columns([3,1])

with left:
    heat_df = district.pivot_table(
        index="district",
        columns="state",
        values="avg_risk_score",
        fill_value=0
    )

    fig = px.imshow(
        heat_df,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        zmin=heat_df.values.min(),
        zmax=heat_df.values.max(),
        title="District-wise Average Risk Score"
    )

    fig.update_traces(
        hovertemplate=
        "<b>District:</b> %{y}<br>"
        "<b>State:</b> %{x}<br>"
        "<b>Avg Risk:</b> %{z:.2f}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### 🚨 Top 5 High-Risk Districts")
    top5 = district.sort_values("avg_risk_score", ascending=False).head(5)
    for _, r in top5.iterrows():
        st.markdown(f"**{r['district']}** ({r['state']}) – `{r['avg_risk_score']:.2f}`")

    st.markdown("---")
    st.markdown("### 🎯 Severity Legend")
    st.markdown("🔴 **Critical** – Immediate audit")
    st.markdown("🟠 **Medium** – Increased monitoring")
    st.markdown("🟢 **Low** – Routine observation")

# --------------------------------------------------
# AUTO INSIGHTS
# --------------------------------------------------
if insights is not None:
    st.subheader("💡 Key System Insights")
    for _, r in insights.iterrows():
        st.markdown(f"• **{r.iloc[0]}**")

# --------------------------------------------------
# HTML REPORT DOWNLOAD
# --------------------------------------------------
if os.path.exists(html_fp):
    st.subheader("📄 Full Audit Report")
    with open(html_fp, "rb") as f:
        st.download_button(
            "⬇️ Download HTML Integrity Report",
            f,
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
    Aadhaar Sentinel • Upload → Analyze → Audit • UIDAI Hackathon 2026
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
