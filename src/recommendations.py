import pandas as pd
from utils import path

district = pd.read_parquet(path("outputs","district_risk_index.parquet"))

rows=[]
for _,r in district.iterrows():
    if r["avg_risk_score"]>=60:
        action="Immediate audit"
    elif r["avg_risk_score"]>=40:
        action="Deploy monitoring"
    else:
        action="Routine monitoring"
    rows.append((r["state"],r["district"],action))

pd.DataFrame(rows,columns=["State","District","Recommendation"]) \
  .to_csv(path("outputs","policy_recommendations.csv"), index=False)

print("✅ Policy recommendations generated")
