import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sklearn.linear_model import LinearRegression
from database import models
from datetime import date
from typing import Dict, Any

def analyze_habits_correlation(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Query database records, aggregate daily metrics, and compute correlations.
    """
    # Fetch historical data
    habits = db.query(models.HabitRecord).filter_by(user_id=user_id).all()
    studies = db.query(models.StudyRecord).filter_by(user_id=user_id).all()
    
    if not habits:
        return {"correlations": {}, "status": "insufficient_data"}
        
    # Prepare Habit DataFrame
    habit_data = []
    for h in habits:
        habit_data.append({
            "date": h.created_at.date(),
            "habit_name": h.habit_name,
            "duration": h.duration_minutes / 60.0, # hours
            "impact": h.impact_score
        })
    df_habits = pd.DataFrame(habit_data)
    
    # Prepare Study DataFrame
    study_data = []
    for s in studies:
        study_data.append({
            "date": s.created_at.date(),
            "study_duration": s.duration_minutes / 60.0,
            "focus_score": s.focus_score
        })
    df_studies = pd.DataFrame(study_data)
    
    # Pivot habits to get daily totals
    # We want columns: Sleep_hours, Exercise_hours, ScreenTime_hours, Social_hours, Average_impact
    pivot_duration = df_habits.pivot_table(
        index="date", 
        columns="habit_name", 
        values="duration", 
        aggfunc="sum"
    ).fillna(0.0)
    
    pivot_impact = df_habits.groupby("date")["impact"].mean().to_frame("daily_impact")
    
    # Merge daily summaries
    daily_summary = pivot_duration.join(pivot_impact, how="outer").fillna(0.0)
    
    # Merge with study metrics
    if not df_studies.empty:
        daily_study_sum = df_studies.groupby("date").agg({
            "study_duration": "sum",
            "focus_score": "mean"
        })
        daily_summary = daily_summary.join(daily_study_sum, how="outer").fillna(0.0)
    else:
        daily_summary["study_duration"] = 0.0
        daily_summary["focus_score"] = 0.0

    # Ensure required columns exist
    for col in ["Sleep", "Exercise", "Screen Time", "Socializing", "study_duration", "focus_score", "daily_impact"]:
        if col not in daily_summary.columns:
            daily_summary[col] = 0.0
            
    # Calculate Pearson correlations
    corr_matrix = daily_summary[[
        "Sleep", "Exercise", "Screen Time", "Socializing", "study_duration", "focus_score", "daily_impact"
    ]].corr().fillna(0.0)
    
    return {
        "correlations": corr_matrix.to_dict(),
        "status": "success",
        "sample_size": len(daily_summary)
    }

def fit_digital_twin_models(db: Session, user_id: int):
    """
    Fits Scikit-Learn models predicting:
      1. Health Index (based on sleep, exercise, screen time, social)
      2. Focus Index (based on sleep, exercise, screen time, study duration)
    Returns trained models and intercepts/coefficients, or fallback coefficients.
    """
    habits = db.query(models.HabitRecord).filter_by(user_id=user_id).all()
    studies = db.query(models.StudyRecord).filter_by(user_id=user_id).all()
    
    # Heuristic fallback coefficients
    fallback = {
        "health": {
            "intercept": 5.0,
            "sleep_coef": 0.4,
            "exercise_coef": 0.8,
            "screen_coef": -0.3,
            "social_coef": 0.2
        },
        "focus": {
            "intercept": 6.0,
            "sleep_coef": 0.3,
            "exercise_coef": 0.2,
            "screen_coef": -0.4,
            "study_coef": -0.1  # Diminishing returns beyond sweet spot
        }
    }
    
    if len(habits) < 20:
        return fallback, True  # Use fallback
        
    try:
        # Recreate daily summary
        habit_data = [{"date": h.created_at.date(), "name": h.habit_name, "dur": h.duration_minutes/60.0, "imp": h.impact_score} for h in habits]
        df_habits = pd.DataFrame(habit_data)
        
        pivot_dur = df_habits.pivot_table(index="date", columns="name", values="dur", aggfunc="sum").fillna(0.0)
        pivot_imp = df_habits.groupby("date")["imp"].mean().to_frame("daily_impact")
        
        daily = pivot_dur.join(pivot_imp, how="outer").fillna(0.0)
        
        if studies:
            study_data = [{"date": s.created_at.date(), "dur": s.duration_minutes/60.0, "focus": s.focus_score} for s in studies]
            df_studies = pd.DataFrame(study_data)
            daily_stud = df_studies.groupby("date").agg({"dur": "sum", "focus": "mean"})
            daily = daily.join(daily_stud, how="outer").fillna(0.0)
        else:
            daily["dur"] = 0.0
            daily["focus"] = 0.0
            
        # Ensure all columns present
        for col in ["Sleep", "Exercise", "Screen Time", "Socializing", "dur", "focus", "daily_impact"]:
            if col not in daily.columns:
                daily[col] = 0.0
                
        # Fit Health Model (predict daily_impact)
        X_health = daily[["Sleep", "Exercise", "Screen Time", "Socializing"]]
        y_health = daily["daily_impact"]
        
        health_model = LinearRegression()
        health_model.fit(X_health, y_health)
        
        # Fit Focus Model (predict focus score)
        # Filter for days when study actually happened (focus > 0)
        study_days = daily[daily["focus"] > 0]
        if len(study_days) >= 5:
            X_focus = study_days[["Sleep", "Exercise", "Screen Time", "dur"]]
            y_focus = study_days["focus"]
            focus_model = LinearRegression()
            focus_model.fit(X_focus, y_focus)
            focus_coefs = {
                "intercept": float(focus_model.intercept_),
                "sleep_coef": float(focus_model.coef_[0]),
                "exercise_coef": float(focus_model.coef_[1]),
                "screen_coef": float(focus_model.coef_[2]),
                "study_coef": float(focus_model.coef_[3])
            }
        else:
            focus_coefs = fallback["focus"]
            
        trained_coefs = {
            "health": {
                "intercept": float(health_model.intercept_),
                "sleep_coef": float(health_model.coef_[0]),
                "exercise_coef": float(health_model.coef_[1]),
                "screen_coef": float(health_model.coef_[2]),
                "social_coef": float(health_model.coef_[3])
            },
            "focus": focus_coefs
        }
        return trained_coefs, False
        
    except Exception as e:
        print(f"Error training models: {e}. Falling back to default heuristics.")
        return fallback, True

def predict_scenario_scores(
    coefs: Dict[str, Any],
    sleep_hours: float,
    exercise_hours: float,
    screen_hours: float,
    social_hours: float,
    study_hours: float
) -> Dict[str, float]:
    """
    Use model coefficients to predict scores.
    Scores are bounded to [1, 10].
    """
    h = coefs["health"]
    health_pred = (
        h["intercept"] + 
        h["sleep_coef"] * sleep_hours + 
        h["exercise_coef"] * exercise_hours + 
        h["screen_coef"] * screen_hours + 
        h["social_coef"] * social_hours
    )
    
    f = coefs["focus"]
    focus_pred = (
        f["intercept"] + 
        f["sleep_coef"] * sleep_hours + 
        f["exercise_coef"] * exercise_hours + 
        f["screen_coef"] * screen_hours + 
        f["study_coef"] * study_hours
    )
    
    return {
        "health_index": float(np.clip(health_pred, 1.0, 10.0)),
        "focus_index": float(np.clip(focus_pred, 1.0, 10.0))
    }

"""
ai_engine/forecasting/habits.py

Habit & Lifestyle Analytics
-----------------------------
Consumes raw habit-tracking records from the database layer and produces
a `habits` list in the exact shape expected by
ai_engine/llm_integration/advisor.py:

    [
        {"habit_name": str, "status": str, "completion_rate": float},
        ...
    ]

Rule-based classification is used deliberately here (no ML model needed) -
it's transparent, tunable, and sufficient for the "habit analysis generated
successfully" evaluation criterion in Milestone 2.
"""

from typing import List, Dict


# Thresholds - tune these against real usage data once you have it
IMPROVING_DELTA = 5.0    # completion_rate increase (percentage points) to call it "improving"
DECLINING_DELTA = -5.0   # completion_rate decrease to call it "declining"
AT_RISK_THRESHOLD = 40.0  # completion_rate below this is flagged "at_risk"


def completion_rate(completed_count: int, total_count: int) -> float:
    """Simple percentage completion rate, guarded against divide-by-zero."""
    if total_count <= 0:
        return 0.0
    return round((completed_count / total_count) * 100, 2)


def classify_habit_status(recent_rate: float, previous_rate: float) -> str:
    """
    Compares this period's completion rate against the previous period to
    classify a habit's trajectory.

    Returns one of: "improving", "declining", "at_risk", "active", "stable"
    """
    if recent_rate < AT_RISK_THRESHOLD:
        return "at_risk"

    delta = recent_rate - previous_rate

    if delta >= IMPROVING_DELTA:
        return "improving"
    elif delta <= DECLINING_DELTA:
        return "declining"
    elif recent_rate >= 70.0:
        return "active"
    return "stable"


def analyze_habit(habit_name: str, recent_log: List[bool], previous_log: List[bool]) -> Dict:
    """
    habit_name: e.g. "Exercise"
    recent_log: list of booleans for the current period (True = done that day)
    previous_log: list of booleans for the prior period, used for trend comparison

    Returns a single habit dict matching the advisor's expected shape.
    """
    recent_rate = completion_rate(sum(recent_log), len(recent_log))
    previous_rate = completion_rate(sum(previous_log), len(previous_log)) if previous_log else recent_rate

    status = classify_habit_status(recent_rate, previous_rate)

    return {
        "habit_name": habit_name,
        "status": status,
        "completion_rate": recent_rate,
    }


def build_habits_list(raw_habit_data: Dict[str, Dict[str, List[bool]]]) -> List[Dict]:
    """
    Main entry point for this module. Takes raw habit-tracking data from the
    database layer and returns the exact `habits` list shape required by
    DigitalTwinAdvisor.set_context().

    raw_habit_data shape:
        {
            "Exercise": {
                "recent": [True, True, False, True, True, True, False],
                "previous": [True, False, False, True, True, False, False]
            },
            "Reading": {
                "recent": [...],
                "previous": [...]
            }
        }

    In production, "recent"/"previous" would be pulled from the
    Habit_Tracking table, e.g. last 7 days vs the 7 days before that.
    """
    habits_list = []
    for habit_name, logs in raw_habit_data.items():
        habits_list.append(
            analyze_habit(
                habit_name=habit_name,
                recent_log=logs.get("recent", []),
                previous_log=logs.get("previous", []),
            )
        )
    return habits_list


def identify_lifestyle_patterns(habits_list: List[Dict]) -> List[str]:
    """
    Optional helper for the dashboard's "Behavioral Patterns" panel.
    Generates short human-readable flags from the classified habits list.
    """
    patterns = []
    for h in habits_list:
        if h["status"] == "at_risk":
            patterns.append(f"{h['habit_name']} is at risk of being dropped ({h['completion_rate']}% completion).")
        elif h["status"] == "improving":
            patterns.append(f"{h['habit_name']} is trending upward - keep the momentum.")
        elif h["status"] == "declining":
            patterns.append(f"{h['habit_name']} has slipped recently compared to last period.")
    return patterns


if __name__ == "__main__":
    # Quick manual sanity check
    sample_data = {
        "Exercise": {
            "recent": [True, True, False, True, True, True, False],
            "previous": [True, False, False, True, False, False, False],
        },
        "Reading": {
            "recent": [True, True, True, True, False, True, True],
            "previous": [True, True, True, True, True, True, True],
        },
        "Meal Prep": {
            "recent": [False, False, True, False, False, False, False],
            "previous": [True, True, False, True, True, False, True],
        },
    }

    habits_result = build_habits_list(sample_data)
    print(habits_result)
    print(identify_lifestyle_patterns(habits_result))