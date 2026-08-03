"""list_users.py — find real user_ids to test against"""
# from database import SessionLocal, models
from database.database import SessionLocal
from database import models

def list_users():
    db = SessionLocal()
    users = db.query(models.User).all()

    if not users:
        print("⚠️  No users found in the database at all.")
        print("You'll need to create one first (via your signup/onboarding flow,")
        print("or by inserting a row directly through models.User).")
        db.close()
        return

    print(f"Found {len(users)} user(s):\n")
    for u in users:
        fin_count = db.query(models.FinancialRecord).filter_by(user_id=u.id).count()
        hab_count = db.query(models.HabitRecord).filter_by(user_id=u.id).count()
        stu_count = db.query(models.StudyRecord).filter_by(user_id=u.id).count()
        print(f"id={u.id}  name={getattr(u, 'name', '?')}  "
              f"financial={fin_count}  habits={hab_count}  study={stu_count}")

    db.close()

if __name__ == "__main__":
    list_users()