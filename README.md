# Digital Twin AI – Personal Life Simulation & Decision Assistant

## AI Assistant Context
**Project Goal:** Build an intelligent decision-support system that creates a "digital twin" of a user to forecast future outcomes of their choices (finances, habits, studies) using predictive analytics, ML, and LLMs.
**Architecture Style:** Decoupled microservices/monorepo. 
**Primary Languages:** Python, SQL.

## Tech Stack
* **Frontend / Visualization:** Streamlit (Python), Plotly
* **Backend / API Routing:** FastAPI (Python), Uvicorn
* **Database:** SQLite (default / local fallback `digital_twin.db`) or PostgreSQL (SQLAlchemy ORM)
* **AI & Machine Learning:** Scikit-learn, Pandas, Large Language Models (Gemini / Groq API)

---

## 🚀 Getting Started

### 1. Environment Setup

Clone the repository and set up a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables Configuration

Copy `.env.example` to `.env` (or create a `.env` file in the root directory) and set your configuration options:

```env
DATABASE_URL=sqlite:///./digital_twin.db
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🏃 Running the Application

The application consists of a **FastAPI backend API** and a **Streamlit frontend dashboard**. You can run both concurrently in separate terminal sessions.

### Start Backend API (FastAPI)

```bash
# Activate virtual environment first
source .venv/bin/activate

# Launch uvicorn server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend Base URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive OpenAPI Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Start Frontend Dashboard (Streamlit)

```bash
# Activate virtual environment first
source .venv/bin/activate

# Launch Streamlit app
streamlit run frontend/app.py --server.port 8501
```

- **Frontend Dashboard URL:** [http://localhost:8501](http://localhost:8501)

---

## 📂 Project Directory Structure

```text
digital-twin-ai/
│
├── frontend/                 # Streamlit dashboard and UI components
│   ├── app.py                # Main Streamlit entry point
│   └── components/           # Reusable UI widgets and charts
│
├── backend/                  # FastAPI server and route handlers
│   ├── main.py               # FastAPI application instance
│   ├── api/                  # API endpoints (users, records, simulations, finance, habits, study)
│   ├── config/               # App configuration
│   └── services/             # Business logic and external API calls
│
├── database/                 # Database schemas, models, and CRUD operations
│   ├── database.py           # SQLAlchemy engine & session setup
│   ├── models.py             # SQLAlchemy ORM models (Users, Finances, Habits, Studies)
│   ├── schemas.py            # Pydantic models for data validation
│   └── crud.py               # Database transaction functions & seed data
│
├── ai_engine/                # Machine learning and simulation logic
│   ├── forecasting/          # Financial and study predictive models
│   ├── simulation/           # Multi-scenario "what-if" simulation logic
│   └── llm_integration/      # Conversational AI prompt handling
│
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variables template
```

---

## 📡 API Endpoints Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | API root status check |
| `/health` | `GET` | Health check endpoint |
| `/users/` | `GET / POST / PUT` | Manage user profiles and baseline metrics |
| `/records/` | `GET` | Retrieve combined user activity logs |
| `/simulations/` | `POST` | Execute multi-scenario digital twin simulations |
| `/finance/` | `GET / POST` | Financial record tracking & budget overview |
| `/habits/` | `GET / POST` | Daily habit tracking & wellness impact metrics |
| `/study/` | `GET / POST` | Study focus time tracking & performance correlation |
