from fastapi import FastAPI
from routers import jobs, analysis
from routers.tts import router as tts_router

# FastAPI app
app = FastAPI(
    title="Job Search API",
    description="API for job search and AI-powered job analysis",
    version="1.0.0"
)

# Include routers
app.include_router(jobs.router)
app.include_router(analysis.router)
app.include_router(tts_router)

@app.get("/")
def root():
    return {"message": "Job Search API", "version": "1.0.0"}

# --- Important Notes for Setup and Execution ---

## Prerequisites:
# 1. **Install required libraries:** `pip install fastapi uvicorn requests pydantic google-genai`
# 2. **Set environment variables:**
#    - **`GEMINI_API_KEY`**: Get your key from Google AI Studio.
#    - **`RAPIDAPI_KEY`**: Get your JSearch key from RapidAPI.

## How to Run:
# 1. Run the server: `uvicorn main:app --reload`
# 2. Access the API docs at: `http://127.0.0.1:8000/docs`
# 3. Available endpoints:
#    - GET /jobs - Get raw job data
#    - POST /analysis/job - Analyze job description with AI