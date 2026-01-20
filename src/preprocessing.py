import pandas as pd
from utils import path, ensure_directories

ensure_directories()

df = pd.read_csv(path("data","updates.csv"), parse_dates=["date"])

daily = df.groupby(
    ["date","state","district","pincode","update_type"],
    observed=True
)["daily_updates"].sum().reset_index()

daily.to_parquet(path("outputs","daily_center_activity.parquet"), engine="pyarrow")
print("✅ Daily aggregation completed")
