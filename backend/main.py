from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import re
import json
import ssl
import time
import spacy
import PyPDF2
import certifi
import urllib.request
from collections import Counter

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

import naukri_scrapper as naukri  # Assuming this file exists in your backend folder

# ========== FASTAPI SETUP ==========

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow everything temporarily
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== HELPERS ==========

def clear_folder(upload_dir):
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# ========== RESUME PROCESSING + JOB MATCHING ==========

nlp = None

def load_spacy_model():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
    return nlp

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return " ".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def preprocess_text(text):
    return re.sub(r'[\W_]+', ' ', text.lower()).strip()

def load_common_skills():
    return [
        "python", "java", "javascript", "c++", "react.js", "node.js", "html5", "css", "git", "sql", "mongodb",
        "data analysis", "machine learning", "tensorflow", "pytorch", "keras",
        "communication", "teamwork", "leadership", "problem solving", "adaptability"
    ]

def extract_skills_with_spacy(text):
    nlp = load_spacy_model()
    doc = nlp(text)
    return set(chunk.text.lower().strip() for chunk in doc.noun_chunks if 1 <= len(chunk.text.split()) <= 3)

def extract_skills(text, common_skills):
    found_skills = set()
    words = set(text.split())
    found_skills.update(skill for skill in common_skills if skill in words)
    potential_skills = extract_skills_with_spacy(text)
    found_skills.update(skill for skill in common_skills if any(skill in ps for ps in potential_skills))
    return sorted(found_skills)

def extract_resume_skills(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("No text found in the PDF.")
        return []
    text = preprocess_text(text)
    common_skills = load_common_skills()
    return extract_skills(text, common_skills)

def preprocess_skills(skills_input):
    skills = re.split(r'[,;\n]+', skills_input.lower())
    return [skill.strip() for skill in skills if skill.strip()]

f = open("job_data.json", "r")
job_database = json.load(f)

def match_skills_to_jobs(skills):
    job_scores = {}
    for job_title, requirements in job_database.items():
        tech_matches = sum(1 for skill in skills if any(tech in skill or skill in tech for tech in requirements["tech"]))
        soft_matches = sum(1 for skill in skills if any(soft in skill or skill in soft for soft in requirements["soft"]))
        total_required = len(requirements["tech"]) + len(requirements["soft"])
        total_matches = tech_matches + soft_matches
        if total_matches > 0:
            match_percentage = total_matches / len(skills) if skills else 0
            req_percentage = total_matches / total_required if total_required else 0
            job_scores[job_title] = (total_matches, match_percentage, req_percentage)
    return job_scores

def get_top_recommendations(job_scores, top_n=5):
    sorted_jobs = sorted(job_scores.items(), key=lambda x: (x[1][0], x[1][1], x[1][2]), reverse=True)
    return sorted_jobs[:top_n]

def suggest_jobs(skills_input):
    if not skills_input.strip():
        return []
    skills = preprocess_skills(skills_input)
    job_scores = match_skills_to_jobs(skills)
    if not job_scores:
        return []
    recommendations = get_top_recommendations(job_scores)
    return [title for title, _ in recommendations]

# ========== FINAL PROCESSING FUNCTION ==========

def final_data(file_path):
    skills = extract_resume_skills(file_path)
    skill_string = ",".join(skills)
    recommended_jobs = suggest_jobs(skill_string)

    if not recommended_jobs:
        return {"skills": skills, "jobs": [], "naukri": []}

    # Scrape jobs from Naukri for the top recommendation
    scraper = naukri.NaukriSeleniumScraper(
        headless=True,
        disable_images=True
    )

    scraped_jobs = scraper.run_scraper(
        keyword=recommended_jobs[0],
        location="Bangalore",
        experience=2,
        pages=3,
        fetch_details=False
    )

    return {
        "skills": skills,
        "jobs": recommended_jobs,
        "naukri": scraped_jobs
    }

# ========== FASTAPI ROUTE ==========

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    clear_folder(upload_dir)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Final logic trigger
    result = final_data(file_path)

    return {
        "message": "File processed successfully!",
        "filename": file.filename,
        "skills": result["skills"],
        "matched_jobs": result["jobs"],
        "naukri_jobs": result["naukri"]
    }

f.close()
