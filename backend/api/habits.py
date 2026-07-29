from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import database, crud
from backend.schemas.habit_schema import HabitRecordCreate, HabitRecordUpdate, HabitRecordResponse

router = APIRouter(
    prefix="/habits",
    tags=["Habits"]
)

@router.post(
    "/",
    summary="Create Habit Record",
    status_code=status.HTTP_201_CREATED,
    response_model=HabitRecordResponse
)
def create_habit_record(
    record: HabitRecordCreate,
    user_id: int = Query(1, description="Associated user ID"),
    db: Session = Depends(database.get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    from database.schemas import HabitRecordCreate as DbHabitRecordCreate
    db_record_input = DbHabitRecordCreate(
        habit_name=record.habit_name,
        duration_minutes=record.duration_minutes,
        impact_score=record.impact_score
    )
    db_record = crud.create_habit_record(db, db_record_input, user_id)
    return db_record

@router.get(
    "/",
    summary="Get All Habit Records",
    response_model=List[HabitRecordResponse]
)
def get_habit_records(
    user_id: int = Query(1, description="Filter by user ID"),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(database.get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_habit_records(db, user_id=user_id, limit=limit, offset=offset)

@router.get(
    "/{habit_id}",
    summary="Get Habit Record",
    response_model=HabitRecordResponse
)
def get_habit_record(habit_id: int, db: Session = Depends(database.get_db)):
    db_record = crud.get_habit_record(db, habit_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Habit record not found")
    return db_record

@router.put(
    "/{habit_id}",
    summary="Update Habit Record",
    response_model=HabitRecordResponse
)
def update_habit_record(
    habit_id: int,
    record: HabitRecordUpdate,
    db: Session = Depends(database.get_db)
):
    db_record = crud.get_habit_record(db, habit_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Habit record not found")
        
    if record.habit_name is not None:
        db_record.habit_name = record.habit_name
    if record.duration_minutes is not None:
        db_record.duration_minutes = record.duration_minutes
    if record.impact_score is not None:
        db_record.impact_score = record.impact_score
        
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete(
    "/{habit_id}",
    summary="Delete Habit Record",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_habit_record(habit_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_habit_record(db, habit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Habit record not found")
    return