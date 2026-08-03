"""inspect_habits.py — see what's actually being fed to the regression"""
from database.database import SessionLocal
from database import models

db = SessionLocal()
records = db.query(models.HabitRecord).filter_by(user_id=1).limit(20).all()

for r in records:
    print(vars(r))

db.close()