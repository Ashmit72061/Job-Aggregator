import time
import re
import spacy
import PyPDF2
from collections import Counter

# Caching the NLP model globally for efficiency
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
    """Load a list of common technical and soft skills."""
    technical_skills = [
        "python", "java", "javascript", "C++", "c#", "ruby", "php", "swift", "kotlin",
        "react.js", "angular", "vue", "node.js", "django", "flask", "spring", "express",
        "html5", "css", "sass", "bootstrap", "tailwind", "jquery", "typescript",
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github",
        "sql", "mysql", "postgresql", "mongodb", "oracle", "sql server", "sqlite",
        "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras",
        "data analysis", "data science", "data visualization", "power bi", "tableau", "excel",
        "hadoop", "spark", "kafka", "elasticsearch", "redis", "graphql", "rest api",
        "agile", "scrum", "kanban", "jira", "confluence", "trello", "asana",
        "linux", "unix", "windows", "macos", "shell scripting", "bash", "powershell",
        "networking", "cybersecurity", "penetration testing", "cloud computing",
        "mobile development", "android", "ios", "react native", "flutter", "xamarin",
        "devops", "ci/cd", "test automation", "selenium", "junit", "pytest", "mocha",
        "R", "matlab", "sas", "spss", "numpy", "pandas", "scipy", "scikit-learn",
        "blockchain", "ethereum", "solidity", "web3", "smart contracts",
        "photoshop", "illustrator", "indesign", "figma", "sketch", "adobe xd",
        "wordpress", "shopify", "woocommerce", "magento", "drupal", "joomla"
    ]

    soft_skills = [
        "communication", "teamwork", "leadership", "problem solving", "critical thinking",
        "time management", "organization", "creativity", "adaptability", "flexibility",
        "work ethic", "interpersonal skills", "emotional intelligence", "collaboration",
        "conflict resolution", "decision making", "presentation", "negotiation",
        "persuasion", "customer service", "attention to detail", "analytical thinking",
        "strategic planning", "research", "writing", "verbal communication",
        "project management", "mentoring", "coaching", "public speaking",
        "active listening", "patience", "empathy", "self motivation", "resourcefulness",
        "reliability", "accountability", "multitasking", "prioritization"
    ]

    return technical_skills + soft_skills


def extract_skills_with_spacy(text):
    nlp = load_spacy_model()
    doc = nlp(text)
    return set(
        chunk.text.lower().strip() for chunk in doc.noun_chunks if 1 <= len(chunk.text.split()) <= 3
    )


def extract_skill_sections(text):
    patterns = [r'(skills|technologies|competencies).*?(\n\n|$)']
    return re.findall('|'.join(patterns), text, re.IGNORECASE | re.DOTALL)


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
    skills = extract_skills(text, common_skills)
    return skills


# Example usage
if __name__ == "__main__":
    skills = extract_resume_skills("PDF_PATH")#ENTER THE PATH OF PDF
    if skills:
        print("\nSkills found in the resume:")
        for i, skill in enumerate(skills, 1):
            print(f"{i}. {skill}")
    else:
        print("\nNo skills found in the resume.")
