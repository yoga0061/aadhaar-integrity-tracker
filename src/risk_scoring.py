import pandas as pd
from utils import path, ensure_directories

ensure_directories()

df = pd.read_parquet(path("outputs","daily_center_activity.parquet"))
an = pd.read_parquet(path("outputs","anomalies.parquet"))

key = ["state","district","pincode"]
risk = pd.DataFrame({
    "total_days": df.groupby(key).size(),
    "anomaly_days": an.groupby(key).size()
}).fillna(0)

risk["anomaly_ratio"] = risk["anomaly_days"] / risk["total_days"].replace(0,1)
risk["max_spike"] = df.groupby(key)["daily_updates"].max()

risk["risk_score"] = (
    0.6*risk["anomaly_ratio"] +
    0.4*(risk["max_spike"]/risk["max_spike"].max())
)*100

risk["severity"] = risk["risk_score"].apply(
    lambda x: "Critical" if x>=60 else "Medium" if x>=30 else "Low"
)

risk.reset_index().to_parquet(path("outputs","center_risk_scores.parquet"), engine="pyarrow")
print("✅ Risk scoring completed")
