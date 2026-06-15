from app.database import Session
from app.models import Set, Workout, Exercise
import pandas as pd

db = Session()

# -----------------------------
# Load workout data
# -----------------------------
data = (
    db.query(Set, Workout, Exercise)
    .join(Workout)
    .join(Exercise)
    .all()
)

rows = []

for s, w, e in data:
    rows.append({
        "date": w.date,
        "exercise": e.name,
        "reps": s.reps,
        "weight": s.weight
    })

df = pd.DataFrame(rows)

# -----------------------------
# Feature engineering
# -----------------------------
df["date"] = pd.to_datetime(df["date"])
df["week"] = df["date"].dt.to_period("W")

# Training volume
df["volume"] = df["reps"] * df["weight"]

# Weekly total volume
weekly_volume = df.groupby("week")["volume"].sum()

# -----------------------------
# Bench press progress
# -----------------------------
bench = df[df["exercise"] == "Bench Press"]

# Best bench performance each week
bench_progress = bench.groupby("week")["weight"].max()

# Starting benchmark
starting_bench = bench_progress.iloc[0]

# Best recorded performance
best_bench = bench_progress.max()

# Current week performance
current_bench = bench_progress.iloc[-1]

# Progress status
if best_bench > starting_bench:
    progress_status = "Improving"
else:
    progress_status = "Stalled"

##### Fatigue detections #####
bench_df = bench_progress.reset_index()
bench_df.columns = ["week", "max_weight"]

bench_df["rolling_avg"] = (
    bench_df["max_weight"]
    .rolling(window=3)
    .mean()
)

bench_df["drop"] = (
    bench_df["max_weight"]
    <
    (bench_df["rolling_avg"] - 1)
)

fatigue_weeks = bench_df[bench_df["drop"] == True]

if len(fatigue_weeks) > 0:
    fatigue_summary = (
        f"Performance dip detected in "
        f"{fatigue_weeks.iloc[-1]['week']}"
    )
else:
    fatigue_summary = "No major fatigue detected"

# -----------------------------
# Workout summary
# -----------------------------
summary = f"""
Workout Summary
-----------------------------

Bench Progress:
Started at: {starting_bench:.1f}kg
Best Performance: {best_bench:.1f}kg
Current Week: {current_bench:.1f}kg

Weekly Volume:
Started at: {weekly_volume.iloc[0]:.0f}
Current: {weekly_volume.iloc[-1]:.0f}

Progress Trend:
{progress_status}

Fatigue Detection:
{fatigue_summary}
"""

print(summary)