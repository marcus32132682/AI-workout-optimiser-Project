from fastapi import FastAPI
from pydantic import BaseModel
from scripts.ai_coach import get_ai_response
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.database import Session
from app.models import Exercise, Workout, Set
from datetime import date



app = FastAPI()

templates = Jinja2Templates(directory="templates")

class CoachRequest(BaseModel):
    question: str | None = None



class WorkoutRequest(BaseModel):
    exercise_id: int
    weight: int
    reps: int
    set_number: int

@app.get("/")
def home():
    return {"message":
            "AI workout Optimised API running"}

@app.get("/coach")
def coach_page(request: Request):

    return templates.TemplateResponse(
        request = request,
        name="index.html",
        context={"request": request},
    )


@app.post ("/ai-coach")
def ai_coach(request: CoachRequest):
    try:

        response = get_ai_response(
            request.question,
        )
        return {
            "response": response
                }
    except Exception as e:
        return {
            "response":
            f"An error occured: {str(e)}"
        }

@app.get("/workouts")
def workout_page(request: Request):
        db = Session()
        exercises = (db.query(Exercise).all())

        recent_sets = (
            db.query(Set)
            .join(Workout)
            .join(Exercise)
            .order_by(Workout.date.desc())
            .limit(5)
            .all()
        )
        return templates.TemplateResponse(
            request=request,
            name="workouts.html",
            context={"request": request, "exercises": exercises, "recent_sets": recent_sets},
    )

@app.post("/workouts")
def save_workout(form_data: WorkoutRequest):

    db = Session()

    new_workout = Workout(
        user_id = 1,
        date=date.today(),
    )

    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    new_set = Set(
        workout_id = new_workout.id,
        exercise_id = form_data.exercise_id,
        reps=form_data.reps,
        weight=form_data.weight,
        set_number=form_data.set_number
    )
    db.add(new_set)
    db.commit()
    db.close()

    return {
        "message": "Workout created"
    }