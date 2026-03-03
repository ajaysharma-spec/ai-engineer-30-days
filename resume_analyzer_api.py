from fastapi import FastAPI, UploadFile,File,Form
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import numpy as np

COMMON_SKILLS = [
    "python", "java", "sql", "machine learning",
    "deep learning", "fastapi", "django",
    "docker", "aws", "react", "git"
]

app=FastAPI()

model=SentenceTransformer("all-miniLM-L6-v2")

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile=File(...),
    job_description: str=Form(...)
):

    reader =PdfReader(resume.file)
    resume_text=""


    for page in reader.pages:
        if page.extract_text():
            resume_text += page.extract_text()
        
    resume_embedding = model.encode([resume_text])[0]
    jd_embedding = model.encode([job_description])[0]

    resume_vec = np.array(resume_embedding)
    jd_vec = np.array(jd_embedding)

    similarity = np.dot(resume_vec, jd_vec) / (
        np.linalg.norm(resume_vec) * np.linalg.norm(jd_vec)
)

    match_percentage = max(0, similarity) * 100

    if match_percentage < 30:
        level = "Low Match"
    elif match_percentage < 60:
        level = "Moderate Match"
    else:
        level = "Strong Match"

    resume_text_lower = resume_text.lower()
    jd_text_lower = job_description.lower()

    resume_skills = [skill for skill in COMMON_SKILLS if skill in resume_text_lower]
    jd_skills = [skill for skill in COMMON_SKILLS if skill in jd_text_lower]

    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

    return {
    "match_percentage": round(match_percentage, 2),
    "match_level": level,
    "skills_in_resume": resume_skills,
    "skills_required": jd_skills,
    "missing_skills": missing_skills
}