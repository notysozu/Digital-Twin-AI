import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from database import models
from ai_engine.forecasting import financial, habits
from typing import Dict, Any

def get_user_baseline_metrics(db: Session, user_id: int) -> Dict[str, float]:
    """
    Compute average habits and financial baselines from the past 30 days of data.
    """
    # Fallback default values
    defaults = {
        "monthly_savings": 1000.0,
        "current_net_worth": 15000.0,
        "sleep_hours": 7.5,
        "exercise_hours": 0.5,
        "screen_hours": 4.0,
        "social_hours": 1.0,
        "study_hours_week": 8.0,
        "study_hours_daily": 8.0 / 7.0
    }
    
    # Check user existence
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        return defaults
        
    # Calculate current net worth (sum of investments - expenses + income in all records is complex,
    # let's calculate it by starting with a base net worth (e.g., $15000) and summing income - expenses)
    # Actually, a simple approach: net worth can be calculated by summing all "Income" and "Investment" records,
    # subtracting "Fixed Expense" and "Discretionary Expense" from a starting seed of $15000.
    start_net_worth = 15000.0
    financials = db.query(models.FinancialRecord).filter_by(user_id=user_id).all()
    
    net_worth = start_net_worth
    for f in financials:
        if f.category == "Income":
            # Net worth doesn't double just because you get salary, it depends on savings.
            # But let's compute net worth as: cumulative (Income + Investment - Fixed Expense - Discretionary Expense)
            # Actually, standard net worth is sum of assets (investments). Let's define:
            # Net Worth = Sum(Investment) + Cash (which is Salary - All Expenses).
            # Let's write a simple formula:
            pass
            
    # Let's count actual investment record totals
    total_investments = sum(f.amount for f in financials if f.category == "Investment")
    total_income = sum(f.amount for f in financials if f.category == "Income")
    total_expenses = sum(f.amount for f in financials if f.category in ["Fixed Expense", "Discretionary Expense"])
    
    current_net_worth = max(1000.0, start_net_worth + total_income - total_expenses)
    
    # Calculate monthly savings:
    # Look at last 30 days of income vs expenses
    # Or simplified: User.monthly_income - average monthly expenses, or just average monthly Investment records.
    # Let's use average monthly investments as the savings rate.
    # In seeded data, it is $1000/month.
    monthly_savings = 1000.0
    if financials:
        # Sum of investments in last 30 days
        now_naive = pd.Timestamp.utcnow().tz_localize(None)
        monthly_savings = sum(f.amount for f in financials if f.category == "Investment" and f.record_date >= now_naive - pd.Timedelta(days=30))
        if monthly_savings == 0:
            monthly_savings = 1000.0
            
    # Calculate habit averages in last 30 days
    thirty_days_ago = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=30)
    habit_logs = db.query(models.HabitRecord).filter(
        models.HabitRecord.user_id == user_id,
        models.HabitRecord.created_at >= thirty_days_ago
    ).all()
    
    sleep_hours = []
    exercise_hours = []
    screen_hours = []
    social_hours = []
    
    for h in habit_logs:
        dur_h = h.duration_minutes / 60.0
        if h.habit_name == "Sleep":
            sleep_hours.append(dur_h)
        elif h.habit_name == "Exercise":
            exercise_hours.append(dur_h)
        elif h.habit_name == "Screen Time":
            screen_hours.append(dur_h)
        elif h.habit_name == "Socializing":
            social_hours.append(dur_h)
            
    study_logs = db.query(models.StudyRecord).filter(
        models.StudyRecord.user_id == user_id,
        models.StudyRecord.created_at >= thirty_days_ago
    ).all()
    
    study_hours_daily = [s.duration_minutes / 60.0 for s in study_logs]
    
    # Average weekly study hours: total study duration in 30 days / (30/7)
    total_study_hours = sum(s.duration_minutes / 60.0 for s in study_logs)
    study_hours_week = total_study_hours / (30.0 / 7.0) if len(study_logs) > 0 else defaults["study_hours_week"]

    return {
        "monthly_savings": float(monthly_savings),
        "current_net_worth": float(current_net_worth),
        "sleep_hours": float(np.mean(sleep_hours)) if sleep_hours else defaults["sleep_hours"],
        "exercise_hours": float(np.sum(exercise_hours) / 30.0) if exercise_hours else defaults["exercise_hours"], # daily average
        "screen_hours": float(np.mean(screen_hours)) if screen_hours else defaults["screen_hours"],
        "social_hours": float(np.sum(social_hours) / 30.0) if social_hours else defaults["social_hours"], # daily average
        "study_hours_week": float(study_hours_week),
        "study_hours_daily": float(total_study_hours / 30.0)
    }

def run_what_if_comparison(
    db: Session,
    user_id: int,
    change_a: Dict[str, float],
    change_b: Dict[str, float],
    years: int = 5
) -> Dict[str, Any]:
    """
    Run two scenarios and return side-by-side comparison results.
    """
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("User not found")
        
    baseline = get_user_baseline_metrics(db, user_id)
    coefs, is_fallback = habits.fit_digital_twin_models(db, user_id)
    
    scenarios = {
        "scenario_a": change_a,
        "scenario_b": change_b
    }
    
    results = {}
    
    for name, change in scenarios.items():
        # Calculate new lifestyle parameters
        # Tweak baseline values by the changes
        mod_savings = max(0.0, baseline["monthly_savings"] + change.get("monthly_investment_change", 0.0))
        mod_sleep = max(4.0, min(12.0, baseline["sleep_hours"] + change.get("sleep_hours_change", 0.0)))
        mod_study_week = max(0.0, baseline["study_hours_week"] + change.get("weekly_study_change", 0.0))
        mod_study_daily = mod_study_week / 7.0
        
        # Keep screen, exercise, social at baseline
        # (Though we could let users configure them, keep it simple for now)
        mod_exercise = baseline["exercise_hours"]
        mod_screen = baseline["screen_hours"]
        mod_social = baseline["social_hours"]
        
        # Predict sustained indices
        preds = habits.predict_scenario_scores(
            coefs=coefs,
            sleep_hours=mod_sleep,
            exercise_hours=mod_exercise,
            screen_hours=mod_screen,
            social_hours=mod_social,
            study_hours=mod_study_daily
        )
        
        # Project financials deterministically for 'years'
        # Return rate 7% nominal, 2.5% inflation
        fin_proj = financial.run_deterministic_projection(
            current_age=user.age,
            retirement_age=user.age + years,
            current_net_worth=baseline["current_net_worth"],
            monthly_savings=mod_savings,
            annual_return_rate=0.08,
            annual_inflation_rate=0.025
        )
        
        # Check if they would hit retirement goals under this scenario
        # We run standard retirement projection up to User.retirement_goal_age
        retirement_proj = financial.run_deterministic_projection(
            current_age=user.age,
            retirement_age=user.retirement_goal_age,
            current_net_worth=baseline["current_net_worth"],
            monthly_savings=mod_savings,
            annual_return_rate=0.08,
            annual_inflation_rate=0.025
        )
        final_retirement_wealth = retirement_proj[-1]["net_worth"]
        attained_retirement = final_retirement_wealth >= user.target_net_worth
        
        # Build datapoints list
        datapoints = []
        for p in fin_proj:
            datapoints.append({
                "year": p["year"],
                "net_worth": p["net_worth"],
                # We assume steady state lifestyle indices for simplicity over projection
                "health_index": round(preds["health_index"], 2),
                "focus_index": round(preds["focus_index"], 2)
            })
            
        results[name] = {
            "scenario_name": "Scenario A" if name == "scenario_a" else "Scenario B",
            "datapoints": datapoints,
            "attained_retirement": attained_retirement,
            "wealth_at_end": fin_proj[-1]["net_worth"],
            "retirement_wealth": final_retirement_wealth,
            "health_index": preds["health_index"],
            "focus_index": preds["focus_index"],
            "details": {
                "sleep": mod_sleep,
                "study_week": mod_study_week,
                "monthly_savings": mod_savings
            }
        }
        
    return results
"""
ai_engine/simulation/simulator.py

Future Outcome Simulation Engine
-----------------------------------
Runs "what-if" decision scenarios by re-invoking the forecasting functions
from financial.py / study.py with modified assumptions, then packages the
result in the exact `scenario_result` shape expected by
ai_engine/llm_integration/advisor.py's ask_with_simulation():

    {
        "scenario_name": str,
        "predicted_outcome": str
    }

This module depends on:
    ai_engine/forecasting/financial.py  (project_savings, project_toward_goal)
    ai_engine/forecasting/study.py      (predict_performance_trend)
"""

from typing import Dict, List, Optional

# from financial import project_savings, project_toward_goal
# from study import predict_performance_trend
from ai_engine.forecasting.financial import project_savings, project_toward_goal
from ai_engine.forecasting.study import predict_performance_trend


def simulate_savings_rate_change(current_savings: float, monthly_income: float,
                                  new_savings_percent: float, months: int = 60,
                                  annual_growth_rate: float = 0.0) -> Dict:
    """
    Scenario: "What if I saved X% of my income instead of my current rate?"

    monthly_income: average monthly income
    new_savings_percent: e.g. 30 for "save 30% of income"
    months: horizon to simulate over (default 5 years)
    """
    monthly_savings = monthly_income * (new_savings_percent / 100)
    projected = project_savings(
        current_savings=current_savings,
        monthly_savings=monthly_savings,
        months=months,
        annual_growth_rate=annual_growth_rate,
    )

    years = round(months / 12, 1)
    outcome = (
        f"Saving {new_savings_percent}% of income would grow savings to "
        f"${projected:,.0f} in {years} years (vs current trajectory)."
    )

    return {
        "scenario_name": f"Increase Savings Rate to {new_savings_percent}%",
        "predicted_outcome": outcome,
    }


def simulate_goal_timeline(current_savings: float, monthly_savings: float,
                            target_value: float, goal_name: str,
                            annual_growth_rate: float = 0.0) -> Dict:
    """
    Scenario: "Will I achieve [goal] and when?"
    """
    months_needed = project_toward_goal(
        current_savings=current_savings,
        monthly_savings=monthly_savings,
        target_value=target_value,
        annual_growth_rate=annual_growth_rate,
    )

    if months_needed is None:
        outcome = f"At the current rate, '{goal_name}' (${target_value:,.0f}) isn't reachable within 20 years."
    elif months_needed == 0:
        outcome = f"'{goal_name}' is already achieved."
    else:
        years = round(months_needed / 12, 1)
        outcome = f"'{goal_name}' (${target_value:,.0f}) is achievable in approximately {months_needed} months (~{years} years)."

    return {
        "scenario_name": f"Goal Timeline: {goal_name}",
        "predicted_outcome": outcome,
    }


def simulate_study_hours_change(current_records: List[Dict], additional_weekly_hours: float) -> Dict:
    """
    Scenario: "What if I studied X more hours per week?"

    Approximates the effect by nudging each record's performance_score
    upward proportionally to the added study time, then re-running the
    trend predictor. This is a simple heuristic, not a trained model -
    replace with a regression model against real historical data if you
    want more rigor.
    """
    if not current_records:
        return {
            "scenario_name": "Increase Weekly Study Hours",
            "predicted_outcome": "Not enough study history to simulate this scenario.",
        }

    # Heuristic: assume every additional hour/week nudges score by ~1.5 points,
    # capped at 100. Tune this multiplier against real data if available.
    boost_per_hour = 1.5
    adjusted_records = []
    for r in current_records:
        adjusted_score = min(r.get("performance_score", 0) + additional_weekly_hours * boost_per_hour, 100)
        adjusted_records.append({**r, "performance_score": adjusted_score})

    new_trend = predict_performance_trend(adjusted_records)

    outcome = (
        f"Adding {additional_weekly_hours} study hours/week would likely shift the "
        f"performance trend to '{new_trend}'."
    )

    return {
        "scenario_name": f"Increase Study Hours by {additional_weekly_hours}/week",
        "predicted_outcome": outcome,
    }


def compare_scenarios(scenarios: List[Dict]) -> Dict:
    """
    Optional helper for the "Scenario Comparison" dashboard panel.
    Takes a list of already-computed scenario_result dicts and returns
    them bundled together, e.g. for side-by-side chart rendering.

    scenarios: list of dicts, each from one of the simulate_* functions above.
    """
    return {
        "comparison_count": len(scenarios),
        "scenarios": scenarios,
    }


if __name__ == "__main__":
    # Quick manual sanity check
    savings_scenario = simulate_savings_rate_change(
        current_savings=15420,
        monthly_income=3800,
        new_savings_percent=30,
        annual_growth_rate=0.03,
    )
    print(savings_scenario)

    goal_scenario = simulate_goal_timeline(
        current_savings=15420,
        monthly_savings=820,
        target_value=20000,
        goal_name="Emergency Fund",
        annual_growth_rate=0.03,
    )
    print(goal_scenario)

    sample_study_records = [
        {"study_hours": 2.0, "performance_score": 74},
        {"study_hours": 2.5, "performance_score": 78},
        {"study_hours": 3.0, "performance_score": 82},
    ]
    study_scenario = simulate_study_hours_change(sample_study_records, additional_weekly_hours=3)
    print(study_scenario)

    print(compare_scenarios([savings_scenario, goal_scenario, study_scenario]))