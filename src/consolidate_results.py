import pandas as pd
from utils import path

daily = pd.read_parquet(path("outputs","daily_center_activity.parquet"))
an = pd.read_parquet(path("outputs","anomalies.parquet"))
risk = pd.read_parquet(path("outputs","center_risk_scores.parquet"))
reco = pd.read_csv(path("outputs","policy_recommendations.csv"))

final = daily.merge(
    an[["date","state","district","pincode","update_type","is_anomaly","anomaly_reason"]],
    how="left",
    on=["date","state","district","pincode","update_type"]
)

final["is_anomaly"]=final["is_anomaly"].fillna(False)
final["anomaly_reason"]=final["anomaly_reason"].fillna("Normal")

final = final.merge(
    risk[["state","district","pincode","risk_score","severity"]],
    on=["state","district","pincode"],
    how="left"
)

final = final.merge(
    reco, left_on=["state","district"], right_on=["State","District"], how="left"
).drop(columns=["State","District"])

final.to_csv(path("outputs","aadhaar_integrity_master.csv"), index=False)
print("✅ Consolidated master file created")
