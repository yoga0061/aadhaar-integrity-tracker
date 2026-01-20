import pandas as pd
from utils import path

df = pd.read_csv(path("outputs","aadhaar_integrity_master.csv"))

html = f"""
<html><head><title>Aadhaar Integrity Report</title></head>
<body>
<h1>Aadhaar Integrity Monitoring Report</h1>
<p>Total records: {len(df)}</p>
{df.head(50).to_html(index=False)}
</body></html>
"""

with open(path("outputs","aadhaar_integrity_report.html"),"w",encoding="utf-8") as f:
    f.write(html)

print("✅ HTML report generated")
