from app.database import Session
from app.models import Exercise, Set, Workout
import pandas as pd

db = Session()

data = db.query(Set, Workout, Exercise).join(Workout).join(Exercise).all()

rows = []
for s, w, e in data:
    rows.append({
        "date": w.date,
        "exercise": e.name,
        "reps": s.reps,
        "weight": s.weight,
    })

df = pd.DataFrame(rows)

df["volume"] = df["reps"] * df["weight"]
df["date"] = pd.to_datetime(df["date"])
df["week"] = df["date"].dt.to_period("W")

weekly_volume = df.groupby("week")["volume"].sum()
print(weekly_volume)

bench = df[df["exercise"] == "Bench Press"]

bench_trend = bench.groupby("week")["weight"].mean()
print(bench_trend)
print(len(weekly_volume))
print(len(df))