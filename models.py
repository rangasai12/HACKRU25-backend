from pydantic import BaseModel, Field
from typing import Optional, List

class RawJob(BaseModel):
    """Raw job data from JSearch API."""
    job_id: str = Field(description="Unique identifier for the job.")
    job_title: Optional[str] = Field(description="The job title.")
    employer_name: Optional[str] = Field(description="The company name.")
    job_description: Optional[str] = Field(description="Full job description.")
    job_city: Optional[str] = Field(description="Job city.")
    job_state: Optional[str] = Field(description="Job state.")
    job_apply_link: Optional[str] = Field(description="Direct application link.")
    job_employment_type: Optional[str] = Field(description="Employment type (full-time, part-time, etc.).")
    job_salary_min: Optional[float] = Field(description="Minimum salary if available.")
    job_salary_max: Optional[float] = Field(description="Maximum salary if available.")
    job_salary_currency: Optional[str] = Field(description="Salary currency.")
    job_salary_period: Optional[str] = Field(description="Salary period (hourly, yearly, etc.).")

class JobAnalysis(BaseModel):
    """AI-generated analysis of a job description."""
    description_summary: str = Field(description="A concise summary of the job description.")
    requirements: List[str] = Field(description="A list of core job requirements and qualifications.")
    required_skills: List[str] = Field(description="A list of technical or soft skills mentioned.")

class JobDescriptionRequest(BaseModel):
    job_description: str

class JobSearchRequest(BaseModel):
    query: str = "Software Developer Jobs in USA"
    page: int = 1
    num_pages: int = 1
    country: str = "us"
    date_posted: str = "today"
    job_requirements: str = "under_3_years_experience"
