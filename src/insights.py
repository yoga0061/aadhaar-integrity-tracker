import pandas as pd
from utils import path

risk = pd.read_parquet(path("outputs", "center_risk_scores.parquet"))

insights = [
    ("Locations Monitored", len(risk)),
    ("Critical Locations", (risk["severity"] == "Critical").sum()),
    ("Highest Risk Score", round(risk["risk_score"].max(), 2))
]

pd.DataFrame(insights, columns=["Metric", "Value"]) \
  .to_csv(path("outputs", "insights.csv"), index=False)

print("✅ Insights generated")
