from app.database import Session
from app.models import User, Exercise, Workout, Set
from datetime import date

def get_or_create_user(db, name="Albert"):
    user = db.query(User).filter_by(name="Albert").first()
    if not user:
        user = User(name="Albert")
        db.add(user)
        db.commit()
    return user

def create_workout(db, user):
    workout = Workout(user=user)
    db.add(workout)
    db.commit()
    return workout

def get_or_create_exercise(db, name):
    name = name.title()
    exercise = db.query(Exercise).filter_by(name=name).first()
    if not exercise:
        exercise = Exercise(name=name)
        db.add(exercise)
        db.commit()
    return exercise

def log_set(db, workout, exercise, reps, weight):
    set_count = db.query(Set).filter_by(workout_id=workout.id).count()
    new_set = Set(
        workout = workout,
        exercise = exercise,
        reps = reps,
        weight = weight,
        set_number = set_count + 1
        )
    db.add(new_set)
    db.commit()


def run():
    db = Session()

    user = get_or_create_user(db)
    workout= create_workout(db, user)

    while True:
        exercise_name = input("Enter exercise (or 'q' to quit): ")
        if exercise_name.lower() == "q":
            break

        exercise = get_or_create_exercise(db, exercise_name)

        unit_choice = input("Select unit (1 = kg, 2 = lbs): ")
        if unit_choice not in ["1", "2"]:
            print("Invalid unit")
            continue

        try:
            weight = float(input("Enter weight: "))
            reps = int(input("Enter reps: "))
        except ValueError:
            print("Invalid input")
            continue

        if unit_choice == "2":
            weight *= 0.453592

        log_set(db, workout, exercise, reps, weight)

        print("Set logged!\n")

    print("Workout saved!")


if __name__ == "__main__":
    run()
