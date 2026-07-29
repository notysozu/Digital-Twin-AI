from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import database, crud
from backend.schemas.study_schema import StudyRecordCreate, StudyRecordUpdate, StudyRecordResponse

router = APIRouter(
    prefix="/study",
    tags=["Study"]
)

@router.post(
    "/",
    summary="Create Study Record",
    status_code=status.HTTP_201_CREATED,
    response_model=StudyRecordResponse
)
def create_study_record(
    record: StudyRecordCreate,
    user_id: int = Query(1, description="Associated user ID"),
    db: Session = Depends(database.get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    from database.schemas import StudyRecordCreate as DbStudyRecordCreate
    db_record_input = DbStudyRecordCreate(
        subject=record.subject,
        duration_minutes=record.duration_minutes,
        focus_score=record.focus_score,
        exam_score=record.exam_score
    )
    db_record = crud.create_study_record(db, db_record_input, user_id)
    return db_record

@router.get(
    "/",
    summary="Get All Study Records",
    response_model=List[StudyRecordResponse]
)
def get_study_records(
    user_id: int = Query(1, description="Filter by user ID"),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(database.get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_study_records(db, user_id=user_id, limit=limit, offset=offset)

@router.get(
    "/{record_id}",
    summary="Get Study Record",
    response_model=StudyRecordResponse
)
def get_study_record(record_id: int, db: Session = Depends(database.get_db)):
    db_record = crud.get_study_record(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Study record not found")
    return db_record

@router.put(
    "/{record_id}",
    summary="Update Study Record",
    response_model=StudyRecordResponse
)
def update_study_record(
    record_id: int,
    record: StudyRecordUpdate,
    db: Session = Depends(database.get_db)
):
    db_record = crud.get_study_record(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Study record not found")
        
    if record.subject is not None:
        db_record.subject = record.subject
    if record.duration_minutes is not None:
        db_record.duration_minutes = record.duration_minutes
    if record.focus_score is not None:
        db_record.focus_score = record.focus_score
    if record.exam_score is not None:
        db_record.exam_score = record.exam_score
        
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete(
    "/{record_id}",
    summary="Delete Study Record",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_study_record(record_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_study_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Study record not found")
    return