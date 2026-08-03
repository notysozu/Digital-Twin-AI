"""verify_forecasting.py — run from project root"""
from database.database import SessionLocal
from ai_engine.forecasting import financial, habits, study

def check_user(user_id: int):
    db = SessionLocal()
    print(f"\n{'='*50}\nCHECKING USER {user_id}\n{'='*50}")

    fin = financial.get_financial_summary(db, user_id)
    print("\n[financial.py] get_financial_summary:")
    print(fin)
    if fin.get("current_savings") == 0 and "note" in fin:
        print("  ⚠️  FALLBACK PATH")
    else:
        print("  ✅ real path")
        if fin["savings_rate"] > 100 or fin["savings_rate"] < 0:
            print(f"  ⚠️  savings_rate={fin['savings_rate']}% looks off")

    coefs, is_fallback = habits.fit_digital_twin_models(db, user_id)
    print("\n[habits.py] fit_digital_twin_models:")
    print("  is_fallback:", is_fallback, "| coefs:", coefs)

    scores_good = habits.predict_scenario_scores(coefs, sleep_hours=8, exercise_hours=1, screen_hours=2, social_hours=1, study_hours=2)
    scores_bad = habits.predict_scenario_scores(coefs, sleep_hours=4, exercise_hours=0, screen_hours=10, social_hours=0, study_hours=0)
    print("  Healthy scenario:", scores_good)
    print("  Unhealthy scenario:", scores_bad)
    if scores_good["health_index"] <= scores_bad["health_index"]:
        print("  ⚠️  Direction looks inverted — check impact_score coding")
    else:
        print("  ✅ direction makes sense")

    study_summary = study.get_study_summary(db, user_id)
    print("\n[study.py] get_study_summary:")
    print(study_summary)

    db.close()

if __name__ == "__main__":
    check_user(user_id=1)