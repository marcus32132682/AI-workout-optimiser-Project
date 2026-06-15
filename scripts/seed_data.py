from app.database import Session
from app.models import User, Exercise, Workout, Set
from datetime import date, timedelta
import random

# create session
db = Session()


# 1. USER SETUP

user = db.query(User).filter_by(name="Albert").first()
if not user:
    user = User(name="Albert")
    db.add(user)
    db.commit()


# 2. EXERCISES SETUP

exercises = ["Bench Press", "Squat", "Deadlift"]

exercise_objects = {}
for name in exercises:
    ex = db.query(Exercise).filter_by(name=name).first()
    if not ex:
        ex = Exercise(name=name)
        db.add(ex)
        db.commit()
    exercise_objects[name] = ex

# 3. GENERATE DATA OVER TIME

base_weights = {
    "Bench Press": 60,
    "Squat": 80,
    "Deadlift": 100
}

start_date = date.today() - timedelta(days=90)

for i in range(90):
    workout = Workout(
        user=user,
        date=start_date + timedelta(days=i)
    )
    db.add(workout)
    db.commit()

    bad_week = (i // 7) == 5
    if bad_week:
        workout_fatigue = 100
    else:
        workout_fatigue = 0

    for ex_name, ex in exercise_objects.items():
        base_weight = base_weights.get(ex_name.title(), 50)
        progression = i * 0.2

        weight = base_weight + progression - workout_fatigue + random.uniform(-2, 2)

        for set_num in range(1, 4):  # 3 sets per exercise

            reps = random.choice([5, 6, 8, 10])

            new_set = Set(
                workout=workout,
                exercise=ex,
                reps=reps,
                weight=round(weight, 1),
                set_number=set_num
            )

            db.add(new_set)

db.commit()

print("Data seeded successfully!")