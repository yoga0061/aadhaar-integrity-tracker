import pandas as pd
from sklearn.ensemble import IsolationForest
from utils import path, ensure_directories

ensure_directories()

df = pd.read_parquet(path("outputs","daily_center_activity.parquet"))

mean, std = df["daily_updates"].mean(), df["daily_updates"].std()

df["z_anomaly"] = ((df["daily_updates"]-mean)/std).abs() > 3
iso = IsolationForest(contamination=0.01, random_state=42)
df["iforest_anomaly"] = iso.fit_predict(df[["daily_updates"]]) == -1
df["is_anomaly"] = df["z_anomaly"] | df["iforest_anomaly"]

def reason(r):
    if r["daily_updates"] > mean + 5*std:
        return "Extreme spike"
    if r["z_anomaly"]:
        return "Statistical deviation"
    if r["iforest_anomaly"]:
        return "Isolation Forest outlier"
    return "Normal"

df["anomaly_reason"] = df.apply(reason, axis=1)

an = df[df["is_anomaly"]]
an.to_parquet(path("outputs","anomalies.parquet"), engine="pyarrow")

an.groupby("update_type").size().reset_index(name="anomaly_days") \
  .to_parquet(path("outputs","update_type_summary.parquet"), engine="pyarrow")

print("🚨 Anomaly detection completed")
