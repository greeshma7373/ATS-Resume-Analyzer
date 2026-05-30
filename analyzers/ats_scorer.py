# analyzers/ats_scorer.py
# ATS scoring engine using TF-IDF, cosine similarity, and rule-based analysis

import re
import sys
import os
from typing import Dict, List, Tuple, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.skills_data import SECTION_KEYWORDS, ATS_KEYWORDS, ACTION_VERBS
from analyzers.skill_extractor import (
    extract_skills, extract_soft_skills, analyze_action_verbs,
    extract_years_of_experience, calculate_keyword_density
)
from parsers.resume_parser import extract_contact_info, split_into_sections


# ─── Scoring weights (must sum to 100) ──────────────────────────────────────
SCORE_WEIGHTS = {
    "contact_info":     8,   # Has email, phone, LinkedIn, GitHub
    "skills":           20,  # Technical skill richness
    "experience":       20,  # Work experience section quality
    "education":        12,  # Education section presence
    "projects":         12,  # Projects section
    "summary":          8,   # Professional summary
    "action_verbs":     8,   # Strong action verb usage
    "readability":      6,   # Text length and structure
    "keyword_density":  6,   # ATS keyword presence
}
assert sum(SCORE_WEIGHTS.values()) == 100, "Weights must sum to 100"


def score_contact_info(text: str, contact: dict) -> Tuple[float, List[str]]:
    """Score contact information completeness."""
    score = 0
    insights = []
    max_score = SCORE_WEIGHTS["contact_info"]

    checks = {
        "email": (contact.get("email"), max_score * 0.35, "Add a professional email address"),
        "phone": (contact.get("phone"), max_score * 0.25, "Include a phone number"),
        "linkedin": (contact.get("linkedin"), max_score * 0.20, "Add your LinkedIn profile URL"),
        "github": (contact.get("github"), max_score * 0.20, "Add your GitHub profile URL (especially for tech roles)"),
    }

    for field, (value, weight, tip) in checks.items():
        if value:
            score += weight
        else:
            insights.append(f"💡 {tip}")

    return min(score, max_score), insights


def score_skills(resume_skills: Dict) -> Tuple[float, List[str]]:
    """Score technical skill breadth and depth."""
    max_score = SCORE_WEIGHTS["skills"]
    insights = []

    total_skills = sum(len(v) for v in resume_skills.values())
    category_count = len(resume_skills)

    # Base score from total unique skills
    base = min(total_skills * 1.5, max_score * 0.7)
    # Bonus for category diversity
    diversity = min(category_count * 1.2, max_score * 0.3)
    score = base + diversity

    if total_skills < 5:
        insights.append("💡 Add more technical skills — ATS systems look for skill-rich resumes")
    if category_count < 3:
        insights.append("💡 Diversify your skill categories (languages, frameworks, tools, cloud)")
    if "Cloud" not in resume_skills:
        insights.append("💡 Consider adding cloud platform experience (AWS/Azure/GCP)")
    if "Tools & Platforms" not in resume_skills:
        insights.append("💡 Add DevOps/tooling skills (Git, Docker, CI/CD)")

    return min(score, max_score), insights


def score_experience(text: str, sections: dict) -> Tuple[float, List[str]]:
    """Score work experience section."""
    max_score = SCORE_WEIGHTS["experience"]
    insights = []
    score = 0

    exp_text = sections.get("experience", "")
    has_section = bool(exp_text and len(exp_text) > 50)

    if not has_section:
        insights.append("⚠️ No clear 'Experience' section detected — add work/internship experience")
        return 0, insights

    score += max_score * 0.3  # Has section

    # Check for date ranges (indicates real experience)
    date_pattern = r'\b(20\d{2}|19\d{2})\b'
    dates = re.findall(date_pattern, exp_text)
    if len(dates) >= 2:
        score += max_score * 0.2
    else:
        insights.append("💡 Include date ranges for each position (e.g., Jan 2022 – Present)")

    # Check for company names (Title Case words near dates)
    bullet_pattern = r'[•\-\*\u2022]'
    bullets = re.findall(bullet_pattern, exp_text)
    if len(bullets) >= 3:
        score += max_score * 0.2
        # Check for measurable achievements
        number_pattern = r'\b\d+[%x+]?\b'
        numbers = re.findall(number_pattern, exp_text)
        if len(numbers) >= 2:
            score += max_score * 0.2
        else:
            insights.append("💡 Add measurable achievements (e.g., 'Reduced load time by 40%', 'Served 10K+ users')")
    else:
        insights.append("💡 Use bullet points to describe your responsibilities and achievements")

    years = extract_years_of_experience(text)
    if years > 0:
        score += min(max_score * 0.1, years * 1.0)
    else:
        insights.append("💡 Mention total years of experience explicitly in your summary")

    return min(score, max_score), insights


def score_education(sections: dict) -> Tuple[float, List[str]]:
    """Score education section."""
    max_score = SCORE_WEIGHTS["education"]
    insights = []
    edu_text = sections.get("education", "")

    if not edu_text or len(edu_text) < 30:
        insights.append("⚠️ Add an Education section (degree, institution, year)")
        return 0, insights

    score = max_score * 0.5  # Has section

    # Check for degree keywords
    degree_keywords = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e",
                       "b.sc", "m.sc", "mba", "bca", "mca", "diploma", "degree"]
    if any(kw in edu_text.lower() for kw in degree_keywords):
        score += max_score * 0.3

    # Check for year
    if re.search(r'\b20\d{2}\b', edu_text):
        score += max_score * 0.2
    else:
        insights.append("💡 Include graduation year in your education section")

    return min(score, max_score), insights


def score_projects(sections: dict) -> Tuple[float, List[str]]:
    """Score projects section."""
    max_score = SCORE_WEIGHTS["projects"]
    insights = []
    proj_text = sections.get("projects", "")

    if not proj_text or len(proj_text) < 50:
        insights.append("💡 Add a Projects section showcasing relevant work (especially for freshers)")
        return 0, insights

    score = max_score * 0.4  # Has section

    # Check for technology mentions
    tech_words = re.findall(r'\b[A-Z][a-z]*(?:\.[a-z]+)?\b', proj_text)
    if len(tech_words) >= 3:
        score += max_score * 0.2

    # Check for links (GitHub, deployed URLs)
    url_pattern = r'https?://\S+|github\.com/\S+'
    links = re.findall(url_pattern, proj_text, re.IGNORECASE)
    if links:
        score += max_score * 0.2
    else:
        insights.append("💡 Add GitHub/live links to your projects — ATS and recruiters value verifiable work")

    # Check for impact descriptions
    number_pattern = r'\b\d+[%x+K]?\b'
    numbers = re.findall(number_pattern, proj_text)
    if numbers:
        score += max_score * 0.2
    else:
        insights.append("💡 Quantify project impact (e.g., '500+ users', '3x faster', '95% accuracy')")

    return min(score, max_score), insights


def score_summary(sections: dict) -> Tuple[float, List[str]]:
    """Score professional summary/objective."""
    max_score = SCORE_WEIGHTS["summary"]
    insights = []
    summary_text = sections.get("summary", "")

    if not summary_text or len(summary_text) < 30:
        insights.append("💡 Add a 2-3 sentence Professional Summary at the top of your resume")
        return 0, insights

    word_count = len(summary_text.split())
    if 30 <= word_count <= 100:
        score = max_score
    elif word_count < 30:
        score = max_score * 0.5
        insights.append("💡 Expand your summary — aim for 50-80 words covering your role, experience, and key skills")
    else:
        score = max_score * 0.7
        insights.append("💡 Shorten your summary — keep it concise (50-80 words)")

    return score, insights


def score_action_verbs(text: str) -> Tuple[float, List[str]]:
    """Score quality of action verbs used."""
    max_score = SCORE_WEIGHTS["action_verbs"]
    insights = []
    verb_analysis = analyze_action_verbs(text)

    score = min(verb_analysis["score"], max_score)

    if verb_analysis["weak_count"] > verb_analysis["strong_count"]:
        insights.append(f"💡 Replace weak verbs ({', '.join(verb_analysis['weak_verbs'][:3])}) with strong ones like 'Architected', 'Optimized', 'Engineered'")
    if verb_analysis["strong_count"] < 5:
        insights.append("💡 Use more strong action verbs (e.g., Spearheaded, Delivered, Automated, Designed)")

    return score, insights


def score_readability(text: str) -> Tuple[float, List[str]]:
    """Score resume readability and length."""
    max_score = SCORE_WEIGHTS["readability"]
    insights = []

    word_count = len(text.split())
    line_count = len([l for l in text.split('\n') if l.strip()])

    # Ideal: 400-700 words for 1-page, up to 1000 for 2-page
    if 400 <= word_count <= 1000:
        score = max_score
    elif word_count < 200:
        score = max_score * 0.3
        insights.append("⚠️ Resume is too short — add more detail about your experience and projects")
    elif word_count < 400:
        score = max_score * 0.6
        insights.append("💡 Resume is brief — consider expanding descriptions of your experience")
    elif word_count > 1000:
        score = max_score * 0.7
        insights.append("💡 Resume may be too long — aim for 1-2 pages (400-800 words)")
    else:
        score = max_score

    return min(score, max_score), insights


def score_keyword_density(text: str) -> Tuple[float, List[str]]:
    """Score ATS keyword presence."""
    max_score = SCORE_WEIGHTS["keyword_density"]
    insights = []

    density = calculate_keyword_density(text, ATS_KEYWORDS)
    score = min(density * 20, max_score)  # Scale to max_score

    if density < 0.5:
        insights.append("💡 Include more industry-standard keywords (agile, cross-functional, data-driven, scalable)")

    return score, insights


def calculate_ats_score(text: str, job_description: Optional[str] = None) -> Dict:
    """
    Main ATS scoring function. Returns comprehensive score breakdown.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    contact = extract_contact_info(text)
    sections = split_into_sections(text)
    resume_skills = extract_skills(text)

    # Calculate section scores
    contact_score, contact_insights = score_contact_info(text, contact)
    skills_score, skills_insights = score_skills(resume_skills)
    experience_score, experience_insights = score_experience(text, sections)
    education_score, education_insights = score_education(sections)
    projects_score, projects_insights = score_projects(sections)
    summary_score, summary_insights = score_summary(sections)
    verb_score, verb_insights = score_action_verbs(text)
    readability_score, readability_insights = score_readability(text)
    keyword_score, keyword_insights = score_keyword_density(text)

    # Base ATS score
    base_score = (
        contact_score + skills_score + experience_score +
        education_score + projects_score + summary_score +
        verb_score + readability_score + keyword_score
    )

    # Job description similarity boost
    jd_similarity = 0.0
    if job_description and job_description.strip():
        try:
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([text, job_description])
            jd_similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            # Add up to 15 bonus points for JD match
            jd_bonus = jd_similarity * 15
            base_score = min(base_score + jd_bonus, 100)
        except Exception:
            pass

    # Compile all insights
    all_insights = (
        contact_insights + skills_insights + experience_insights +
        education_insights + projects_insights + summary_insights +
        verb_insights + readability_insights + keyword_insights
    )

    return {
        "total_score": round(base_score, 1),
        "section_scores": {
            "Contact Info": round(contact_score, 1),
            "Skills": round(skills_score, 1),
            "Experience": round(experience_score, 1),
            "Education": round(education_score, 1),
            "Projects": round(projects_score, 1),
            "Summary": round(summary_score, 1),
            "Action Verbs": round(verb_score, 1),
            "Readability": round(readability_score, 1),
            "Keywords": round(keyword_score, 1),
        },
        "max_scores": SCORE_WEIGHTS,
        "insights": all_insights,
        "jd_similarity": round(jd_similarity * 100, 1),
        "contact": contact,
        "sections": sections,
        "resume_skills": resume_skills,
        "verb_analysis": analyze_action_verbs(text),
        "word_count": len(text.split()),
    }


def calculate_job_match(resume_text: str, role: str) -> Dict:
    """Calculate how well a resume matches a specific job role."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from data.skills_data import JOB_ROLES
    from analyzers.skill_extractor import get_missing_skills

    if role not in JOB_ROLES:
        return {"error": f"Role '{role}' not found"}

    role_data = JOB_ROLES[role]
    resume_skills = extract_skills(resume_text)

    all_resume_skills = []
    for skills in resume_skills.values():
        all_resume_skills.extend([s.lower() for s in skills])

    # Count matching skills per tier
    required_match = sum(1 for s in role_data["required"] if any(s.lower() in rs or rs in s.lower() for rs in all_resume_skills))
    preferred_match = sum(1 for s in role_data["preferred"] if any(s.lower() in rs or rs in s.lower() for rs in all_resume_skills))
    bonus_match = sum(1 for s in role_data["bonus"] if any(s.lower() in rs or rs in s.lower() for rs in all_resume_skills))

    required_pct = (required_match / len(role_data["required"])) * 100 if role_data["required"] else 0
    preferred_pct = (preferred_match / len(role_data["preferred"])) * 100 if role_data["preferred"] else 0
    bonus_pct = (bonus_match / len(role_data["bonus"])) * 100 if role_data["bonus"] else 0

    # Weighted match score
    match_score = (required_pct * 0.6) + (preferred_pct * 0.3) + (bonus_pct * 0.1)

    # TF-IDF similarity with role keywords
    role_keywords_text = " ".join(role_data["required"] + role_data["preferred"])
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text, role_keywords_text])
        tfidf_sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100
        match_score = (match_score * 0.7) + (tfidf_sim * 0.3)
    except Exception:
        pass

    missing = get_missing_skills(resume_skills, {
        "Required": role_data["required"],
        "Preferred": role_data["preferred"],
    })

    # Learning path
    learning_path = []
    if missing.get("Required"):
        learning_path.append(f"🔴 Master required skills: {', '.join(missing['Required'][:4])}")
    if missing.get("Preferred"):
        learning_path.append(f"🟡 Learn preferred skills: {', '.join(missing['Preferred'][:4])}")
    if bonus_match < len(role_data["bonus"]) // 2:
        bonus_missing = [s for s in role_data["bonus"] if not any(s.lower() in rs for rs in all_resume_skills)]
        learning_path.append(f"🟢 Stand out with: {', '.join(bonus_missing[:3])}")

    return {
        "role": role,
        "match_score": round(match_score, 1),
        "required_match": round(required_pct, 1),
        "preferred_match": round(preferred_pct, 1),
        "bonus_match": round(bonus_pct, 1),
        "missing_skills": missing,
        "learning_path": learning_path,
        "description": role_data["description"],
    }
