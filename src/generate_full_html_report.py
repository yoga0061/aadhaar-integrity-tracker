import pandas as pd
from utils import path

# ---------------- LOAD DATA ----------------
master = pd.read_csv(path("outputs", "aadhaar_integrity_master.csv"))
district = pd.read_parquet(path("outputs", "district_risk_index.parquet"))

# ---------------- SUMMARY METRICS ----------------
total_locations = master[["state","district","pincode"]].drop_duplicates().shape[0]
critical_count = (master["severity"] == "Critical").sum()
medium_count = (master["severity"] == "Medium").sum()
low_count = (master["severity"] == "Low").sum()
max_risk = round(master["risk_score"].max(), 2)

# ---------------- TOP CRITICAL LOCATIONS ----------------
top_critical = (
    master[master["severity"] == "Critical"]
    .drop_duplicates(subset=["state","district","pincode"])
    .sort_values("risk_score", ascending=False)
    .head(10)
)

# ---------------- HTML TEMPLATE ----------------
html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Aadhaar Integrity & Anomaly Monitoring Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #fafafa;
        }}
        h1 {{
            color: #B71C1C;
        }}
        h2 {{
            color: #333;
            margin-top: 40px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 15px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            font-size: 14px;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .critical {{
            background-color: #ffcccc;
        }}
        .medium {{
            background-color: #fff3cd;
        }}
        .low {{
            background-color: #e8f5e9;
        }}
        .summary-box {{
            background: #ffffff;
            padding: 20px;
            border-left: 6px solid #B71C1C;
            margin-bottom: 30px;
        }}
    </style>
</head>

<body>

<h1>🛡️ Aadhaar Integrity & Anomaly Monitoring Report</h1>

<div class="summary-box">
    <h2>📊 Executive Summary</h2>
    <ul>
        <li><b>Total Locations Monitored:</b> {total_locations}</li>
        <li><b>Critical Risk Records:</b> {critical_count}</li>
        <li><b>Medium Risk Records:</b> {medium_count}</li>
        <li><b>Low Risk Records:</b> {low_count}</li>
        <li><b>Highest Risk Score Observed:</b> {max_risk}</li>
    </ul>
</div>

<h2>🚨 Top Critical Locations (Immediate Attention Required)</h2>
{top_critical.to_html(index=False)}

<h2>🗺️ District-Level Risk Overview</h2>
{district.sort_values("avg_risk_score", ascending=False).to_html(index=False)}

<h2>📋 Full Consolidated Aadhaar Integrity Results</h2>
<p>This table contains daily Aadhaar activity, detected anomalies, risk scores, severity levels, and policy recommendations.</p>
{master.to_html(index=False)}

</body>
</html>
"""

# ---------------- SAVE FILE ----------------
with open(path("outputs", "aadhaar_integrity_full_report.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Full HTML result report generated successfully")
print("📄 File: outputs/aadhaar_integrity_full_report.html")
