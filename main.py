from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from routers import jobs, analysis, questions, learning, scores, tts
from routers import guidance
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI(
    title="Job Search API",
    description="API for job search and AI-powered job analysis",
    version="1.0.0"
)

# Include routers

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins (use specific origins in production!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(analysis.router)
app.include_router(questions.router)
app.include_router(learning.router)
app.include_router(scores.router)
app.include_router(tts.router)
app.include_router(guidance.router)

# Custom exception handler for UnicodeDecodeError
@app.exception_handler(UnicodeDecodeError)
async def unicode_decode_exception_handler(request: Request, exc: UnicodeDecodeError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Audio processing error. The audio data contains invalid characters that cannot be decoded. Please try with a different audio file or format."
        }
    )

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
#    - POST /questions - Generate interview questions
#    - POST /learning - Generate learning recommendations
#    - POST /scores - Score interview questions