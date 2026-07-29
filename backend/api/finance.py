from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database import database, crud
from backend.schemas.financial_schema import FinancialRecordCreate, FinancialRecordUpdate, FinancialRecordResponse

router = APIRouter(
    prefix="/finance",
    tags=["Finance"]
)

@router.post(
    "/",
    summary="Create Financial Record",
    status_code=status.HTTP_201_CREATED,
    response_model=FinancialRecordResponse
)
def create_financial_record(
    record: FinancialRecordCreate,
    user_id: int = Query(1, description="Associated user ID"),
    db: Session = Depends(database.get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Map backend/schemas model to database/schemas model
    from database.schemas import FinancialRecordCreate as DbFinancialRecordCreate
    db_record_input = DbFinancialRecordCreate(
        category=record.category,
        description=record.description,
        amount=record.amount
    )
    db_record = crud.create_financial_record(db, db_record_input, user_id)
    return db_record

@router.get(
    "/",
    summary="Get All Financial Records",
    response_model=List[FinancialRecordResponse]
)
def get_financial_records(
    user_id: int = Query(1, description="Filter by user ID"),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(database.get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_financial_records(db, user_id=user_id, limit=limit, offset=offset)

@router.get(
    "/{record_id}",
    summary="Get Financial Record",
    response_model=FinancialRecordResponse
)
def get_financial_record(record_id: int, db: Session = Depends(database.get_db)):
    db_record = crud.get_financial_record(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Financial record not found")
    return db_record

@router.put(
    "/{record_id}",
    summary="Update Financial Record",
    response_model=FinancialRecordResponse
)
def update_financial_record(
    record_id: int,
    record: FinancialRecordUpdate,
    db: Session = Depends(database.get_db)
):
    db_record = crud.get_financial_record(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Financial record not found")
    
    # Merge updates
    if record.category is not None:
        db_record.category = record.category
    if record.description is not None:
        db_record.description = record.description
    if record.amount is not None:
        db_record.amount = record.amount
        
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete(
    "/{record_id}",
    summary="Delete Financial Record",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_financial_record(record_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_financial_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Financial record not found")
    return