import pandas as pd
from utils import path

risk = pd.read_parquet(path("outputs","center_risk_scores.parquet"))

district = risk.groupby(["state","district"]).agg(
    avg_risk_score=("risk_score","mean"),
    critical_locations=("severity",lambda x:(x=="Critical").sum()),
    total_locations=("severity","count")
).reset_index()

district["critical_ratio"] = district["critical_locations"]/district["total_locations"]
district.to_parquet(path("outputs","district_risk_index.parquet"), engine="pyarrow")
print("✅ District analysis completed")
