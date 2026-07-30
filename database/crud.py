import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Any
from . import models, schemas

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        age=user.age,
        retirement_goal_age=user.retirement_goal_age,
        target_net_worth=user.target_net_worth,
        monthly_income=user.monthly_income,
        sleep_target_hours=user.sleep_target_hours,
        study_target_hours_week=user.study_target_hours_week
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_db_user_or_raise(db, user_id)
    if not db_user:
        return None
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_db_user_or_raise(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Financial operations
def get_financial_records(db: Session, user_id: int, limit: int = 100, offset: int = 0):
    return db.query(models.FinancialRecord)\
        .filter(models.FinancialRecord.user_id == user_id)\
        .order_by(models.FinancialRecord.record_date.desc())\
        .offset(offset).limit(limit).all()

def create_financial_record(db: Session, record: schemas.FinancialRecordCreate, user_id: int):
    db_record = models.FinancialRecord(
        user_id=user_id,
        category=record.category,
        description=record.description,
        amount=record.amount,
        record_date=record.record_date or datetime.utcnow()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# Habit operations
def get_habit_records(db: Session, user_id: int, limit: int = 100, offset: int = 0):
    return db.query(models.HabitRecord)\
        .filter(models.HabitRecord.user_id == user_id)\
        .order_by(models.HabitRecord.created_at.desc())\
        .offset(offset).limit(limit).all()

def create_habit_record(db: Session, record: schemas.HabitRecordCreate, user_id: int):
    db_record = models.HabitRecord(
        user_id=user_id,
        habit_name=record.habit_name,
        duration_minutes=record.duration_minutes,
        impact_score=record.impact_score,
        created_at=record.created_at or datetime.utcnow()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# Study operations
def get_study_records(db: Session, user_id: int, limit: int = 100, offset: int = 0):
    return db.query(models.StudyRecord)\
        .filter(models.StudyRecord.user_id == user_id)\
        .order_by(models.StudyRecord.created_at.desc())\
        .offset(offset).limit(limit).all()

def create_study_record(db: Session, record: schemas.StudyRecordCreate, user_id: int):
    db_record = models.StudyRecord(
        user_id=user_id,
        subject=record.subject,
        duration_minutes=record.duration_minutes,
        focus_score=record.focus_score,
        exam_score=record.exam_score,
        created_at=record.created_at or datetime.utcnow()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# Seed Data helper
def seed_mock_data(db: Session, user_id: int):
    # Check if records exist already
    financials_count = db.query(models.FinancialRecord).filter_by(user_id=user_id).count()
    if financials_count > 0:
        return  # Already seeded
    
    print(f"Seeding mock data for user {user_id}...")
    start_date = datetime.utcnow() - timedelta(days=90)
    
    # 1. Seed Financial Records
    # Monthly Income and Fixed Expenses (logged monthly)
    for m in range(4):
        log_date = start_date + timedelta(days=m * 30)
        # Salary
        db.add(models.FinancialRecord(
            user_id=user_id,
            category="Income",
            description="Monthly Paycheck",
            amount=5000.0,
            record_date=log_date
        ))
        # Fixed Rent/Bill
        db.add(models.FinancialRecord(
            user_id=user_id,
            category="Fixed Expense",
            description="Rent and Utilities",
            amount=1800.0,
            record_date=log_date + timedelta(days=1)
        ))
        # Automatic Investment
        db.add(models.FinancialRecord(
            user_id=user_id,
            category="Investment",
            description="Index Funds Portfolio",
            amount=1000.0,
            record_date=log_date + timedelta(days=5)
        ))
        
    # Weekly Discretionary Expenses and Subscriptions
    for d in range(90):
        log_date = start_date + timedelta(days=d)
        
        # Daily food & fun expenses (occasional)
        if random.random() < 0.7:
            category = "Discretionary Expense"
            desc = random.choice(["Groceries", "Coffee & Diner", "Uber ride", "Amazon order", "Weekend Movie"])
            amount = round(random.uniform(10.0, 75.0), 2)
            db.add(models.FinancialRecord(
                user_id=user_id,
                category=category,
                description=desc,
                amount=amount,
                record_date=log_date
            ))
            
    # 2. Seed Habit Records
    # We log sleep daily, exercise 3x/week, social 2x/week
    for d in range(90):
        log_date = start_date + timedelta(days=d)
        
        # Sleep (Daily)
        # General distribution: mostly 7-8 hours, but sometimes less/more
        sleep_hours = random.choice([6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0])
        # Add correlation: if they sleep more, their impact score is higher
        impact = int(min(10, max(1, sleep_hours + random.uniform(-1, 1))))
        db.add(models.HabitRecord(
            user_id=user_id,
            habit_name="Sleep",
            duration_minutes=int(sleep_hours * 60),
            impact_score=impact,
            created_at=log_date
        ))
        
        # Exercise (3x a week)
        if d % 7 in [1, 3, 5]:
            exercise_duration = random.choice([30, 45, 60, 90])
            # positive impact on wellbeing
            impact = random.choice([7, 8, 9, 10])
            db.add(models.HabitRecord(
                user_id=user_id,
                habit_name="Exercise",
                duration_minutes=exercise_duration,
                impact_score=impact,
                created_at=log_date + timedelta(hours=8)
            ))
            
        # Socializing (2x a week)
        if d % 7 in [5, 6]:
            social_duration = random.choice([120, 180, 240])
            impact = random.choice([6, 7, 8, 9])
            db.add(models.HabitRecord(
                user_id=user_id,
                habit_name="Socializing",
                duration_minutes=social_duration,
                impact_score=impact,
                created_at=log_date + timedelta(hours=18)
            ))

        # Screen Time (Daily)
        screen_minutes = random.choice([120, 180, 240, 300, 360, 420])
        # Higher screen time usually means lower productivity/feeling worse
        impact = int(min(10, max(1, 10 - (screen_minutes // 60) + random.randint(-1, 1))))
        db.add(models.HabitRecord(
            user_id=user_id,
            habit_name="Screen Time",
            duration_minutes=screen_minutes,
            impact_score=impact,
            created_at=log_date + timedelta(hours=12)
        ))

    # 3. Seed Study Records (Logged 4 times a week)
    subjects = ["Data Science", "Economics", "Machine Learning", "System Design"]
    for d in range(90):
        log_date = start_date + timedelta(days=d)
        
        if d % 7 in [0, 2, 4, 6]:
            subject = random.choice(subjects)
            # Study duration
            duration = random.choice([60, 90, 120, 180])
            
            # Focus score correlates with sleep: look up sleep hours for the day
            # (We will simulate correlation: better sleep = higher focus score)
            # For seeding, we just compute it with random noise correlated to sleep
            focus = random.choice([6, 7, 8, 9, 10]) if d % 7 != 0 else random.choice([4, 5, 6, 7])
            
            # Occasional exam score (every 3 weeks)
            exam = None
            if d % 21 == 0:
                exam = float(random.choice([78.0, 84.5, 90.0, 95.0, 98.0]))
                
            db.add(models.StudyRecord(
                user_id=user_id,
                subject=subject,
                duration_minutes=duration,
                focus_score=focus,
                exam_score=exam,
                created_at=log_date + timedelta(hours=14)
            ))

    db.commit()
    print("Seed complete.")


# Single-item CRUD helpers for finance, habit, and study records
def get_financial_record(db: Session, record_id: int):
    return db.query(models.FinancialRecord).filter(models.FinancialRecord.id == record_id).first()

def update_financial_record(db: Session, record_id: int, record_update: Any):
    db_record = get_financial_record(db, record_id)
    if not db_record:
        return None
    db_record.category = record_update.category
    db_record.description = record_update.description
    db_record.amount = record_update.amount
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_financial_record(db: Session, record_id: int):
    db_record = get_financial_record(db, record_id)
    if not db_record:
        return False
    db.delete(db_record)
    db.commit()
    return True

def get_habit_record(db: Session, habit_id: int):
    return db.query(models.HabitRecord).filter(models.HabitRecord.id == habit_id).first()

def update_habit_record(db: Session, habit_id: int, habit_update: Any):
    db_record = get_habit_record(db, habit_id)
    if not db_record:
        return None
    db_record.habit_name = habit_update.habit_name
    db_record.duration_minutes = habit_update.duration_minutes
    db_record.impact_score = habit_update.impact_score
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_habit_record(db: Session, habit_id: int):
    db_record = get_habit_record(db, habit_id)
    if not db_record:
        return False
    db.delete(db_record)
    db.commit()
    return True

def get_study_record(db: Session, record_id: int):
    return db.query(models.StudyRecord).filter(models.StudyRecord.id == record_id).first()

def update_study_record(db: Session, record_id: int, study_update: Any):
    db_record = get_study_record(db, record_id)
    if not db_record:
        return None
    db_record.subject = study_update.subject
    db_record.duration_minutes = study_update.duration_minutes
    db_record.focus_score = study_update.focus_score
    db_record.exam_score = study_update.exam_score
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_study_record(db: Session, record_id: int):
    db_record = get_study_record(db, record_id)
    if not db_record:
        return False
    db.delete(db_record)
    db.commit()
    return True

