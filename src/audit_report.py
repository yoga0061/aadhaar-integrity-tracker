import pandas as pd
from utils import path

risk = pd.read_parquet(path("outputs","center_risk_scores.parquet"))
an = pd.read_parquet(path("outputs","anomalies.parquet"))

report = an.merge(risk.reset_index(), on=["state","district","pincode"], how="left")
report["auditor_status"]="Pending Review"
report.to_csv(path("outputs","audit_report.csv"), index=False)

print("✅ Audit report exported")
