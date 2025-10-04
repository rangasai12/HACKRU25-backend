import requests
import os
from typing import List
from google import genai
from google.genai import types
from models import RawJob, JobAnalysis

# Environment variables
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "your-rapidapi-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup AI client
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found. Using dummy key, AI calls will fail.")
    ai_client = genai.Client(api_key="DUMMY_KEY_IF_MISSING")
else:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)

def get_raw_jobs(query: str, page: int, num_pages: int, country: str, 
                date_posted: str, job_requirements: str) -> List[RawJob]:
    """Fetch raw job data from JSearch API."""
    url = f"https://{RAPIDAPI_HOST}/search"
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }
    params = {
        "query": query,
        "page": page,
        "num_pages": num_pages,
        "country": country,
        "date_posted": date_posted,
        "job_requirements": job_requirements,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        raw_data = response.json()
    except Exception as e:
        raise Exception(f"JSearch API error: {str(e)}")

    jobs: List[RawJob] = []
    for i, job in enumerate(raw_data.get("data", [])):
        job_id = f"job_{i}_{hash(job.get('job_title', ''))}"
        
        jobs.append(RawJob(
            job_id=job_id,
            job_title=job.get('job_title'),
            employer_name=job.get('employer_name'),
            job_description=job.get('job_description'),
            job_city=job.get('job_city'),
            job_state=job.get('job_state'),
            job_apply_link=job.get('job_apply_link'),
            job_employment_type=job.get('job_employment_type'),
            job_salary_min=job.get('job_salary_min'),
            job_salary_max=job.get('job_salary_max'),
            job_salary_currency=job.get('job_salary_currency'),
            job_salary_period=job.get('job_salary_period')
        ))

    return jobs

def analyze_job_description(job_description: str) -> JobAnalysis:
    """Analyze job description using AI and return structured data."""
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=JobAnalysis,
    )

    try:
        gemini_response = ai_client.models.generate_content(
            model='models/gemini-flash-lite-latest',
            contents=[
                {"role": "user", "parts": [{"text": f"Analyze the following job description and extract:\n1. A concise summary of what the job involves (4-5 lines)\n2. Key requirements and qualifications needed (return as a list of individual requirements (upto 5)\n3. Required technical and soft skills (return as a list of individual skills (upto 5) )\n\nJob Description:\n{job_description}"}]}
            ],
            config=config,
        )

        job_analysis = JobAnalysis.model_validate_json(gemini_response.text)
        return job_analysis
        
    except Exception as e:
        raise Exception(f"AI processing failed: {str(e)}")
