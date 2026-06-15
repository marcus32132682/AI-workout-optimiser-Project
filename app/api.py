from fastapi import FastAPI
from pydantic import BaseModel
from scripts.ai_coach import get_ai_response
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class CoachRequest(BaseModel):
    question: str | None = None

@app.get("/")
def home():
    return {"message":
            "AI workout Optimised API running"}

@app.get("/coach")
def coach_page(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post ("/ai-coach")
def ai_coach(request: CoachRequest):

    response = get_ai_response(
        request.question,
    )
    return {
        "response": response
            }