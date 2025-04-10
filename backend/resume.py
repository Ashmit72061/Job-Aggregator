import PyPDF2
import re
import spacy
import argparse
from collections import Counter

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def preprocess_text(text):
    """Clean and preprocess the extracted text."""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    
    return text.strip()

def load_common_skills():
    """Load a list of common technical and soft skills."""
    technical_skills = [
        "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin",
        "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
        "html", "css", "sass", "bootstrap", "tailwind", "jquery", "typescript",
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
        "r", "matlab", "sas", "spss", "numpy", "pandas", "scipy", "scikit-learn",
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
    """Extract skills using spaCy's named entity recognition and noun chunks."""
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("Downloading spaCy model...")
        import subprocess
        subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    
    doc = nlp(text)
    
    # Extract noun phrases as potential skills
    potential_skills = [chunk.text.lower() for chunk in doc.noun_chunks]
    
    # Add entities that might be skills
    potential_skills.extend([ent.text.lower() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]])
    
    return potential_skills

def extract_skills(text, common_skills):
    """Extract skills from preprocessed text using multiple techniques."""
    skills = set()
    
    # Method 1: Check for common skills in the text
    for skill in common_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            skills.add(skill)
    
    # Method 2: Use spaCy to extract potential skills
    potential_skills = extract_skills_with_spacy(text)
    
    # Filter potential skills
    for skill in potential_skills:
        words = skill.split()
        # Only consider phrases with 1-3 words
        if 1 <= len(words) <= 3:
            # Check if any of the common skills is a subset of the potential skill
            for common_skill in common_skills:
                if common_skill in skill and len(common_skill) > 3:
                    skills.add(common_skill)
    
    # Method 3: Look for skills in sections likely to contain skills
    skill_sections = extract_skill_sections(text)
    for section in skill_sections:
        section_skills = extract_skills_from_section(section, common_skills)
        skills.update(section_skills)
    
    return list(skills)

def extract_skill_sections(text):
    """Extract sections likely to contain skills from the resume."""
    skill_section_patterns = [
        r'(?i)skills.*?(?=\n\n|\Z)',
        r'(?i)technical skills.*?(?=\n\n|\Z)',
        r'(?i)professional skills.*?(?=\n\n|\Z)',
        r'(?i)core competencies.*?(?=\n\n|\Z)',
        r'(?i)technologies.*?(?=\n\n|\Z)',
        r'(?i)proficiencies.*?(?=\n\n|\Z)'
    ]
    
    sections = []
    for pattern in skill_section_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        sections.extend(matches)
    
    return sections

def extract_skills_from_section(section, common_skills):
    """Extract skills from a section specifically containing skills."""
    skills = set()
    
    # Look for bullet points or comma-separated lists
    items = re.split(r'[,•\n]', section)
    
    for item in items:
        item = item.strip().lower()
        if not item:
            continue
        
        # Check if the entire item is a common skill
        if item in common_skills:
            skills.add(item)
            continue
        
        # Check if the item contains any common skills
        for skill in common_skills:
            if len(skill) > 3 and skill in item:  # Avoid short skills that might occur as part of other words
                if re.search(r'\b' + re.escape(skill) + r'\b', item):
                    skills.add(skill)
    
    return skills

def main():
    parser = argparse.ArgumentParser(description='Extract skills from a resume PDF')
    parser.add_argument('Ashmit123.pdf', help='Path to the resume PDF file')
    args = parser.parse_args()
    
    # Extract text from PDF
    print(f"Extracting text from {args.pdf_path}...")
    pdf_text = extract_text_from_pdf(args.pdf_path)
    
    if not pdf_text:
        print("Failed to extract text from the PDF. Please check the file path and format.")
        return
    
    # Preprocess the text
    preprocessed_text = preprocess_text(pdf_text)
    
    # Load common skills
    common_skills = load_common_skills()
    
    # Extract skills
    skills = extract_skills(preprocessed_text, common_skills)
    
    # Print results
    if skills:
        print("\nSkills found in the resume:")
        for i, skill in enumerate(sorted(skills), 1):
            print(f"{i}. {skill}")
    else:
        print("\nNo skills were identified in the resume.")
    
    return skills

if __name__ == "__main__":
    main()
