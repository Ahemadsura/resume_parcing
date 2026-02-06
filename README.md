# Resume Parser Application

A full-stack resume parsing application built with:
- **Frontend**: Next.js (React)
- **Backend**: FastAPI (Python)
- **Database**: Supabase
- **Deployment**: Vercel (Frontend) & Render (Backend)

## Project Structure
- `/backend`: Python FastAPI application
- `/frontend`: Next.js application

## Setup & Run

### Backend (Python/FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend will be available at imports `http://localhost:8000`.

### Frontend (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
    The frontend will be available at `http://localhost:3000`.
