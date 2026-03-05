from fastapi import FastAPI, UploadFile, File, Form
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import numpy as np
import requests
import os

app = FastAPI()

# -----------------------------
# Load Embedding Model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Skill List
# -----------------------------
COMMON_SKILLS = [
    "python","java","sql","javascript","html","css",
    "machine learning","deep learning","fastapi","django",
    "flask","docker","aws","react","node","git",
    "mongodb","postgresql","kubernetes"
]

# -----------------------------
# API Key (use environment variable)
# -----------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# -----------------------------
# LLM Feedback Function
# -----------------------------
def get_ai_feedback(resume_text, job_description, missing_skills):

    prompt = f"""
You are an AI career assistant.

Analyze the resume against the job description.

Job Description:
{job_description}

Resume:
{resume_text}

Missing Skills:
{missing_skills}

Give short suggestions to improve the resume.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        if "error" in result:
            return f"AI feedback unavailable: {result['error']}"

        return "AI feedback unavailable."

    except Exception as e:
        return f"AI feedback error: {str(e)}"


# -----------------------------
# Resume Analyzer Endpoint
# -----------------------------
@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):

    try:

        # Reset file pointer
        resume.file.seek(0)

        # Read PDF
        reader = PdfReader(resume.file)

        resume_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume_text += text

        # -----------------------------
        # Embeddings
        # -----------------------------
        resume_embedding = model.encode([resume_text])[0]
        jd_embedding = model.encode([job_description])[0]

        resume_vec = np.array(resume_embedding)
        jd_vec = np.array(jd_embedding)

        # -----------------------------
        # Cosine Similarity
        # -----------------------------
        similarity = np.dot(resume_vec, jd_vec) / (
            np.linalg.norm(resume_vec) * np.linalg.norm(jd_vec)
        )

        # -----------------------------
        # Match Percentage
        # -----------------------------
        match_percentage = max(0, similarity) * 100

        if match_percentage < 30:
            level = "Low Match"
        elif match_percentage < 60:
            level = "Moderate Match"
        else:
            level = "Strong Match"

        # -----------------------------
        # Skill Extraction
        # -----------------------------
        resume_text_lower = resume_text.lower()
        jd_text_lower = job_description.lower()

        resume_skills = [
            skill for skill in COMMON_SKILLS if skill in resume_text_lower
        ]

        jd_skills = [
            skill for skill in COMMON_SKILLS if skill in jd_text_lower
        ]

        missing_skills = [
            skill for skill in jd_skills if skill not in resume_skills
        ]

        # -----------------------------
        # AI Feedback
        # -----------------------------
        ai_feedback = get_ai_feedback(
            resume_text,
            job_description,
            missing_skills
        )

        # -----------------------------
        # Final Response
        # -----------------------------
        return {
            "match_percentage": round(match_percentage, 2),
            "match_level": level,
            "skills_in_resume": resume_skills,
            "skills_required": jd_skills,
            "missing_skills": missing_skills,
            "ai_feedback": ai_feedback
        }

    except Exception as e:
        return {"error": str(e)}