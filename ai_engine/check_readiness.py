"""check_readiness.py — run before anything else"""
from database import SessionLocal, models

def check_readiness(user_id: int):
    db = SessionLocal()
    user = db.query(models.User).filter_by(id=user_id).first()
    fin = db.query(models.FinancialRecord).filter_by(user_id=user_id).all()
    hab = db.query(models.HabitRecord).filter_by(user_id=user_id).all()
    stu = db.query(models.StudyRecord).filter_by(user_id=user_id).all()

    print(f"User {user_id}: {'FOUND' if user else 'MISSING'}")
    print(f"FinancialRecords: {len(fin)}  (need >0 for real path)")
    print(f"HabitRecords:     {len(hab)}  (need >=5 for real regression)")
    print(f"StudyRecords:     {len(stu)}  (need >=5 for regression, >=2 for trend)")

    if fin:
        cats = set(r.category for r in fin)
        print(f"  categories present: {cats}")
        print(f"  date range: {min(r.transaction_date for r in fin)} to {max(r.transaction_date for r in fin)}")

    db.close()

if __name__ == "__main__":
    check_readiness(user_id=1)  # change to your real test user's id