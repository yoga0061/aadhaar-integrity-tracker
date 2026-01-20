import pandas as pd
from utils import path, ensure_directories

ensure_directories()

demo = pd.read_csv(path("data","api_data_aadhar_demographic_0_500000.csv"))
enrol = pd.read_csv(path("data","api_data_aadhar_enrolment_0_500000.csv"))
bio = pd.read_csv(path("data","api_data_aadhar_biometric_0_500000.csv"))

for df in [demo, enrol, bio]:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

demo["daily_updates"] = demo["demo_age_5_17"].fillna(0) + demo["demo_age_17_"].fillna(0)
enrol["daily_updates"] = enrol["age_0_5"].fillna(0) + enrol["age_5_17"].fillna(0) + enrol["age_18_greater"].fillna(0)
bio["daily_updates"] = bio["bio_age_5_17"].fillna(0) + bio["bio_age_17_"].fillna(0)

def normalize(df, t):
    out = df[["date","state","district","pincode"]].copy()
    out["update_type"] = t
    out["daily_updates"] = df["daily_updates"]
    return out

master = pd.concat([
    normalize(demo,"demographic"),
    normalize(enrol,"enrolment"),
    normalize(bio,"biometric")
])

master = master.dropna()
master = master[master["daily_updates"] >= 0]

master.to_csv(path("data","updates.csv"), index=False)
print("✅ updates.csv generated")
