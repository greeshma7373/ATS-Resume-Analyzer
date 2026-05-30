# app.py
# AI Resume Analyzer & ATS Score Checker
# 100% offline — no paid APIs required

import sys
import os

# ── Bootstrap: ensure dependencies are available ─────────────────────────────
def bootstrap_dependencies():
    """Download spaCy model and NLTK data safely — works on Streamlit Cloud."""

    # ── spaCy model ──────────────────────────────────────────────────────────
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
        except OSError:
            # Use pip to install the model wheel directly — works on all platforms
            import pip
            pip.main(["install",
                      "https://github.com/explosion/spacy-models/releases/download/"
                      "en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl",
                      "--quiet"])
            try:
                spacy.load("en_core_web_sm")
            except Exception:
                # Final fallback: link after pip install
                from spacy.cli import download as spacy_download
                spacy_download("en_core_web_sm")
    except Exception:
        pass

    # ── NLTK data ────────────────────────────────────────────────────────────
    try:
        import nltk
        nltk.data.path.append(os.path.join(os.path.expanduser("~"), "nltk_data"))
        for pkg, kind in [('punkt', 'tokenizers'), ('punkt_tab', 'tokenizers'),
                          ('stopwords', 'corpora'), ('wordnet', 'corpora')]:
            try:
                nltk.data.find(f'{kind}/{pkg}')
            except LookupError:
                nltk.download(pkg, quiet=True)
    except Exception:
        pass

bootstrap_dependencies()

# ── Imports ───────────────────────────────────────────────────────────────────
import streamlit as st
import plotly.graph_objects as go

# Local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsers.resume_parser import extract_text_from_pdf, extract_name, count_pages
from analyzers.ats_scorer import calculate_ats_score, calculate_job_match
from analyzers.skill_extractor import extract_skills, extract_soft_skills, analyze_action_verbs
from components.ui_components import (
    render_score_gauge, render_section_bar_chart, render_skill_radar,
    render_skill_bubbles, render_job_match_chart, score_badge,
    keyword_pills, missing_keyword_pills
)
from utils.report_generator import generate_pdf_report
from data.skills_data import JOB_ROLES

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'About': '# AI Resume Analyzer\nBuilt with ❤️ using Python & Streamlit'
    }
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* Root variables */
:root {
    --bg-primary: #0a0f1e;
    --bg-secondary: #0f172a;
    --bg-card: #111827;
    --bg-card-hover: #1a2440;
    --border: #2a3a5c;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;
    --text-label: #a0b0c8;
}

/* Global overrides — bright readable text everywhere */
.stApp { background: var(--bg-primary); }
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary) !important;
}

/* Force all paragraph and span text to be bright */
p, span, div, li, td, th, label {
    color: var(--text-primary);
}

/* Hide Streamlit default elements */
#MainMenu, footer, .stDeployButton { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.stAppDeployButton { display: none !important; }
header[data-testid="stHeader"] {
    background: rgba(10,15,30,0.95);
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(10px);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #0a0f1e 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 { color: var(--accent-light); }

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: var(--text-secondary) !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.5) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--accent) !important;
    border-radius: 16px !important;
    background: rgba(99,102,241,0.05) !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] * { color: var(--text-secondary) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #ffffff !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] label {
    color: var(--text-label) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* Streamlit native text elements */
.stMarkdown p { color: var(--text-secondary) !important; }
.stMarkdown strong { color: #f8fafc !important; }
.stMarkdown li { color: var(--text-secondary) !important; }

/* Progress bars */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--accent), #818cf8) !important;
    border-radius: 10px !important;
}
.stProgress > div > div {
    background: var(--border) !important;
    border-radius: 10px !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}
.stSelectbox label { color: var(--text-secondary) !important; }

/* Text areas */
.stTextArea textarea {
    background: #0d1529 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
}
.stTextArea label { color: var(--text-secondary) !important; }

/* Info/success/warning boxes */
.stAlert { border-radius: 12px !important; border-left: 4px solid !important; }
.stAlert p { color: #f8fafc !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* ── Custom components ───────────────────────────── */

.resume-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.75rem 0;
    transition: all 0.2s ease;
    color: #f8fafc;
}
.resume-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.resume-card p, .resume-card span, .resume-card div,
.resume-card li, .resume-card td { color: #cbd5e1; }

.stat-card {
    background: linear-gradient(135deg, var(--bg-card), #151f35);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    text-align: center;
}

.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.insight-item {
    background: rgba(99,102,241,0.10);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.9rem;
    color: #e2e8f0 !important;
    line-height: 1.6;
    font-weight: 450;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #818cf8, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    letter-spacing: -0.03em;
}

.hero-sub {
    font-size: 1.15rem;
    color: #cbd5e1;
    font-weight: 400;
    line-height: 1.7;
    max-width: 560px;
}

code, .mono {
    font-family: 'JetBrains Mono', monospace;
    background: rgba(99,102,241,0.15);
    color: #c4b5fd;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
}

/* Table text */
table td, table th { color: #e2e8f0 !important; }

/* Lists inside cards */
ul li, ol li { color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "resume_text": None,
        "resume_name": None,
        "ats_result": None,
        "job_match": None,
        "selected_role": list(JOB_ROLES.keys())[0],
        "jd_text": "",
        "page": "home",
        "candidate_name": "Candidate",
        "page_count": 1,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <div style="font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:900;
                  background:linear-gradient(135deg,#818cf8,#a855f7);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        🎯 ResumeIQ
      </div>
      <div style="color:#94a3b8;font-size:0.75rem;letter-spacing:0.1em;margin-top:4px">AI RESUME ANALYZER</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    pages = {
        "🏠 Home": "home",
        "📄 Upload Resume": "upload",
        "📊 ATS Analysis": "ats",
        "🔧 Skill Analysis": "skills",
        "🎯 Job Match": "jobmatch",
        "💡 Suggestions": "suggestions",
    }

    for label, page_id in pages.items():
        is_active = st.session_state.page == page_id
        if st.button(
            label,
            key=f"nav_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("---")

    if st.session_state.resume_text:
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #2a3a5c;border-radius:12px;padding:1rem">
          <div style="color:#a0b0c8;font-size:0.7rem;letter-spacing:0.1em;margin-bottom:6px">LOADED RESUME</div>
          <div style="color:#f1f5f9;font-weight:600;font-size:0.9rem">📄 {st.session_state.resume_name}</div>
          <div style="color:#94a3b8;font-size:0.75rem;margin-top:4px">{st.session_state.page_count} page(s) • {len(st.session_state.resume_text.split())} words</div>
          {"<div style='margin-top:8px'>" + score_badge(st.session_state.ats_result['total_score']) + "</div>" if st.session_state.ats_result else ""}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#111827;border:1px dashed #2a3a5c;border-radius:12px;padding:1rem;text-align:center">
          <div style="color:#cbd5e1;font-size:0.85rem">No resume loaded yet</div>
          <div style="color:#818cf8;font-size:0.75rem;margin-top:4px">Upload on the Resume page →</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem;padding:1rem;text-align:center">
      <div style="color:#94a3b8;font-size:0.7rem">100% Open Source · No API Keys</div>
      <div style="color:#94a3b8;font-size:0.7rem">Runs fully offline after install</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

# ── HOME PAGE ─────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    # Hero
    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.markdown('<div class="hero-title">AI-Powered<br>Resume Analyzer</div>', unsafe_allow_html=True)
        st.markdown('<p class="hero-sub">Get your ATS score, discover missing skills, and land more interviews — 100% free, open-source, and runs entirely offline.</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Analyze My Resume", use_container_width=True, type="primary"):
            st.session_state.page = "upload"
            st.rerun()

    with col2:
        st.markdown("")  # empty right column — layout balance

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # Feature cards
    st.markdown('<div class="section-header">What ResumeIQ Does</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    feat_cols = st.columns(3, gap="medium")
    features = [
        ("📊", "ATS Score Analysis", "9-dimensional scoring using TF-IDF, cosine similarity, and rule-based NLP. See exactly why you're failing ATS filters."),
        ("🔧", "Skill Extraction", "Automatically categorize 200+ tech skills from your resume across 7 categories: languages, frontend, backend, cloud, AI/ML, and more."),
        ("🎯", "Job Role Matching", "Compare your profile against 8 job roles with required/preferred/bonus skill tiers and get a personalized learning path."),
        ("💡", "Smart Suggestions", "Get specific, actionable improvement tips: add measurable metrics, strengthen verbs, fix missing sections, boost keywords."),
        ("🔍", "Gap Detection", "Upload a job description and instantly see which keywords you're missing vs. present — visual pill-based comparison."),
        ("📥", "PDF Report", "Download a polished ATS analysis report with section scores, detected skills, suggestions, and job match results."),
    ]

    for i, (icon, title, desc) in enumerate(features):
        with feat_cols[i % 3]:
            st.markdown(f"""
            <div class="resume-card">
              <div style="font-size:2rem;margin-bottom:0.5rem">{icon}</div>
              <div style="font-weight:700;font-size:1rem;color:#f1f5f9;margin-bottom:0.5rem">{title}</div>
              <div style="color:#cbd5e1;font-size:0.85rem;line-height:1.6">{desc}</div>
            </div>
            """, unsafe_allow_html=True)




# ── UPLOAD PAGE ───────────────────────────────────────────────────────────────
elif st.session_state.page == "upload":
    st.markdown('<div class="section-header">📄 Upload Your Resume</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#cbd5e1">Upload a PDF resume to begin analysis. All processing happens locally — your file never leaves your device.</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 0.7], gap="large")

    with col1:
        uploaded = st.file_uploader(
            "Drop your PDF resume here",
            type=["pdf"],
            help="Supports single and multi-page PDFs",
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**Paste Job Description (Optional)**")
        st.markdown('<p style="color:#cbd5e1;font-size:0.85rem">Adding a JD improves keyword gap detection and ATS score accuracy.</p>', unsafe_allow_html=True)
        jd_input = st.text_area(
            "Job Description",
            value=st.session_state.jd_text,
            height=160,
            placeholder="Paste the job description here...\n\nE.g.: We are looking for a Python developer with 2+ years experience in Django, REST APIs, PostgreSQL...",
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if uploaded:
            if st.button("🚀 Analyze Resume", use_container_width=True, type="primary"):
                with st.spinner("🔍 Extracting text from PDF..."):
                    text = extract_text_from_pdf(uploaded)
                    page_count = count_pages(uploaded)

                if text.startswith("ERROR"):
                    st.error(text)
                elif len(text.strip()) < 50:
                    st.error("⚠️ Could not extract meaningful text. The PDF may be image-based or encrypted. Try a text-based PDF.")
                else:
                    st.session_state.resume_text = text
                    st.session_state.resume_name = uploaded.name
                    st.session_state.jd_text = jd_input
                    st.session_state.page_count = page_count
                    st.session_state.candidate_name = extract_name(text)

                    with st.spinner("📊 Running ATS analysis..."):
                        result = calculate_ats_score(text, jd_input if jd_input.strip() else None)
                        st.session_state.ats_result = result

                    with st.spinner("🎯 Computing job match..."):
                        role = st.session_state.selected_role
                        match = calculate_job_match(text, role)
                        st.session_state.job_match = match

                    st.success(f"✅ Resume analyzed! ATS Score: **{result['total_score']}/100**")
                    st.balloons()

                    if st.button("View Full Analysis →", type="primary"):
                        st.session_state.page = "ats"
                        st.rerun()

    with col2:
        st.markdown("**Target Job Role**")
        role_select = st.selectbox(
            "Select role",
            options=list(JOB_ROLES.keys()),
            index=list(JOB_ROLES.keys()).index(st.session_state.selected_role),
            label_visibility="collapsed"
        )
        st.session_state.selected_role = role_select

        if role_select in JOB_ROLES:
            role_data = JOB_ROLES[role_select]
            st.markdown(f"""
            <div class="resume-card" style="margin-top:0.5rem">
              <div style="color:#818cf8;font-weight:700;font-size:0.95rem;margin-bottom:0.5rem">{role_select}</div>
              <div style="color:#cbd5e1;font-size:0.82rem;margin-bottom:1rem">{role_data['description']}</div>
              <div style="color:#a0b0c8;font-size:0.78rem;font-weight:600;margin-bottom:4px">REQUIRED SKILLS</div>
              {keyword_pills(role_data['required'][:5])}
              <div style="color:#a0b0c8;font-size:0.78rem;font-weight:600;margin:8px 0 4px">PREFERRED</div>
              {keyword_pills(role_data['preferred'][:4], '#1a3a2a')}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="resume-card">
          <div style="font-weight:700;color:#e2e8f0;margin-bottom:0.75rem">📋 Tips for Best Results</div>
          <ul style="color:#cbd5e1;font-size:0.83rem;line-height:1.9;padding-left:1.2rem;margin:0">
            <li>Use a text-based PDF (not scanned image)</li>
            <li>Include all sections: Experience, Education, Skills, Projects</li>
            <li>Use standard section headings</li>
            <li>Avoid tables and columns in PDF — plain layout works best</li>
            <li>Include a job description for better keyword gap analysis</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    # Show existing resume text preview if loaded
    if st.session_state.resume_text:
        st.markdown("---")
        with st.expander(f"📄 Currently Loaded: {st.session_state.resume_name} — Text Preview"):
            st.text_area("Extracted Text", st.session_state.resume_text[:2000] + "..." if len(st.session_state.resume_text) > 2000 else st.session_state.resume_text,
                        height=250, disabled=True)


# ── ATS ANALYSIS PAGE ─────────────────────────────────────────────────────────
elif st.session_state.page == "ats":
    if not st.session_state.ats_result:
        st.warning("⚠️ No resume analyzed yet. Please upload a resume first.")
        if st.button("← Go to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        st.stop()

    result = st.session_state.ats_result
    score = result["total_score"]

    st.markdown('<div class="section-header">📊 ATS Score Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#cbd5e1">Analysis for: <strong style="color:#f1f5f9">{st.session_state.candidate_name}</strong> · {st.session_state.resume_name}</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Score overview row
    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    grade = "A+" if score >= 85 else "A" if score >= 80 else "B+" if score >= 75 else "B" if score >= 65 else "C+" if score >= 55 else "C" if score >= 45 else "D"
    label = "Excellent" if score >= 80 else "Good" if score >= 65 else "Average" if score >= 50 else "Needs Work"

    with col1: st.metric("ATS Score", f"{score}/100")
    with col2: st.metric("Grade", grade)
    with col3: st.metric("Status", label)
    with col4: st.metric("Word Count", result["word_count"])
    with col5: st.metric("JD Similarity", f"{result['jd_similarity']}%" if result['jd_similarity'] > 0 else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main layout: gauge + section bars
    col_gauge, col_bars = st.columns([0.45, 0.55], gap="large")

    with col_gauge:
        render_score_gauge(score, "ATS Score")

        # Score interpretation
        if score >= 80:
            bg, icon, msg = "#14532d", "🏆", "Excellent! Your resume is well-optimized for ATS systems."
        elif score >= 65:
            bg, icon, msg = "#14532d", "✅", "Good score! A few tweaks will push you into the excellent range."
        elif score >= 50:
            bg, icon, msg = "#713f12", "⚡", "Average. Your resume needs improvement to pass ATS filters consistently."
        else:
            bg, icon, msg = "#7f1d1d", "❌", "Low score. Focus on the suggestions below to significantly improve your ATS performance."

        st.markdown(f"""
        <div style="background:{bg}20;border:1px solid {bg}80;border-radius:12px;padding:1rem;text-align:center">
          <div style="font-size:1.5rem">{icon}</div>
          <div style="color:#e2e8f0;font-size:0.85rem;margin-top:4px;line-height:1.5">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_bars:
        st.markdown("**Section-Wise Breakdown**")
        render_section_bar_chart(result["section_scores"], result["max_scores"])

    # ── Progress bars detail ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Detailed Section Scores**")
    st.markdown("<br>", unsafe_allow_html=True)

    max_scores_map = {
        "Contact Info": 8, "Skills": 20, "Experience": 20, "Education": 12,
        "Projects": 12, "Summary": 8, "Action Verbs": 8, "Readability": 6, "Keywords": 6
    }

    score_cols = st.columns(3, gap="medium")
    for i, (section, s_score) in enumerate(result["section_scores"].items()):
        max_s = max_scores_map.get(section, 10)
        pct = int((s_score / max_s) * 100) if max_s > 0 else 0
        color = "#22c55e" if pct >= 75 else "#eab308" if pct >= 50 else "#ef4444"

        with score_cols[i % 3]:
            st.markdown(f"""
            <div class="resume-card" style="padding:1rem">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                <span style="font-weight:600;font-size:0.9rem;color:#e2e8f0">{section}</span>
                <span style="font-weight:700;color:{color}">{s_score}/{max_s}</span>
              </div>
            """, unsafe_allow_html=True)
            st.progress(pct / 100)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Insights ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header" style="font-size:1.2rem">💡 Improvement Insights</div>', unsafe_allow_html=True)

    if result["insights"]:
        ins_cols = st.columns(2, gap="medium")
        for i, insight in enumerate(result["insights"]):
            with ins_cols[i % 2]:
                st.markdown(f'<div class="insight-item">{insight}</div>', unsafe_allow_html=True)
    else:
        st.success("🎉 Great job! No major issues found. Your resume looks well-optimized.")

    # ── Download Report ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**📥 Download ATS Report**")
    col_dl1, col_dl2 = st.columns([0.4, 0.6])
    with col_dl1:
        pdf_bytes = generate_pdf_report(
            st.session_state.candidate_name,
            result,
            st.session_state.job_match
        )
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"ATS_Report_{st.session_state.candidate_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    # ── JD Keyword Analysis ───────────────────────────────────────────────────
    if st.session_state.jd_text.strip() and result['jd_similarity'] > 0:
        st.markdown("---")
        st.markdown(f'<div class="section-header" style="font-size:1.2rem">🔍 Job Description Keyword Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#cbd5e1">Similarity score: <strong style="color:#818cf8">{result["jd_similarity"]}%</strong></p>', unsafe_allow_html=True)

        # Simple keyword overlap visualization
        import re
        resume_words = set(re.findall(r'\b[a-zA-Z+#]{3,}\b', st.session_state.resume_text.lower()))
        jd_words = set(re.findall(r'\b[a-zA-Z+#]{3,}\b', st.session_state.jd_text.lower()))

        # Filter meaningful words (skip stopwords)
        stop = {'the', 'and', 'for', 'are', 'you', 'will', 'with', 'this', 'that', 'have',
                'from', 'our', 'your', 'they', 'their', 'not', 'but', 'all', 'can', 'any'}
        jd_words = {w for w in jd_words if w not in stop and len(w) > 3}
        resume_words = {w for w in resume_words if w not in stop and len(w) > 3}

        present = sorted(jd_words & resume_words)[:30]
        missing = sorted(jd_words - resume_words)[:30]

        kw_col1, kw_col2 = st.columns(2, gap="medium")
        with kw_col1:
            st.markdown(f"**✅ Present Keywords** ({len(present)} found)")
            st.markdown(keyword_pills(present[:20], '#1a3a2a'), unsafe_allow_html=True)
        with kw_col2:
            st.markdown(f"**❌ Missing Keywords** ({len(missing)} missing)")
            st.markdown(missing_keyword_pills(missing[:20]), unsafe_allow_html=True)


# ── SKILL ANALYSIS PAGE ───────────────────────────────────────────────────────
elif st.session_state.page == "skills":
    if not st.session_state.resume_text:
        st.warning("⚠️ Please upload a resume first.")
        if st.button("← Go to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        st.stop()

    st.markdown('<div class="section-header">🔧 Skill Analysis</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#cbd5e1">Deep dive into the technical and soft skills detected in your resume.</p>', unsafe_allow_html=True)

    resume_skills = st.session_state.ats_result["resume_skills"]
    soft_skills = extract_soft_skills(st.session_state.resume_text)
    verb_analysis = st.session_state.ats_result["verb_analysis"]
    total_skills = sum(len(v) for v in resume_skills.values())

    st.markdown("<br>", unsafe_allow_html=True)

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1: st.metric("Total Tech Skills", total_skills)
    with m2: st.metric("Skill Categories", len(resume_skills))
    with m3: st.metric("Soft Skills", len(soft_skills))
    with m4: st.metric("Strong Action Verbs", verb_analysis["strong_count"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    tab1, tab2, tab3 = st.tabs(["📊 Skill Map", "🕸️ Radar Chart", "🔤 Action Verbs"])

    with tab1:
        st.markdown("**Skill Category Treemap**")
        render_skill_bubbles(resume_skills)

    with tab2:
        st.markdown("**Skill Coverage by Category**")
        render_skill_radar(resume_skills)

    with tab3:
        col_v1, col_v2 = st.columns(2, gap="large")
        with col_v1:
            st.markdown(f"**✅ Strong Verbs Found** ({verb_analysis['strong_count']})")
            if verb_analysis["strong_verbs"]:
                st.markdown(keyword_pills(verb_analysis["strong_verbs"], '#14532d'), unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#ef4444">No strong action verbs detected.</p>', unsafe_allow_html=True)

        with col_v2:
            st.markdown(f"**⚠️ Weak Verbs to Replace** ({verb_analysis['weak_count']})")
            if verb_analysis["weak_verbs"]:
                st.markdown(missing_keyword_pills(verb_analysis["weak_verbs"]), unsafe_allow_html=True)
            else:
                st.success("No weak verbs found!")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**💡 Strong Verb Suggestions**")
            suggestions = ["Architected", "Engineered", "Optimized", "Deployed", "Automated",
                          "Spearheaded", "Delivered", "Streamlined", "Pioneered", "Reduced"]
            st.markdown(keyword_pills(suggestions, '#1e3a5f'), unsafe_allow_html=True)

    # Skill detail by category
    st.markdown("---")
    st.markdown("**Detected Skills by Category**")
    st.markdown("<br>", unsafe_allow_html=True)

    if resume_skills:
        cat_cols = st.columns(2, gap="medium")
        for i, (category, skills) in enumerate(resume_skills.items()):
            with cat_cols[i % 2]:
                st.markdown(f"""
                <div class="resume-card">
                  <div style="font-weight:700;color:#818cf8;margin-bottom:0.75rem">
                    {category} <span style="color:#94a3b8;font-weight:400;font-size:0.85rem">({len(skills)} skills)</span>
                  </div>
                  {keyword_pills(skills)}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("No technical skills detected. Ensure your resume lists skills clearly.")

    # Soft skills
    if soft_skills:
        st.markdown("---")
        st.markdown("**💼 Soft Skills Detected**")
        st.markdown(keyword_pills(soft_skills, '#2d1b69'), unsafe_allow_html=True)


# ── JOB MATCH PAGE ────────────────────────────────────────────────────────────
elif st.session_state.page == "jobmatch":
    if not st.session_state.resume_text:
        st.warning("⚠️ Please upload a resume first.")
        if st.button("← Go to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        st.stop()

    st.markdown('<div class="section-header">🎯 Job Role Match</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#cbd5e1">Compare your resume against top tech job roles and get a personalized skill gap analysis.</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_select, col_result = st.columns([0.35, 0.65], gap="large")

    with col_select:
        st.markdown("**Select Target Role**")
        selected_role = st.selectbox(
            "Role", list(JOB_ROLES.keys()), label_visibility="collapsed",
            index=list(JOB_ROLES.keys()).index(st.session_state.selected_role)
        )

        if st.button("Analyze Match →", use_container_width=True, type="primary"):
            with st.spinner("Analyzing match..."):
                match = calculate_job_match(st.session_state.resume_text, selected_role)
                st.session_state.job_match = match
                st.session_state.selected_role = selected_role

        if selected_role in JOB_ROLES:
            role_info = JOB_ROLES[selected_role]
            st.markdown(f"""
            <div class="resume-card" style="margin-top:1rem">
              <div style="color:#cbd5e1;font-size:0.85rem;line-height:1.6">{role_info['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_result:
        if st.session_state.job_match:
            match = st.session_state.job_match
            match_score = match["match_score"]
            color = "#22c55e" if match_score >= 70 else "#eab308" if match_score >= 40 else "#ef4444"

            # Match score display
            st.markdown(f"""
            <div class="resume-card" style="border-color:{color}40">
              <div style="display:flex;align-items:center;justify-content:space-between">
                <div>
                  <div style="color:#a0b0c8;font-size:0.8rem;letter-spacing:0.05em">MATCH SCORE</div>
                  <div style="font-family:'Playfair Display',serif;font-size:3rem;font-weight:900;color:{color}">{match_score}%</div>
                </div>
                <div style="text-align:right">
                  <div style="color:#a0b0c8;font-size:0.8rem">Role</div>
                  <div style="color:#f1f5f9;font-weight:700">{match['role']}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Sub-scores
            sub1, sub2, sub3 = st.columns(3, gap="small")
            with sub1: st.metric("Required Skills", f"{match['required_match']}%")
            with sub2: st.metric("Preferred Skills", f"{match['preferred_match']}%")
            with sub3: st.metric("Bonus Skills", f"{match['bonus_match']}%")

    # Full match breakdown
    if st.session_state.job_match:
        match = st.session_state.job_match
        st.markdown("---")

        tab_m1, tab_m2, tab_m3 = st.tabs(["🔍 Skill Gaps", "📚 Learning Path", "🏆 All Roles"])

        with tab_m1:
            missing = match.get("missing_skills", {})
            if missing:
                for tier, skills in missing.items():
                    tier_color = "#ef4444" if tier == "Required" else "#eab308"
                    st.markdown(f"**{tier} Skills — Missing**")
                    st.markdown(missing_keyword_pills(skills), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.success("🎉 You have all required and preferred skills for this role!")

        with tab_m2:
            path = match.get("learning_path", [])
            if path:
                for step in path:
                    st.markdown(f'<div class="insight-item">{step}</div>', unsafe_allow_html=True)
            else:
                st.success("You're well-prepared for this role!")

            # Resource suggestions
            st.markdown("<br>")
            st.markdown("**📚 Recommended Learning Resources**")
            resources = [
                ("freeCodeCamp", "https://freecodecamp.org"),
                ("The Odin Project", "https://www.theodinproject.com"),
                ("fast.ai", "https://www.fast.ai"),
                ("Kaggle Learn", "https://kaggle.com/learn"),
                ("roadmap.sh", "https://roadmap.sh"),
            ]
            res_cols = st.columns(len(resources))
            for j, (name, url) in enumerate(resources):
                with res_cols[j]:
                    st.markdown(f'<a href="{url}" target="_blank" style="color:#818cf8;text-decoration:none;font-size:0.8rem">{name} ↗</a>', unsafe_allow_html=True)

        with tab_m3:
            st.markdown("**Compare Against All Roles**")
            with st.spinner("Computing match for all roles..."):
                all_matches = []
                for role_name in JOB_ROLES.keys():
                    m = calculate_job_match(st.session_state.resume_text, role_name)
                    all_matches.append(m)

            render_job_match_chart(all_matches)

            # Best fit roles
            all_matches_sorted = sorted(all_matches, key=lambda x: x["match_score"], reverse=True)
            st.markdown("**🏆 Your Best-Fit Roles**")
            for i, m in enumerate(all_matches_sorted[:3]):
                rank_icon = ["🥇", "🥈", "🥉"][i]
                sc = m["match_score"]
                c = "#22c55e" if sc >= 70 else "#eab308" if sc >= 40 else "#ef4444"
                st.markdown(f"""
                <div class="resume-card" style="padding:0.75rem 1rem">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>{rank_icon} <strong style="color:#e2e8f0">{m['role']}</strong></div>
                    <div style="color:{c};font-weight:700;font-size:1.1rem">{sc}%</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)


# ── SUGGESTIONS PAGE ──────────────────────────────────────────────────────────
elif st.session_state.page == "suggestions":
    if not st.session_state.ats_result:
        st.warning("⚠️ Please upload and analyze a resume first.")
        if st.button("← Go to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        st.stop()

    st.markdown('<div class="section-header">💡 Resume Improvement Suggestions</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#cbd5e1">Actionable, prioritized tips to maximize your ATS score and recruiter appeal.</p>', unsafe_allow_html=True)

    result = st.session_state.ats_result
    verb_analysis = result["verb_analysis"]

    st.markdown("<br>", unsafe_allow_html=True)

    # Priority insights (warnings first)
    warnings = [i for i in result["insights"] if "⚠️" in i]
    tips = [i for i in result["insights"] if "💡" in i]

    if warnings:
        st.markdown("### 🔴 Critical Issues")
        for w in warnings:
            st.markdown(f'<div class="insight-item" style="border-color:#ef444440;background:#ef444408">{w}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    if tips:
        st.markdown("### 🟡 Improvement Tips")
        for t in tips:
            st.markdown(f'<div class="insight-item">{t}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Structural checklist
    st.markdown("---")
    st.markdown("### ✅ Resume Completeness Checklist")
    st.markdown("<br>", unsafe_allow_html=True)

    sections = result["sections"]
    contact = result["contact"]
    checklist = [
        ("Professional Summary", "summary" in sections and len(sections.get("summary", "")) > 30),
        ("Work Experience", "experience" in sections and len(sections.get("experience", "")) > 50),
        ("Education", "education" in sections and len(sections.get("education", "")) > 30),
        ("Projects", "projects" in sections and len(sections.get("projects", "")) > 50),
        ("Technical Skills", bool(result["resume_skills"])),
        ("Email Address", bool(contact.get("email"))),
        ("Phone Number", bool(contact.get("phone"))),
        ("LinkedIn Profile", bool(contact.get("linkedin"))),
        ("GitHub Profile", bool(contact.get("github"))),
        ("Action Verbs (5+)", verb_analysis["strong_count"] >= 5),
        ("Measurable Metrics", bool(result["verb_analysis"])),
        ("Resume Length (400-1000 words)", 400 <= result["word_count"] <= 1000),
    ]

    chk_col1, chk_col2 = st.columns(2, gap="medium")
    for i, (item, passed) in enumerate(checklist):
        icon = "✅" if passed else "❌"
        bg = "#14532d20" if passed else "#7f1d1d20"
        border = "#22c55e40" if passed else "#ef444440"
        with chk_col1 if i % 2 == 0 else chk_col2:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:8px;
                        padding:0.6rem 1rem;margin:0.3rem 0;display:flex;align-items:center;gap:0.5rem">
              <span style="font-size:1rem">{icon}</span>
              <span style="color:#e2e8f0;font-size:0.88rem">{item}</span>
            </div>
            """, unsafe_allow_html=True)

    # Content improvement guide
    st.markdown("---")
    st.markdown("### 📝 Content Quality Guide")

    guide_tabs = st.tabs(["📌 Before vs After", "💪 Power Phrases", "📏 Formatting Rules"])

    with guide_tabs[0]:
        st.markdown("""
        <div class="resume-card">
          <div style="font-weight:700;color:#e2e8f0;margin-bottom:1rem">Transform Weak Bullets → Strong Bullets</div>
          <table style="width:100%;border-collapse:collapse;font-size:0.88rem">
            <tr style="border-bottom:1px solid #1e293b">
              <th style="color:#ef4444;text-align:left;padding:8px;width:50%">❌ Weak</th>
              <th style="color:#22c55e;text-align:left;padding:8px">✅ Strong</th>
            </tr>
            <tr style="border-bottom:1px solid #111827">
              <td style="color:#cbd5e1;padding:8px">Worked on a web app</td>
              <td style="color:#f1f5f9;padding:8px">Engineered a React/FastAPI web app serving 2,000+ daily active users with 99.9% uptime</td>
            </tr>
            <tr style="border-bottom:1px solid #111827">
              <td style="color:#cbd5e1;padding:8px">Helped improve performance</td>
              <td style="color:#f1f5f9;padding:8px">Optimized PostgreSQL queries, reducing API response time by 65% and cutting server costs by $800/month</td>
            </tr>
            <tr style="border-bottom:1px solid #111827">
              <td style="color:#cbd5e1;padding:8px">Made a machine learning model</td>
              <td style="color:#f1f5f9;padding:8px">Built a fraud detection classifier (XGBoost) achieving 94.2% F1-score, deployed via FastAPI on AWS Lambda</td>
            </tr>
            <tr>
              <td style="color:#cbd5e1;padding:8px">Used Python for data analysis</td>
              <td style="color:#f1f5f9;padding:8px">Automated sales pipeline analytics with Python/Pandas, saving 8 hours/week and reducing reporting errors by 90%</td>
            </tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    with guide_tabs[1]:
        power_phrases = {
            "Impact & Scale": ["Scaled to 100K+ users", "Reduced latency by 70%", "Increased revenue by $X", "Served 10K+ requests/day"],
            "Leadership": ["Led a team of 5 engineers", "Mentored 3 junior developers", "Spearheaded initiative to..."],
            "Technical Achievement": ["Architected microservices for...", "Engineered zero-downtime deployment", "Implemented CI/CD pipeline"],
            "Efficiency Gains": ["Automated manual process saving X hours/week", "Cut deployment time from X to Y", "Reduced error rate by 85%"],
        }
        pp_cols = st.columns(2, gap="medium")
        for i, (cat, phrases) in enumerate(power_phrases.items()):
            with pp_cols[i % 2]:
                st.markdown(f"**{cat}**")
                for p in phrases:
                    st.markdown(f'<div class="insight-item" style="font-size:0.82rem">"{p}"</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    with guide_tabs[2]:
        st.markdown("""
        <div class="resume-card">
          <ul style="color:#e2e8f0;font-size:0.88rem;line-height:2.2;padding-left:1.2rem">
            <li><strong style="color:#818cf8">File format:</strong> Always submit as PDF unless specifically asked otherwise</li>
            <li><strong style="color:#818cf8">Length:</strong> 1 page for 0-5 years, 2 pages for 5+ years experience</li>
            <li><strong style="color:#818cf8">Font:</strong> Clean readable font (Calibri, Garamond, Georgia) at 10-12pt</li>
            <li><strong style="color:#818cf8">Margins:</strong> 0.5–1 inch all around</li>
            <li><strong style="color:#818cf8">Section order:</strong> Summary → Experience → Projects → Skills → Education</li>
            <li><strong style="color:#818cf8">Dates:</strong> Right-aligned, consistent format (Jan 2023 – Present)</li>
            <li><strong style="color:#818cf8">Bullets:</strong> 3-5 per role, starting with strong action verbs</li>
            <li><strong style="color:#818cf8">Contact:</strong> Email, phone, LinkedIn, GitHub on the first line</li>
            <li><strong style="color:#818cf8">ATS tip:</strong> Avoid tables, columns, headers/footers, and images</li>
            <li><strong style="color:#818cf8">Keywords:</strong> Mirror language from the job description naturally</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)



# ── HOME fallback redirect ────────────────────────────────────────────────────
else:
    st.session_state.page = "home"
    st.rerun()
