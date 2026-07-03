from asyncio.windows_events import NULL

from sqlalchemy import null

from app.database import Session
from app.models import Set, Workout, Exercise
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os

from scripts.workout_summary import best_bench

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)
def get_ai_response(question=None):
    db = Session()

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
            "weight": s.weight,
        })

    df = pd.DataFrame(rows)


    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.to_period("W")

    df["volume"] = (df["reps"] * df["weight"])
    weekly_volume = (
        df.groupby("week")["volume"]
        .sum()
        )

    average_weekly_volume = round(
        weekly_volume.mean(),
        0
    )

    bench = df[
        df["exercise"] == "Bench Press"
    ]

    bench_progress = (
        bench.groupby("week")["weight"]
        .max()
    )

    starting_bench = (
        bench_progress.iloc[0]
    )

    best_bench = (
        bench_progress.max()
    )

    current_bench = (
        bench_progress.iloc[-1]
    )

    total_workouts = (
        df["date"]
        .nunique()
    )

    total_exercises = (
        df["exercise"]
        .nunique()
    )

    bench_df = (
        bench_progress
        .reset_index()
    )

    bench_df.columns = [
        "week",
        "max_weight"
    ]

    bench_df["rolling_avg"] = (
        bench_df["max_weight"]
        .rolling(window=3)
        .mean()
    )

    bench_df["drop"] = (
        bench_df["max_weight"]
        <
        (
            bench_df["rolling_avg"]
            - 1
        )
    )

    fatigue_weeks = bench_df[
        bench_df["drop"] == True
    ]

    if len(fatigue_weeks) > 0:

        latest_fatigue_week = (
            fatigue_weeks["week"]
            .iloc[-1]
        )

        fatigue_summary = (
            f"Fatigue detected in "
            f"{latest_fatigue_week}"
        )

    else:
        fatigue_summary = (
            "No major fatigue detected"
        )
    fatigue_count = len(fatigue_weeks)
#############################
    volume_change = (
        (
            weekly_volume.iloc[-1]
            - weekly_volume.iloc[0]
        )
        / weekly_volume.iloc[0]
    ) * 100

    bench_change = (
        (
            best_bench
            - starting_bench
        )
        / starting_bench
    ) * 100


    summary = f"""
    Workout Summary
    
    General Statistics:
    Total Workouts: {total_workouts}
    Exercises Tracked: {total_exercises}
    Average Weekly Volume: {average_weekly_volume:.0f}
    
    Bench Progress:
    Started at: {starting_bench:.1f}kg
    Best Performance: {best_bench:.1f}kg
    Current Week: {current_bench:.1f}kg
    Strength Increase: {bench_change:.1f}%

    Weekly Volume:
    Started at: {weekly_volume.iloc[0]:.0f}
    Current: {weekly_volume.iloc[-1]:.0f}
    Volume Increase: {volume_change:.1f}%

    Fatigue: 
    {fatigue_summary}
    Fatigue weeks detected: {fatigue_count}
    
    """

###################################
    ###while True:
      #  Choice = input("Do you want to ask your AI coach a question regarding anything to do with your progression or training? (y/n): ").lower()
       # if Choice == "y":
       #     question = input("How can i help?")
        #    break
       # elif Choice == "n":
           # question = None
        #    break
#        else:
           # print("Please enter y or n")





    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an experienced strength coach "
                    "specialising in progressive overload, "
                    "fatigue management, and recovery.\n\n"

                    "Only use the workout data provided."
                    "When giving recommendations.\n\n"

                    "Avoid generic advice unless supported "
                    "by the data.\n\n"

                    "Focus on:\n"
                    "- strength progression\n"
                    "- fatigue trends\n"
                    "- recovery considerations\n"
                    "- practical next steps\n\n"

                    "Keep responses concise and evidence-based.\n\n"
                    
                    "you may ONLY answer questions related to: "
                    "training, gym performance, strength "
                    "progression, fatigue, recovery, "
                    "workout volume, and fitness trends.\n\n"
    
                    "If a question is unrelated to fitness "
                    "or workout progress, politely refuse "
                    "to answer and explain that you only "
                    "support workout-related questions."
                    "If question is set to none then ignore it like a question wasn't asked.\n\n"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here is my workout data:\n"
                    f"{summary}\n\n"
                    f"Question: {question}\n\n"
                    f"Answer only using the workout data provided.\n\n"
                    f"Give me recommendations.\n\n"
                )
            }
        ]
    )
    return response.choices[0].message.content

print("\nAI coach:\n")
