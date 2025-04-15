import re
from collections import Counter
import spacy
import PyPDF2
import ssl
import certifi
import urllib.request
ssl._create_default_https_context = ssl._create_unverified_context

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

import naukri-scrapper


"""PART-1   Extracting the skills from resume    """
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





"""Part-2   Mappping the skills to suitable job titles"""

# Expanded database of job titles mapped to required tech stacks and soft skills
job_database = {
    # Technology & Software Development
    "Frontend Developer": {
        "tech": ["html", "css", "javascript", "react", "angular", "vue", "sass", "webpack", "responsive design",
                 "typescript", "web accessibility", "seo"],
        "soft": ["attention to detail", "creativity", "problem solving", "teamwork", "time management"]
    },
    "Backend Developer": {
        "tech": ["python", "java", "c#", "node.js", "express", "django", "flask", "spring", "databases", "sql",
                 "mongodb", "api", "rest", "graphql", "microservices"],
        "soft": ["problem solving", "analytical thinking", "attention to detail", "system design",
                 "architecture planning"]
    },
    "Full Stack Developer": {
        "tech": ["html", "css", "javascript", "react", "vue", "angular", "node.js", "python", "java", "sql", "mongodb",
                 "api", "git", "docker", "full stack", "debugging"],
        "soft": ["problem solving", "adaptability", "time management", "teamwork", "multitasking", "communication"]
    },
    "Data Scientist": {
        "tech": ["python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow", "statistics",
                 "machine learning", "data visualization", "jupyter", "pytorch", "big data", "hypothesis testing"],
        "soft": ["analytical thinking", "critical thinking", "communication", "curiosity", "research", "storytelling"]
    },
    "DevOps Engineer": {
        "tech": ["linux", "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "ci/cd", "terraform", "ansible",
                 "git", "bash", "python", "monitoring", "logging", "security"],
        "soft": ["problem solving", "communication", "teamwork", "adaptability", "system thinking",
                 "automation mindset"]
    },
    "Cloud Engineer": {
        "tech": ["aws", "azure", "gcp", "terraform", "cloudformation", "serverless", "lambda", "s3", "ec2", "docker",
                 "kubernetes", "cloud security", "networking", "cost optimization"],
        "soft": ["problem solving", "adaptability", "communication", "continuous learning", "documentation"]
    },
    "Mobile Developer": {
        "tech": ["swift", "kotlin", "java", "react native", "flutter", "android", "ios", "mobile ui",
                 "app store optimization", "push notifications", "offline storage"],
        "soft": ["attention to detail", "problem solving", "creativity", "user empathy", "performance optimization"]
    },
    "UI/UX Designer": {
        "tech": ["figma", "sketch", "adobe xd", "photoshop", "illustrator", "wireframing", "prototyping",
                 "user research", "ui design", "usability testing", "information architecture", "design systems"],
        "soft": ["creativity", "empathy", "communication", "teamwork", "visual thinking", "user advocacy",
                 "design thinking"]
    },
    "Product Manager": {
        "tech": ["product development", "agile", "scrum", "jira", "product roadmap", "user stories", "market research",
                 "analytics", "a/b testing", "product strategy", "pricing"],
        "soft": ["leadership", "communication", "strategic thinking", "problem solving", "organization", "negotiation",
                 "empathy", "prioritization", "stakeholder management"]
    },
    "QA Engineer": {
        "tech": ["test automation", "selenium", "cypress", "jira", "test cases", "api testing", "performance testing",
                 "test planning", "regression testing", "qa processes", "bug tracking"],
        "soft": ["attention to detail", "analytical thinking", "communication", "thoroughness", "quality advocacy",
                 "documentation"]
    },
    "Database Administrator": {
        "tech": ["sql", "mysql", "postgresql", "oracle", "mongodb", "database design", "data modeling", "etl",
                 "performance tuning", "backup and recovery", "high availability", "security"],
        "soft": ["attention to detail", "problem solving", "analytical thinking", "systems thinking",
                 "data integrity focus"]
    },
    "Security Engineer": {
        "tech": ["network security", "penetration testing", "vulnerability assessment", "encryption", "firewalls",
                 "security protocols", "owasp", "threat modeling", "security frameworks", "compliance"],
        "soft": ["analytical thinking", "attention to detail", "ethics", "problem solving", "risk assessment",
                 "security mindset", "continuous learning"]
    },
    "Machine Learning Engineer": {
        "tech": ["python", "tensorflow", "pytorch", "keras", "scikit-learn", "deep learning", "nlp", "computer vision",
                 "ml ops", "feature engineering", "model deployment", "distributed training"],
        "soft": ["analytical thinking", "research", "innovation", "problem solving", "experimentation",
                 "mathematical intuition"]
    },
    "Data Engineer": {
        "tech": ["python", "sql", "spark", "hadoop", "etl", "data warehousing", "data modeling", "airflow", "kafka",
                 "data pipelines", "big data", "streaming data", "data governance"],
        "soft": ["problem solving", "attention to detail", "analytical thinking", "systems design",
                 "data quality focus"]
    },
    "Systems Administrator": {
        "tech": ["linux", "windows server", "active directory", "networking", "virtualization", "security",
                 "backup solutions", "troubleshooting", "scripting", "patch management"],
        "soft": ["problem solving", "attention to detail", "time management", "communication", "documentation",
                 "user support"]
    },
    "Network Engineer": {
        "tech": ["networking", "tcp/ip", "routing", "switching", "vpn", "firewalls", "dns", "dhcp", "cisco", "juniper",
                 "wan", "lan", "network security", "network monitoring"],
        "soft": ["problem solving", "attention to detail", "troubleshooting", "documentation", "continuous learning"]
    },
    "Blockchain Developer": {
        "tech": ["blockchain", "solidity", "ethereum", "smart contracts", "web3", "cryptography",
                 "consensus mechanisms", "decentralized apps", "bitcoin", "distributed systems"],
        "soft": ["analytical thinking", "security mindset", "attention to detail", "problem solving",
                 "continuous learning"]
    },
    "Game Developer": {
        "tech": ["c++", "c#", "unity", "unreal engine", "3d modeling", "game physics", "animation",
                 "graphics programming", "multiplayer", "game ai", "level design"],
        "soft": ["creativity", "problem solving", "teamwork", "attention to detail", "user experience focus",
                 "performance optimization"]
    },
    "Technical Writer": {
        "tech": ["markdown", "documentation", "api documentation", "technical writing", "git", "content management",
                 "developer tools", "publishing platforms", "information architecture"],
        "soft": ["communication", "attention to detail", "organization", "clarity", "research", "empathy for audience",
                 "simplification skills"]
    },
    "Site Reliability Engineer": {
        "tech": ["linux", "monitoring", "automation", "incident response", "kubernetes", "docker",
                 "infrastructure as code", "programming", "networking", "security", "cloud platforms"],
        "soft": ["problem solving", "analytical thinking", "communication", "calm under pressure", "systems thinking",
                 "process improvement"]
    },

    # Data & Analytics
    "Business Intelligence Analyst": {
        "tech": ["sql", "tableau", "power bi", "excel", "data visualization", "data modeling", "etl",
                 "data warehousing", "business metrics", "reporting", "dashboards"],
        "soft": ["analytical thinking", "business acumen", "communication", "attention to detail", "problem solving",
                 "storytelling"]
    },
    "Business Analyst": {
        "tech": ["sql", "excel", "tableau", "power bi", "requirements gathering", "user stories", "process modeling",
                 "jira", "data analysis", "crm systems"],
        "soft": ["analytical thinking", "communication", "organization", "problem solving", "stakeholder management",
                 "requirements elicitation", "process thinking"]
    },
    "Data Analyst": {
        "tech": ["sql", "excel", "python", "r", "data visualization", "tableau", "power bi", "statistics",
                 "data cleaning", "reporting", "spreadsheets"],
        "soft": ["analytical thinking", "attention to detail", "problem solving", "communication", "critical thinking",
                 "curiosity", "storytelling"]
    },
    "Market Research Analyst": {
        "tech": ["spss", "excel", "survey tools", "data visualization", "statistical analysis", "crm",
                 "market research methodologies", "data collection", "segmentation"],
        "soft": ["analytical thinking", "communication", "attention to detail", "curiosity", "objectivity",
                 "business acumen", "presentation skills"]
    },
    "Financial Analyst": {
        "tech": ["excel", "financial modeling", "accounting software", "bloomberg terminal", "sql", "erp systems",
                 "visualization tools", "forecasting", "budgeting", "valuation"],
        "soft": ["analytical thinking", "attention to detail", "critical thinking", "financial acumen", "communication",
                 "ethical judgment", "quantitative skills"]
    },

    # Healthcare
    "Registered Nurse": {
        "tech": ["electronic health records", "medical equipment", "patient monitoring", "medication administration",
                 "clinical procedures", "health informatics", "telehealth"],
        "soft": ["compassion", "communication", "critical thinking", "attention to detail", "teamwork",
                 "stress management", "adaptability", "patient advocacy"]
    },
    "Physician": {
        "tech": ["medical diagnostics", "treatment planning", "electronic health records", "medical imaging",
                 "clinical procedures", "medical devices", "pharmacology"],
        "soft": ["communication", "empathy", "critical thinking", "decision making", "ethics", "attention to detail",
                 "continuous learning", "patient rapport"]
    },
    "Physical Therapist": {
        "tech": ["rehabilitation techniques", "assessment methods", "therapeutic exercise", "mobility aids",
                 "electronic documentation", "therapeutic modalities"],
        "soft": ["empathy", "communication", "patience", "motivation", "attention to detail", "adaptability",
                 "problem solving", "interpersonal skills"]
    },
    "Medical Laboratory Technician": {
        "tech": ["lab equipment", "specimen processing", "testing procedures", "quality control",
                 "laboratory information systems", "safety protocols", "diagnostic techniques"],
        "soft": ["attention to detail", "precision", "analytical thinking", "problem solving", "time management",
                 "documentation", "teamwork"]
    },
    "Pharmacist": {
        "tech": ["pharmaceutical knowledge", "medication management", "pharmacy systems", "drug interactions",
                 "compounding", "inventory management", "prescription verification"],
        "soft": ["attention to detail", "communication", "ethics", "problem solving", "patient counseling", "teamwork",
                 "accuracy"]
    },
    "Healthcare Administrator": {
        "tech": ["healthcare management", "electronic health records", "medical billing", "healthcare regulations",
                 "financial management", "quality improvement", "healthcare analytics"],
        "soft": ["leadership", "communication", "organization", "problem solving", "ethics", "decision making",
                 "strategic thinking"]
    },

    # Education
    "Teacher": {
        "tech": ["curriculum development", "instructional methods", "educational technology", "assessment techniques",
                 "classroom management", "learning management systems"],
        "soft": ["communication", "patience", "adaptability", "creativity", "empathy", "organization", "leadership",
                 "conflict resolution"]
    },
    "School Counselor": {
        "tech": ["counseling techniques", "career assessment", "student information systems", "intervention strategies",
                 "psychological assessment", "academic planning"],
        "soft": ["empathy", "communication", "ethics", "patience", "problem solving", "confidentiality",
                 "cultural sensitivity", "relationship building"]
    },
    "College Professor": {
        "tech": ["research methods", "academic writing", "instructional design", "presentation software",
                 "learning management systems", "subject expertise", "publication"],
        "soft": ["communication", "critical thinking", "time management", "mentoring", "assessment", "research",
                 "public speaking", "collaboration"]
    },
    "Instructional Designer": {
        "tech": ["e-learning platforms", "multimedia design", "learning management systems", "authoring tools",
                 "curriculum development", "assessment design", "video production"],
        "soft": ["creativity", "communication", "organization", "problem solving", "adaptability",
                 "empathy for learners", "collaboration"]
    },

    # Finance & Accounting
    "Accountant": {
        "tech": ["accounting software", "excel", "tax preparation", "financial reporting", "gaap", "erp systems",
                 "auditing", "bookkeeping", "regulatory compliance"],
        "soft": ["attention to detail", "analytical thinking", "ethics", "time management", "organization", "accuracy",
                 "problem solving"]
    },
    "Financial Advisor": {
        "tech": ["financial planning software", "investment platforms", "tax planning", "retirement planning",
                 "estate planning", "financial analysis", "crm software"],
        "soft": ["communication", "ethics", "relationship building", "analytical thinking", "patience",
                 "trustworthiness", "listening skills"]
    },
    "Investment Banker": {
        "tech": ["financial modeling", "valuation", "excel", "bloomberg terminal", "capital markets",
                 "deal structuring", "financial analysis", "due diligence"],
        "soft": ["analytical thinking", "negotiation", "communication", "networking", "work ethic",
                 "attention to detail", "pressure management"]
    },
    "Actuary": {
        "tech": ["statistical analysis", "predictive modeling", "excel", "r", "python", "risk assessment",
                 "probability", "financial mathematics", "actuarial software"],
        "soft": ["analytical thinking", "problem solving", "attention to detail", "communication", "ethical judgment",
                 "continuous learning"]
    },
    "Risk Manager": {
        "tech": ["risk assessment", "financial analysis", "compliance", "regulatory knowledge", "scenario modeling",
                 "data analysis", "risk mitigation strategies"],
        "soft": ["analytical thinking", "decision making", "communication", "attention to detail", "foresight",
                 "ethics", "strategic thinking"]
    },

    # Marketing & Sales
    "Digital Marketing Specialist": {
        "tech": ["seo", "sem", "social media platforms", "google analytics", "content management systems",
                 "email marketing", "ppc advertising", "marketing automation"],
        "soft": ["creativity", "analytical thinking", "communication", "adaptability", "strategic thinking",
                 "customer focus", "trend awareness"]
    },
    "Sales Representative": {
        "tech": ["crm software", "sales tracking", "presentation tools", "proposal software", "lead generation tools",
                 "market research", "product knowledge"],
        "soft": ["communication", "negotiation", "relationship building", "persistence", "active listening",
                 "problem solving", "time management", "persuasion"]
    },
    "Marketing Manager": {
        "tech": ["marketing analytics", "project management", "budgeting", "campaign management", "market research",
                 "brand strategy", "digital marketing", "content strategy"],
        "soft": ["creativity", "strategic thinking", "leadership", "communication", "organization", "adaptability",
                 "collaboration", "customer insight"]
    },
    "Content Strategist": {
        "tech": ["content management systems", "seo", "analytics tools", "editorial planning", "content creation",
                 "publishing platforms", "audience research", "social media"],
        "soft": ["creativity", "strategic thinking", "communication", "organization", "adaptability", "storytelling",
                 "editing", "research"]
    },
    "Public Relations Specialist": {
        "tech": ["media monitoring", "press release writing", "social media management", "crm", "event planning",
                 "content creation", "media relations", "crisis management"],
        "soft": ["communication", "relationship building", "writing", "creativity", "strategic thinking",
                 "problem solving", "adaptability", "media savvy"]
    },

    # Human Resources
    "HR Manager": {
        "tech": ["hris systems", "applicant tracking systems", "performance management", "hr analytics",
                 "compensation planning", "benefits administration", "hr policies"],
        "soft": ["communication", "leadership", "ethics", "conflict resolution", "employee relations",
                 "problem solving", "discretion", "empathy"]
    },
    "Recruiter": {
        "tech": ["applicant tracking systems", "linkedin recruiting", "job boards", "crm", "resume screening",
                 "interviewing techniques", "social media recruiting", "talent assessment"],
        "soft": ["communication", "relationship building", "assessment", "negotiation", "organization",
                 "active listening", "persuasion", "judgment"]
    },
    "Training and Development Specialist": {
        "tech": ["learning management systems", "instructional design", "e-learning platforms", "training delivery",
                 "assessment design", "presentation software", "needs analysis"],
        "soft": ["communication", "organization", "creativity", "adaptability", "facilitation", "public speaking",
                 "empathy", "patience"]
    },
    "Compensation and Benefits Analyst": {
        "tech": ["hris", "compensation software", "benefits administration", "data analysis", "excel",
                 "market research", "compliance", "survey tools"],
        "soft": ["analytical thinking", "attention to detail", "ethics", "confidentiality", "communication",
                 "problem solving", "fairness"]
    },

    # Creative & Design
    "Graphic Designer": {
        "tech": ["adobe creative suite", "illustrator", "photoshop", "indesign", "typography", "color theory",
                 "layout design", "branding", "print production", "digital design"],
        "soft": ["creativity", "attention to detail", "time management", "communication", "problem solving",
                 "adaptability", "visual thinking", "accepting feedback"]
    },
    "Video Editor": {
        "tech": ["premiere pro", "final cut pro", "after effects", "audio editing", "color grading", "storytelling",
                 "motion graphics", "video production", "editing techniques"],
        "soft": ["creativity", "attention to detail", "patience", "time management", "storytelling", "collaboration",
                 "problem solving", "aesthetic sense"]
    },
    "Copywriter": {
        "tech": ["content creation", "seo writing", "editing", "research", "content management systems",
                 "marketing concepts", "brand voice", "social media writing"],
        "soft": ["creativity", "writing", "communication", "adaptability", "research", "attention to detail",
                 "deadline focus", "receiving feedback"]
    },
    "Art Director": {
        "tech": ["design software", "creative direction", "brand development", "visual storytelling", "typography",
                 "layout design", "multimedia", "campaign development"],
        "soft": ["leadership", "creativity", "communication", "strategic thinking", "project management",
                 "visual thinking", "problem solving", "collaboration"]
    },
    "Interior Designer": {
        "tech": ["cad software", "3d modeling", "color theory", "space planning", "materials knowledge",
                 "building codes", "sustainable design", "rendering software"],
        "soft": ["creativity", "attention to detail", "communication", "problem solving", "project management",
                 "client management", "aesthetic sense"]
    },

    # Engineering (Non-Software)
    "Civil Engineer": {
        "tech": ["autocad", "structural analysis", "construction methods", "project management", "civil 3d",
                 "building codes", "material science", "surveying", "soil mechanics"],
        "soft": ["problem solving", "attention to detail", "communication", "project management", "analytical thinking",
                 "teamwork", "mathematical skills"]
    },
    "Mechanical Engineer": {
        "tech": ["cad software", "finite element analysis", "thermodynamics", "fluid mechanics",
                 "manufacturing processes", "materials science", "product design", "prototyping"],
        "soft": ["problem solving", "analytical thinking", "creativity", "attention to detail", "teamwork",
                 "communication", "technical writing"]
    },
    "Electrical Engineer": {
        "tech": ["circuit design", "power systems", "control systems", "pcb design", "signal processing",
                 "microcontrollers", "electrical testing", "embedded systems"],
        "soft": ["problem solving", "analytical thinking", "attention to detail", "teamwork", "communication",
                 "mathematical skills", "technical documentation"]
    },
    "Aerospace Engineer": {
        "tech": ["aerodynamics", "propulsion systems", "structural analysis", "cad software",
                 "computational fluid dynamics", "materials science", "avionics", "flight dynamics"],
        "soft": ["analytical thinking", "problem solving", "attention to detail", "teamwork", "innovation",
                 "mathematical skills", "communication"]
    },
    "Biomedical Engineer": {
        "tech": ["medical device design", "biomaterials", "clinical evaluation", "regulatory standards",
                 "imaging systems", "electronics", "biomechanics", "tissue engineering"],
        "soft": ["problem solving", "analytical thinking", "ethics", "communication", "teamwork", "attention to detail",
                 "research"]
    },

    # Project & Operations Management
    "Project Manager": {
        "tech": ["project management software", "gantt charts", "resource allocation", "budgeting", "risk management",
                 "scrum", "agile", "kanban", "ms project", "jira"],
        "soft": ["leadership", "communication", "organization", "problem solving", "negotiation", "time management",
                 "conflict resolution", "adaptability", "stakeholder management"]
    },
    "Operations Manager": {
        "tech": ["erp systems", "process improvement", "quality management", "inventory management", "supply chain",
                 "data analysis", "forecasting", "resource planning"],
        "soft": ["leadership", "problem solving", "decision making", "communication", "strategic thinking",
                 "organization", "adaptability", "team management"]
    },
    "Supply Chain Manager": {
        "tech": ["supply chain management", "inventory systems", "logistics planning", "procurement", "erp systems",
                 "forecasting", "distribution", "vendor management"],
        "soft": ["analytical thinking", "problem solving", "leadership", "communication", "negotiation", "organization",
                 "global perspective"]
    },
    "Quality Assurance Manager": {
        "tech": ["quality management systems", "statistical process control", "six sigma", "iso standards",
                 "quality auditing", "compliance", "testing methods", "documentation"],
        "soft": ["attention to detail", "analytical thinking", "leadership", "communication", "problem solving",
                 "ethics", "continuous improvement mindset"]
    },

    # Legal
    "Lawyer": {
        "tech": ["legal research", "case management software", "document review", "legal writing", "contract drafting",
                 "legal analysis", "regulatory compliance"],
        "soft": ["analytical thinking", "communication", "negotiation", "ethics", "attention to detail", "research",
                 "problem solving", "public speaking"]
    },
    "Paralegal": {
        "tech": ["legal research", "document management", "case management software", "e-filing", "legal writing",
                 "legal procedures", "document preparation"],
        "soft": ["attention to detail", "organization", "communication", "research", "confidentiality",
                 "time management", "teamwork"]
    },
    "Compliance Officer": {
        "tech": ["regulatory knowledge", "compliance systems", "risk assessment", "audit procedures", "reporting",
                 "policy development", "investigation techniques"],
        "soft": ["ethics", "attention to detail", "communication", "analytical thinking", "problem solving",
                 "discretion", "integrity"]
    },

    # Scientific Research
    "Research Scientist": {
        "tech": ["laboratory techniques", "experimental design", "data analysis", "scientific instrumentation",
                 "research methodologies", "statistics", "publication", "grant writing"],
        "soft": ["analytical thinking", "problem solving", "attention to detail", "curiosity", "teamwork",
                 "communication", "ethics", "patience"]
    },
    "Environmental Scientist": {
        "tech": ["environmental sampling", "gis", "data analysis", "field research", "environmental regulations",
                 "modeling", "remediation techniques", "monitoring systems"],
        "soft": ["analytical thinking", "problem solving", "communication", "teamwork", "ethics", "adaptability",
                 "observation skills"]
    },
    "Bioinformatician": {
        "tech": ["python", "r", "bioinformatics tools", "genomics", "statistics", "database management",
                 "sequence analysis", "computational biology", "data visualization"],
        "soft": ["analytical thinking", "problem solving", "attention to detail", "communication", "research",
                 "collaboration", "interdisciplinary thinking"]
    },

    # Architecture & Construction
    "Architect": {
        "tech": ["autocad", "revit", "building information modeling", "3d modeling", "building codes",
                 "sustainable design", "construction documentation", "rendering"],
        "soft": ["creativity", "communication", "problem solving", "attention to detail", "project management",
                 "spatial thinking", "client management"]
    },
    "Construction Manager": {
        "tech": ["construction methods", "project scheduling", "budgeting", "building codes", "safety protocols",
                 "blueprint reading", "contract management", "quality control"],
        "soft": ["leadership", "communication", "problem solving", "organization", "negotiation", "conflict resolution",
                 "decision making", "time management"]
    },
    "Urban Planner": {
        "tech": ["gis", "zoning regulations", "land use planning", "transportation planning", "urban design",
                 "environmental impact assessment", "demographic analysis"],
        "soft": ["analytical thinking", "communication", "problem solving", "creativity", "collaboration",
                 "public engagement", "long-term vision"]
    },

    # Journalism & Media
    "Journalist": {
        "tech": ["reporting", "interviewing", "fact checking", "writing", "multimedia production", "research",
                 "social media", "content management systems"],
        "soft": ["communication", "ethics", "curiosity", "adaptability", "critical thinking", "objectivity",
                 "deadline management", "storytelling"]
    },
    "Social Media Manager": {
        "tech": ["social media platforms", "content creation", "scheduling tools", "analytics", "community management",
                 "campaign management", "digital marketing", "seo"],
        "soft": ["creativity", "communication", "adaptability", "strategy", "writing", "time management",
                 "trend awareness", "crisis management"]
    },
    "Video Producer": {
        "tech": ["video production", "editing software", "camera operation", "lighting", "sound recording",
                 "storyboarding", "post-production", "production planning"],
        "soft": ["creativity", "leadership", "communication", "problem solving", "organization", "attention to detail",
                 "storytelling", "teamwork"]
    },

    # Customer Service & Hospitality
    "Customer Service Representative": {
        "tech": ["crm software", "ticketing systems", "communication tools", "product knowledge", "documentation",
                 "problem resolution", "data entry", "telephony systems"],
        "soft": ["communication", "patience", "empathy", "problem solving", "adaptability", "conflict resolution",
                 "active listening", "positive attitude"]
    },
    "Hotel Manager": {
        "tech": ["property management systems", "revenue management", "booking systems", "inventory management",
                 "financial management", "marketing", "customer service"],
        "soft": ["leadership", "communication", "problem solving", "customer focus", "organization", "adaptability",
                 "conflict resolution", "cultural awareness"]
    },
    "Event Planner": {
        "tech": ["event management software", "budgeting", "vendor management", "logistics planning", "marketing",
                 "registration systems", "contract negotiation"],
        "soft": ["organization", "communication", "problem solving", "creativity", "attention to detail",
                 "time management", "negotiation", "adaptability"]
    },

    # Transportation & Logistics
    "Air Traffic Controller": {
        "tech": ["radar systems", "air traffic control procedures", "navigation systems", "communication protocols",
                 "weather monitoring", "emergency procedures"],
        "soft": ["attention to detail", "decision making", "communication", "stress management", "spatial awareness",
                 "multitasking", "clear speech"]
    },
    "Logistics Coordinator": {
        "tech": ["transportation management systems", "inventory management", "route planning",
                 "shipping documentation", "customs regulations", "supply chain", "freight forwarding"],
        "soft": ["organization", "problem solving", "communication", "attention to detail", "adaptability",
                 "time management", "negotiation"]
    },
    "Commercial Pilot": {
        "tech": ["aircraft operation", "navigation systems", "flight planning", "weather interpretation",
                 "emergency procedures", "communication protocols", "aircraft systems"],
        "soft": ["decision making", "communication", "attention to detail", "situational awareness",
                 "stress management", "teamwork", "problem solving"]
    },

    # Executive & Leadership
    "Chief Executive Officer (CEO)": {
        "tech": ["strategic planning", "financial management", "market analysis", "business operations",
                 "investor relations", "corporate governance", "industry knowledge"],
        "soft": ["leadership", "strategic thinking", "decision making", "communication", "vision setting",
                 "negotiation", "emotional intelligence", "resilience"]
    },
    "Chief Technology Officer (CTO)": {
        "tech": ["technology strategy", "software architecture", "emerging technologies", "product development",
                 "it infrastructure", "cybersecurity", "digital transformation"],
        "soft": ["leadership", "strategic thinking", "communication", "problem solving", "decision making",
                 "innovation", "technical vision", "business acumen"]
    },
    "Chief Marketing Officer (CMO)": {
        "tech": ["marketing strategy", "brand management", "digital marketing", "market analysis",
                 "campaign management", "marketing analytics", "customer experience"],
        "soft": ["leadership", "creativity", "strategic thinking", "communication", "analytical thinking",
                 "customer focus", "adaptability", "innovation"]
    },
    "Chief Financial Officer (CFO)": {
        "tech": ["financial planning", "accounting principles", "treasury management", "risk management",
                 "investment strategy", "financial reporting", "regulatory compliance"],
        "soft": ["leadership", "analytical thinking", "strategic thinking", "ethics", "communication",
                 "attention to detail", "decision making"]
    },

    # Manufacturing & Production
    "Production Manager": {
        "tech": ["production planning", "quality control", "lean manufacturing", "inventory management",
                 "process improvement", "machinery operation", "safety protocols"],
        "soft": ["leadership", "problem solving", "communication", "organization", "decision making", "adaptability",
                 "teamwork"]
    },
    "Manufacturing Engineer": {
        "tech": ["cad/cam", "production processes", "lean manufacturing", "quality control", "automation",
                 "industrial engineering", "material science", "process optimization"],
        "soft": ["problem solving", "analytical thinking", "communication", "attention to detail", "teamwork",
                 "continuous improvement mindset"]
    },

    # Sports & Fitness
    "Athletic Trainer": {
        "tech": ["injury assessment", "rehabilitation techniques", "treatment modalities", "emergency care",
                 "taping methods", "exercise prescription", "medical equipment"],
        "soft": ["communication", "empathy", "decision making", "adaptability", "attention to detail", "teamwork",
                 "patience"]
    },
    "Sports Coach": {
        "tech": ["sport techniques", "training methodology", "performance analysis", "game strategy",
                 "conditioning programming", "video analysis", "skill development"],
        "soft": ["leadership", "communication", "motivation", "adaptability", "patience", "psychology", "teaching",
                 "teamwork"]
    },
    "Personal Trainer": {
        "tech": ["exercise technique", "program design", "fitness assessment", "nutrition knowledge", "anatomy",
                 "injury prevention", "equipment usage", "health monitoring"],
        "soft": ["communication", "motivation", "empathy", "adaptability", "patience", "customer service",
                 "relationship building"]
    },

    # Miscellaneous Specialized Roles
    "Translator": {
        "tech": ["language fluency", "translation software", "cultural knowledge", "terminology management", "editing",
                 "localization", "subject matter expertise"],
        "soft": ["attention to detail", "cultural sensitivity", "research", "time management", "adaptability",
                 "communication", "continuous learning"]
    },
    "Data Privacy Officer": {
        "tech": ["data protection regulations", "privacy frameworks", "risk assessment", "compliance monitoring",
                 "security protocols", "audit procedures", "policy development"],
        "soft": ["ethics", "analytical thinking", "communication", "attention to detail", "problem solving",
                 "diplomacy", "integrity"]
    },
    "Ethical Hacker": {
        "tech": ["penetration testing", "vulnerability assessment", "network security", "programming",
                 "operating systems", "security tools", "cryptography", "reverse engineering"],
        "soft": ["ethical judgment", "analytical thinking", "problem solving", "attention to detail", "communication",
                 "creativity", "persistence"]
    },
    "Drone Operator": {
        "tech": ["drone piloting", "aerial photography", "flight planning", "equipment maintenance",
                 "weather interpretation", "navigation", "data processing", "regulations"],
        "soft": ["attention to detail", "spatial awareness", "problem solving", "adaptability", "communication",
                 "safety focus", "technical aptitude"]
    },
    "Astronaut": {
        "tech": ["spacecraft systems", "space navigation", "scientific experimentation", "robotics",
                 "emergency procedures", "EVA procedures", "life support systems"],
        "soft": ["mental fortitude", "teamwork", "problem solving", "adaptability", "communication",
                 "attention to detail", "physical fitness", "stress management"]
    },
}


def preprocess_skills(skills_input):
    """Convert input string to list of skills and normalize them"""
    # Split by commas, newlines, or semicolons
    skills = re.split(r'[,;\n]+', skills_input.lower())
    # Clean up each skill
    skills = [skill.strip() for skill in skills if skill.strip()]
    return skills


def match_skills_to_jobs(skills):
    """Match input skills to potential job titles"""
    job_scores = {}

    for job_title, requirements in job_database.items():
        tech_matches = sum(1 for skill in skills if
                           any(tech_skill in skill or skill in tech_skill for tech_skill in requirements["tech"]))
        soft_matches = sum(1 for skill in skills if
                           any(soft_skill in skill or skill in soft_skill for soft_skill in requirements["soft"]))

        # Calculate a score based on matches and the total number of skills required
        total_required = len(requirements["tech"]) + len(requirements["soft"])
        total_matches = tech_matches + soft_matches

        if total_matches > 0:
            # Score is a combination of absolute matches and percentage of required skills
            match_percentage = total_matches / len(skills) if skills else 0
            req_percentage = total_matches / total_required if total_required else 0
            job_scores[job_title] = (total_matches, match_percentage, req_percentage)

    return job_scores


def get_top_recommendations(job_scores, top_n=5):
    """Get top job recommendations based on scores"""
    # Sort by total matches (index 0) in descending order
    sorted_jobs = sorted(job_scores.items(), key=lambda x: (x[1][0], x[1][1], x[1][2]), reverse=True)
    return sorted_jobs[:top_n]


def suggest_jobs(skills_input):

    if not skills_input.strip():
        print("No skills provided. Please try again with some skills.")
        return

    skills = preprocess_skills(skills_input)
    job_scores = match_skills_to_jobs(skills)

    if not job_scores:
        print("\nNo matching job titles found for your skills. Try adding more skills or different keywords.")
        return

    recommendations = get_top_recommendations(job_scores)
    recomm_jobs=[]
    print("\n----- TOP JOB RECOMMENDATIONS -----")
    for i, (job_title, (matches, match_percent, req_percent)) in enumerate(recommendations, 1):

        print(f"{i}. {job_title}")
        recomm_jobs.append(job_title)

    print(recomm_jobs)
    return recomm_jobs

"""Part 3"""
def scrape_monster_jobs(job_title, location, num_pages=2):
    driver = uc.Chrome()
    jobs_list = []

    try:
        base_url = "https://www.monster.com/jobs/search/"
        query = f"?q={job_title.replace(' ', '+')}&where={location.replace(' ', '+')}"
        full_url = base_url + query
        print(full_url)
        driver.get(full_url)
        time.sleep(5)

        for page in range(num_pages):
            print(f"📄 Scanning Page {page + 1}: {driver.current_url}")

            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.card-content")

            print(f"🔍 Found {len(job_cards)} job cards.")

            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2.title > a").text.strip()
                    url = card.find_element(By.CSS_SELECTOR, "h2.title > a").get_attribute("href")
                    company = card.find_element(By.CSS_SELECTOR, "div.company > span.name").text.strip()
                    location = card.find_element(By.CSS_SELECTOR, "div.location > span.name").text.strip()

                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": url
                    })
                except Exception as e:
                    print(f"❌ Error extracting job: {e}")

            # Try to go to the next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.btn-next")
                if "disabled" in next_button.get_attribute("class"):
                    print("⛔ Next button disabled.")
                    break
                next_button.click()
                time.sleep(4)
            except Exception as e:
                print("🚫 No more pages or next button not found.")
                break

    finally:
         driver.quit()
    return pd.DataFrame(jobs_list)




if __name__ == "__main__":
    skills = extract_resume_skills("Ashmit123.pdf")
    delimiter=","
    skills=delimiter.join(skills)
    job=suggest_jobs(skills)

    scraper = naukri.NaukriSeleniumScraper(
        headless=True,  # Set to False to see the browser in action
        disable_images=True  # Disable images to speed up scraping
    )

    jobs = scraper.run_scraper(
        keyword=job[4],
        location="Banglore",
        experience=2,
        pages=3,  # Number of pages to scrape
        fetch_details=False  # Set to True to fetch detailed job information
    )





