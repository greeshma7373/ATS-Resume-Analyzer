# 🎯 ResumeIQ — AI Resume Analyzer & ATS Score Checker

> **100% free · No API keys · No cloud AI · Runs fully offline after installation**

A production-ready resume analyzer that calculates your ATS score, extracts skills, detects keyword gaps, and generates improvement suggestions — all using open-source Python libraries.

---

## ✨ Features

| Feature | Description |
|---|---|
| **ATS Score** | 9-dimensional weighted scoring (0–100) |
| **Skill Extraction** | 200+ skills across 7 categories |
| **Job Role Match** | 8 roles with required/preferred/bonus tiers |
| **Keyword Gap Detection** | Compare resume vs job description using TF-IDF |
| **Smart Suggestions** | Section-specific, actionable improvement tips |
| **PDF Report** | Downloadable branded ATS analysis report |
| **Visualizations** | Gauge, radar, treemap, bar charts (Plotly) |

## 🏗️ Project Structure

```
resume-analyzer/
│
├── app.py                    ← Main Streamlit application (entry point)
├── requirements.txt          ← All Python dependencies
├── README.md
│
├── parsers/
│   └── resume_parser.py      ← PDF text extraction (pdfplumber + PyPDF2)
│
├── analyzers/
│   ├── ats_scorer.py         ← ATS scoring engine (TF-IDF + rules)
│   └── skill_extractor.py    ← NLP-based skill extraction
│
├── components/
│   └── ui_components.py      ← Plotly charts and HTML UI elements
│
├── utils/
│   └── report_generator.py   ← PDF report generation (fpdf2)
│
└── data/
    └── skills_data.py        ← Skill dictionaries + job role definitions
```

## 🚀 Quick Start (Local)

### 1. Prerequisites
- Python 3.9+ installed
- pip package manager

### 2. Installation

```bash
# Clone or download the project
git clone <your-repo-url>
cd resume-analyzer

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model (one-time)
python -m spacy download en_core_web_sm
```

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🌐 Deployment

### Streamlit Community Cloud (Free)

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **New app** → select your repo
5. Set **Main file path**: `app.py`
6. Click **Deploy**

The spaCy model auto-downloads on first run. No environment variables needed.

### Render (Free Tier)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Deploy

---

## 📊 ATS Scoring Algorithm

The scoring engine evaluates 9 weighted dimensions:

| Dimension | Weight | What it checks |
|---|---|---|
| Skills | 20 | Tech skill count and category diversity |
| Experience | 20 | Section presence, dates, bullets, quantified metrics |
| Education | 12 | Degree type, institution, graduation year |
| Projects | 12 | GitHub/live links, tech stack, impact numbers |
| Contact Info | 8 | Email, phone, LinkedIn, GitHub |
| Summary | 8 | Professional summary length and quality |
| Action Verbs | 8 | Strong vs weak verb ratio |
| Readability | 6 | Word count (400-1000 ideal) |
| ATS Keywords | 6 | Industry keyword density |

**Job Description Boost**: If you provide a JD, TF-IDF cosine similarity adds up to 15 bonus points.

---

## 🔧 Tech Stack

- **Python 3.9+** — Core language
- **Streamlit** — Web UI framework
- **spaCy** — NLP (en_core_web_sm)
- **scikit-learn** — TF-IDF & cosine similarity
- **pdfplumber** — PDF text extraction (primary)
- **PyPDF2** — PDF extraction (fallback)
- **NLTK** — Text preprocessing
- **Plotly** — Interactive charts
- **fpdf2** — PDF report generation
- **pandas / numpy** — Data manipulation

## 🛠️ Troubleshooting

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**PDF text extraction empty:**
- Ensure your PDF is text-based (not a scanned image)
- Try re-saving from Word as PDF
- Use [pdf2docx](https://github.com/dothinking/pdf2docx) to convert scanned PDFs

**Port conflict:**
```bash
streamlit run app.py --server.port 8502
```

**Memory issues on large PDFs:**
- Limit resume to 2 pages
- Compress PDF before uploading

---

## 📈 Future Roadmap

- [ ] OCR support for scanned/image PDFs
- [ ] Multi-resume ranking & comparison
- [ ] LinkedIn profile scraper
- [ ] Local LLM integration (Ollama/LLaMA) for richer suggestions
- [ ] Chrome extension for auto job matching
- [ ] Resume template generator
- [ ] Interview question generator from skill gaps
- [ ] Multi-language support

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

Built with open-source libraries. No external APIs. No tracking. Your resume data stays on your machine.

**Ideal for:** College major projects · Developer portfolios · Hackathons · Placement prep
