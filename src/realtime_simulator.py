import pandas as pd, time
from sklearn.ensemble import IsolationForest
from utils import path

df = pd.read_parquet(path("outputs","daily_center_activity.parquet")).sort_values("date")
iso = IsolationForest(contamination=0.01, random_state=42)

print("🔴 Real-time alert simulation\n")
for d, chunk in df.groupby("date"):
    alerts = chunk[iso.fit_predict(chunk[["daily_updates"]]) == -1]
    if not alerts.empty:
        print(f"⚠️ {d.date()} | Alerts: {len(alerts)}")
        print(alerts[["state","district","pincode","update_type","daily_updates"]])
        print("-"*50)
    time.sleep(0.1)
