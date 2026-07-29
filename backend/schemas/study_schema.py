from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StudyRecordCreate(BaseModel):
    subject: str
    duration_minutes: int
    focus_score: int
    exam_score: Optional[float] = None


class StudyRecordUpdate(BaseModel):
    subject: Optional[str] = None
    duration_minutes: Optional[int] = None
    focus_score: Optional[int] = None
    exam_score: Optional[float] = None


class StudyRecordResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    duration_minutes: int
    focus_score: int
    exam_score: Optional[float] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
    