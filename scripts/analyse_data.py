from app.database import Session
from app.models import Exercise, Set, Workout
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
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
print(bench.head(20))

bench_trend = bench.groupby("week")["weight"].max()
print(bench_trend)
print(len(weekly_volume))
print(len(df))



df["one_rm"] = df["weight"] * (1+ df["reps"] / 30)

X = df[["weight", "reps"]] # Sets the input X to weight and reps from the dataframe
y = df["one_rm"] # Sets the output of one_rm to y

X_train, X_test, y_train, y_test = train_test_split( # Creates a test/train split for the data
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression() # Sets the model to linear regression
model.fit(X_train, y_train) #

predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
print("Mae:", mae)


bench_df = bench_trend.reset_index()
bench_df.columns = ["week", "avg_weight"]
fatigue_X = bench_df[["avg_weight"]]

bench_df["rolling_avg"] = bench_df["avg_weight"].rolling(window=3).mean() # Creates a rolling average of the weight for the last 3 weeks
bench_df["drop"] = bench_df["avg_weight"] < (bench_df["rolling_avg"] - 1) # indicates the drop in weight from the average to help identify fatigue

drops = bench_df[bench_df["drop"] == True]
print(drops)


print(bench_df)
print(bench_df[["week", "avg_weight", "rolling_avg"]])