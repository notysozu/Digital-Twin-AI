from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine
from database.models import Base
from database.crud import seed_mock_data
from backend.api import users, records, simulations, finance, habits, study
from database.database import SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Twin AI Backend API",
    description="Backend services for Digital Twin AI simulation and prediction system.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        from backend.api.users import get_default_user
        get_default_user(db)
    finally:
        db.close()

app.include_router(users.router)
app.include_router(records.router)
app.include_router(simulations.router)
app.include_router(finance.router)
app.include_router(habits.router)
app.include_router(study.router)

@app.get("/")
def read_root():
    return {
        "message": "Digital Twin AI API is running",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }