from app.database import Session
from app.models import User, Exercise, Workout, Set
from datetime import date

db = Session()

user = User(name="Albert")
bench = Exercise(name="Bench Press")
workout = Workout(user=user, date=date.today())

set1 = Set(workout=workout, exercise=bench, reps=8, weight=80, set_number=1)
set2 = Set(workout=workout, exercise=bench, reps=6, weight=85, set_number=2)

db.add(user)
db.add(bench)
db.add(workout)
db.add(set1)
db.add(set2)

db.commit()
print("Data inserted")