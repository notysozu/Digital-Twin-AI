# Digital Twin AI – Personal Life Simulation & Decision Assistant

## AI Assistant Context
**Project Goal:** Build an intelligent decision-support system that creates a "digital twin" of a user to forecast future life outcomes of their choices (finances, habits, studies) using predictive analytics, machine learning, and LLM advice.
**Architecture Style:** Decoupled frontend/backend monorepo.

## Tech Stack
* **Frontend Client:** React 19, TypeScript, Vite, TanStack Router & Start, Tailwind CSS, Radix UI, Recharts.
* **Backend API Server:** FastAPI (Python), Uvicorn.
* **Database:** PostgreSQL or SQLite (SQLAlchemy ORM).
* **AI & Predictive Engines:** Scikit-learn, Pandas, Gemini & Groq LLM Advisors.

---

## 🚀 Getting Started

### 1. Backend Environment Setup

Clone the repository and set up a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Environment Setup

Ensure you have Node.js installed, then install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

### 3. Environment Variables Configuration

Create a `.env` file in the root directory and set your configuration options:

```env
DATABASE_URL=sqlite:///./digital_twin.db
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🏃 Running the Application

The application consists of a **FastAPI backend API** and a **React Vite frontend**. You can run both concurrently in separate terminal sessions.

### Start Backend API (FastAPI)

```bash
# Activate virtual environment
source .venv/bin/activate

# Launch uvicorn server
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

- **Backend Base URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive OpenAPI Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Start Frontend Client (Vite React)

```bash
cd frontend
npm run dev
```

- **Frontend Client URL:** [http://localhost:8080](http://localhost:8080)

---

## 📂 Project Directory Structure

```text
digital-twin-ai/
│
├── frontend/                 # React, TypeScript and Vite client
│   ├── src/
│   │   ├── routes/           # Routing tree (Landing, Dashboard, Simulator, Setup, Tasks)
│   │   ├── components/       # App Shell, Settings Dialog, charts, and Radix widgets
│   │   └── lib/              # API Client (api.ts) & Central State Provider (twin-store.tsx)
│   ├── package.json          # Node dependencies and build scripts
│   └── vite.config.ts        # Vite environment configs
│
├── backend/                  # FastAPI server and route handlers
│   ├── main.py               # FastAPI application instance
│   ├── api/                  # API routers (users, records, simulations, finance, habits, study)
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
│   └── llm_integration/      # Conversational AI advisor prompt handling
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
| `/users/` | `POST` | Create a new user profile |
| `/users/{user_id}` | `PUT` | Update user settings/metrics |
| `/users/username/{username}` | `GET` | Retrieve user profile by username |
| `/users/email/{email}` | `GET` | Retrieve user profile by email |
| `/records/habit/{user_id}` | `GET / POST` | Log/get habit duration & wellness impact records |
| `/records/study/{user_id}` | `GET / POST` | Log/get study duration & focus performance records |
| `/records/financial/{user_id}` | `GET / POST` | Log/get financial transaction ledger records |
| `/simulations/baseline/{user_id}` | `GET` | Compute user's average baseline parameters |
| `/simulations/forecast/{user_id}` | `GET` | Generate deterministic net worth forecast |
| `/simulations/compare/{user_id}` | `POST` | Execute multi-scenario What-If simulations & AI recommendations |
