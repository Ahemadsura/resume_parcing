from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
from nlp_processor import extract_keywords, match_resume
import os
from typing import Optional, List, Dict

app = FastAPI(
    title="Resume Parser API",
    description="NLP-powered resume parsing and job matching",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobDescription(BaseModel):
    text: str
    keywords: list[str] = []


class ResumeData(BaseModel):
    skills: List[str]
    skills_by_category: Dict[str, List[str]]
    experience_years: str
    keywords: List[str]
    contact: Dict[str, str]
    education: Dict
    quality_analysis: Dict
    resume_score: int
    suggestions: List[Dict]
    word_count: int


class ResumeResponse(BaseModel):
    resume_data: ResumeData
    match_score: Optional[float] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Resume Parser API is running"}


@app.get("/health")
async def health_check():
    """Health check for deployment monitoring"""
    return {"status": "ok"}


@app.post("/parse-resume", response_model=ResumeResponse)
async def parse_resume(
    file: UploadFile,
    job_desc: str = Form(default="")
):
    """
    Parse a PDF resume and optionally match against a job description.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Extract text from PDF
        pdf_text = await extract_pdf_text(file)
        
        if not pdf_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. The file may be image-based or corrupted."
            )
        
        # Extract keywords and skills using NLP
        resume_data_dict = extract_keywords(pdf_text)
        
        # Calculate match score if job description provided
        match_score = None
        if job_desc.strip():
            match_score = match_resume(resume_data_dict, job_desc)
        
        return ResumeResponse(
            resume_data=resume_data_dict,
            match_score=match_score
        )
        
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


async def extract_pdf_text(file: UploadFile) -> str:
    """
    Extract text content from a PDF file.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file.file)
        text_content = []
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        
        return " ".join(text_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading PDF: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
