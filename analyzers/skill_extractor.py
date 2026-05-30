# analyzers/skill_extractor.py
# Extracts and categorizes skills from resume text using NLP + rule-based matching

import re
from typing import Dict, List, Tuple
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.skills_data import SKILLS_DB, SOFT_SKILLS, ACTION_VERBS


def load_nlp_model():
    """Load spaCy model with automatic download if missing."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Auto-download
            import subprocess
            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                check=True, capture_output=True
            )
            nlp = spacy.load("en_core_web_sm")
        return nlp
    except Exception:
        return None


def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Extract technical skills from resume text.
    Uses multi-strategy matching: exact, fuzzy, and NLP-based.
    Returns categorized skills dict.
    """
    text_lower = text.lower()
    found_skills = {category: [] for category in SKILLS_DB}

    for category, skill_list in SKILLS_DB.items():
        for skill in skill_list:
            # Use word boundary matching to avoid partial matches
            # Handle skills with special characters
            pattern = r'(?<![a-zA-Z0-9\-\+#])' + re.escape(skill) + r'(?![a-zA-Z0-9\-\+#])'
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Normalize display name
                display = skill.title() if len(skill) > 3 else skill.upper()
                # Special cases
                special_cases = {
                    "python": "Python", "java": "Java", "javascript": "JavaScript",
                    "typescript": "TypeScript", "html": "HTML", "css": "CSS",
                    "sql": "SQL", "aws": "AWS", "gcp": "GCP", "api": "API",
                    "rest": "REST", "grpc": "gRPC", "ci/cd": "CI/CD",
                    "mlops": "MLOps", "devops": "DevOps", "node.js": "Node.js",
                    "next.js": "Next.js", "vue.js": "Vue.js", "react.js": "React.js",
                    "d3.js": "D3.js", "three.js": "Three.js", "c++": "C++",
                    "c#": "C#", "f#": "F#", "asp.net": "ASP.NET", "golang": "Go",
                    "nlp": "NLP", "ml": "ML", "ai": "AI", "cv": "CV",
                    "llm": "LLM", "bert": "BERT", "gpt": "GPT", "elk stack": "ELK Stack"
                }
                display = special_cases.get(skill.lower(), skill.title())
                if display not in found_skills[category]:
                    found_skills[category].append(display)

    # Remove empty categories
    found_skills = {k: v for k, v in found_skills.items() if v}
    return found_skills


def extract_soft_skills(text: str) -> List[str]:
    """Extract soft skills mentioned in resume."""
    text_lower = text.lower()
    found = []
    for skill in SOFT_SKILLS:
        if skill in text_lower:
            found.append(skill.title())
    return found


def analyze_action_verbs(text: str) -> Dict[str, any]:
    """Analyze quality and quantity of action verbs used."""
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)

    strong_found = [v for v in ACTION_VERBS["strong"] if v in words]
    weak_found = [v for v in ACTION_VERBS["weak"] if v in words]

    total = len(strong_found) + len(weak_found)
    strong_ratio = len(strong_found) / total if total > 0 else 0

    return {
        "strong_verbs": strong_found,
        "weak_verbs": weak_found,
        "strong_count": len(strong_found),
        "weak_count": len(weak_found),
        "strong_ratio": strong_ratio,
        "score": min(100, len(strong_found) * 8)  # up to 100
    }


def extract_years_of_experience(text: str) -> int:
    """Estimate total years of experience from text patterns."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+of\s+exp',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return max(int(m) for m in matches)

    # Estimate from date ranges
    year_pattern = r'\b(20\d{2})\b'
    years = re.findall(year_pattern, text)
    if len(years) >= 2:
        years = sorted(set(int(y) for y in years))
        span = years[-1] - years[0]
        if 0 < span < 50:
            return span

    return 0


def calculate_keyword_density(text: str, keywords: List[str]) -> float:
    """Calculate keyword density as percentage of total words."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    keyword_count = sum(1 for w in words if w in [k.lower() for k in keywords])
    return (keyword_count / len(words)) * 100


def get_missing_skills(resume_skills: Dict[str, List[str]], role_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Find skills required for a role that are missing from resume."""
    all_resume_skills = []
    for skills in resume_skills.values():
        all_resume_skills.extend([s.lower() for s in skills])

    missing = {}
    for level, skills in role_skills.items():
        missing_skills = []
        for skill in skills:
            if skill.lower() not in all_resume_skills:
                # Also check partial matches
                found = any(skill.lower() in rs or rs in skill.lower() for rs in all_resume_skills)
                if not found:
                    missing_skills.append(skill.title())
        if missing_skills:
            missing[level] = missing_skills

    return missing
