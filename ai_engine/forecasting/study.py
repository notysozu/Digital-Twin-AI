# """
# ai_engine/forecasting/study.py

# Study & Productivity Intelligence
# ----------------------------------
# Consumes raw study/activity records from the database layer and produces a
# `study_summary` dict in the exact shape expected by
# ai_engine/llm_integration/advisor.py:

#     {
#         "avg_weekly_hours": float,
#         "performance_trend": str   # "improving" | "declining" | "stable"
#     }

# Uses simple linear-regression-style slope detection on performance_score
# over time - no heavy ML dependency required, fully explainable for a demo.
# """

# from typing import List, Dict, Optional


# def average_weekly_hours(records: List[Dict], weeks: int = 4) -> float:
#     """
#     records: list of {"study_hours": float, "activity_date": ...}
#     Returns average study hours per week over the trailing `weeks` window.
#     Assumes records are daily entries; adjust divisor if your DB stores
#     weekly aggregates instead.
#     """
#     if not records:
#         return 0.0

#     recent = records[-(weeks * 7):] if len(records) > weeks * 7 else records
#     total_hours = sum(r.get("study_hours", 0) for r in recent)
#     num_weeks = max(len(recent) / 7, 1)
#     return round(total_hours / num_weeks, 2)


# def _simple_slope(values: List[float]) -> float:
#     """
#     Computes the slope of a best-fit line through `values` (indexed 0..n-1)
#     using ordinary least squares. Returns 0.0 if fewer than 2 points.
#     """
#     n = len(values)
#     if n < 2:
#         return 0.0

#     x_vals = list(range(n))
#     x_mean = sum(x_vals) / n
#     y_mean = sum(values) / n

#     numerator = sum((x_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
#     denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))

#     if denominator == 0:
#         return 0.0

#     return numerator / denominator


# def predict_performance_trend(records: List[Dict], threshold: float = 0.5) -> str:
#     """
#     records: list of {"performance_score": float, "activity_date": ...}
#         ordered chronologically (oldest first).
#     threshold: minimum slope magnitude (points per period) to call it a
#         real trend rather than "stable" noise. Tune this against real data.

#     Returns one of: "improving", "declining", "stable"
#     """
#     scores = [r.get("performance_score", 0) for r in records if r.get("performance_score") is not None]

#     if len(scores) < 2:
#         return "stable"

#     slope = _simple_slope(scores)

#     if slope > threshold:
#         return "improving"
#     elif slope < -threshold:
#         return "declining"
#     return "stable"


# def predict_exam_readiness(records: List[Dict], target_score: float = 85.0) -> float:
#     """
#     Optional helper: extrapolates the trend line forward to estimate a
#     'readiness' percentage against a target score. Used for dashboard
#     "Exam Readiness" style metrics.
#     Returns a value clamped between 0 and 100.
#     """
#     scores = [r.get("performance_score", 0) for r in records if r.get("performance_score") is not None]
#     if not scores:
#         return 0.0

#     latest = scores[-1]
#     readiness = (latest / target_score) * 100 if target_score else 0.0
#     return round(min(max(readiness, 0.0), 100.0), 2)


# def build_study_summary(records: List[Dict], weeks: int = 4) -> Dict:
#     """
#     Main entry point for this module. Takes raw study/activity records from
#     the database layer and returns the exact `study_summary` dict shape
#     required by DigitalTwinAdvisor.set_context().

#     records: list of dicts, each like:
#         {"study_hours": 2.5, "performance_score": 78, "subject": "DBMS",
#          "activity_date": "2026-07-20"}
#         ordered oldest -> newest.
#     """
#     return {
#         "avg_weekly_hours": average_weekly_hours(records, weeks=weeks),
#         "performance_trend": predict_performance_trend(records),
#     }


# if __name__ == "__main__":
#     # Quick manual sanity check
#     sample_records = [
#         {"study_hours": 1.5, "performance_score": 70, "activity_date": "2026-07-01"},
#         {"study_hours": 2.0, "performance_score": 74, "activity_date": "2026-07-05"},
#         {"study_hours": 2.0, "performance_score": 76, "activity_date": "2026-07-10"},
#         {"study_hours": 2.5, "performance_score": 78, "activity_date": "2026-07-15"},
#         {"study_hours": 3.0, "performance_score": 82, "activity_date": "2026-07-20"},
#     ]
#     print(build_study_summary(sample_records))
#     print("Exam readiness:", predict_exam_readiness(sample_records))
"""
Study performance trend prediction.
Used by ai_engine/simulation/simulator.py and llm_integration/advisor.py.
"""

from typing import List, Dict
from sqlalchemy.orm import Session
from database import models


def predict_performance_trend(records: List[Dict]) -> str:
    """
    records: list of dicts with 'performance_score' (chronological order assumed).
    Simple linear regression (slope sign) to classify trend direction.
    """
    if not records or len(records) < 2:
        return "insufficient data"

    scores = [r.get("performance_score", 0) for r in records]
    n = len(scores)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(scores) / n

    numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0

    if slope > 0.5:
        return "improving"
    elif slope < -0.5:
        return "declining"
    return "stable"


def get_study_summary(db: Session, user_id: int) -> dict:
    """
    Used by llm_integration/advisor.py's set_context() to ground the chatbot.
    Keys: avg_weekly_hours, performance_trend
    """
    records = db.query(models.StudyRecord).filter_by(user_id=user_id).all()

    if not records:
        return {"avg_weekly_hours": 0, "performance_trend": "insufficient data"}

    total_hours = sum(r.duration_minutes / 60.0 for r in records)
    avg_weekly_hours = round(total_hours / max(len(records) / 7, 1), 1)

    score_records = [{"performance_score": r.exam_score or r.focus_score * 10} for r in records]
    trend = predict_performance_trend(score_records)

    return {
        "avg_weekly_hours": avg_weekly_hours,
        "performance_trend": trend
    }