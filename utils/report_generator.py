
# utils/report_generator.py
# Generates downloadable PDF ATS reports

import io
from datetime import datetime


def clean(text: str) -> str:
    """
    Strip all characters unsupported by fpdf2's built-in Helvetica font.
    Replaces common Unicode symbols with ASCII equivalents.
    """
    replacements = {
        "\u2014": "-",   # em dash  —
        "\u2013": "-",   # en dash  –
        "\u2019": "'",   # right single quote  '
        "\u2018": "'",   # left single quote  '
        "\u201c": '"',   # left double quote  "
        "\u201d": '"',   # right double quote  "
        "\u2022": "*",   # bullet  •
        "\u2026": "...", # ellipsis  …
        "\u00e9": "e",   # é
        "\u00e8": "e",   # è
        "\u00ea": "e",   # ê
        "\u00e0": "a",   # à
        "\u00e2": "a",   # â
        "\u00f9": "u",   # ù
        "\u00fb": "u",   # û
        "\u00ee": "i",   # î
        "\u00f4": "o",   # ô
        "\u00e7": "c",   # ç
        "\u00fc": "u",   # ü
        "\u00e4": "a",   # ä
        "\u00f6": "o",   # ö
        "\u00df": "ss",  # ß
        "\u2764": "<3",  # ❤
        "\u2665": "<3",  # ♥
        "\u2713": "OK",  # ✓
        "\u2717": "X",   # ✗
        "\u2192": "->",  # →
        "\u2190": "<-",  # ←
        "\u00b0": " deg",# °
        "\u00b7": "*",   # ·
        "\u00d7": "x",   # ×
        "\u00f7": "/",   # ÷
        "\u00b1": "+/-", # ±
        "\u2248": "~",   # ≈
        "\u2260": "!=",  # ≠
        "\u2264": "<=",  # ≤
        "\u2265": ">=",  # ≥
        "\u00a9": "(c)", # ©
        "\u00ae": "(R)", # ®
        "\u2122": "(TM)",# ™
        "\u20b9": "Rs.", # ₹
        "\u20ac": "EUR", # €
        "\u00a3": "GBP", # £
        "\u00a5": "JPY", # ¥
        "\u2728": "*",   # ✨
        "\u1f3c6": "",   # 🏆
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)

    # Final pass: drop any remaining non-latin-1 characters
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def generate_pdf_report(candidate_name: str, ats_result: dict, job_match: dict = None) -> bytes:
    """
    Generate a professional PDF ATS analysis report.
    Returns PDF as bytes for download.
    """
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_margins(15, 15, 15)
        pdf.add_page()

        # ── Header ────────────────────────────────────────────────────
        pdf.set_fill_color(15, 23, 42)
        pdf.rect(0, 0, 210, 40, 'F')

        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 10)
        pdf.cell(180, 10, "AI Resume ATS Analysis Report", ln=True, align="C")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(180, 180, 200)
        pdf.set_xy(15, 25)
        safe_name = clean(candidate_name)
        pdf.cell(180, 8,
                 f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}  |  Candidate: {safe_name}",
                 align="C")

        # ── ATS Score Banner ──────────────────────────────────────────
        pdf.ln(20)
        score = ats_result["total_score"]
        color = (34, 197, 94) if score >= 75 else (234, 179, 8) if score >= 50 else (239, 68, 68)

        pdf.set_fill_color(*color)
        pdf.rect(15, 48, 180, 22, 'F')
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(15, 52)
        label = "Excellent" if score >= 80 else "Good" if score >= 65 else "Average" if score >= 50 else "Needs Work"
        # Use " - " instead of " — " to avoid em-dash encoding error
        pdf.cell(180, 14, f"ATS Score: {score}/100  -  {label}", align="C")

        # ── Section Scores ────────────────────────────────────────────
        pdf.ln(32)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, "Section-Wise Score Breakdown", ln=True)
        pdf.set_draw_color(200, 200, 220)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

        section_scores = ats_result["section_scores"]
        max_scores = ats_result["max_scores"]

        for section, s_score in section_scores.items():
            max_s = max_scores.get(section.lower().replace(" ", "_"), 10)
            pct = (s_score / max_s * 100) if max_s > 0 else 0

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 80)
            pdf.cell(70, 7, clean(section), ln=False)

            # Progress bar
            bar_x = pdf.get_x()
            bar_y = pdf.get_y() + 1
            bar_w = 90
            bar_fill = bar_w * (pct / 100)

            pdf.set_fill_color(230, 230, 240)
            pdf.rect(bar_x, bar_y, bar_w, 5, 'F')

            bar_color = (34, 197, 94) if pct >= 75 else (234, 179, 8) if pct >= 50 else (239, 68, 68)
            pdf.set_fill_color(*bar_color)
            pdf.rect(bar_x, bar_y, bar_fill, 5, 'F')

            pdf.set_xy(bar_x + bar_w + 3, pdf.get_y())
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*bar_color)
            pdf.cell(20, 7, f"{s_score}/{max_s}", ln=True)

        # ── Skills Found ──────────────────────────────────────────────
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, "Detected Skills", ln=True)
        pdf.set_draw_color(200, 200, 220)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

        resume_skills = ats_result.get("resume_skills", {})
        for category, skills in resume_skills.items():
            if skills:
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(59, 130, 246)
                pdf.cell(0, 6, clean(f"{category}:"), ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(60, 60, 80)
                pdf.multi_cell(0, 6, clean(", ".join(skills)))
                pdf.ln(1)

        # ── Improvement Insights ──────────────────────────────────────
        if ats_result.get("insights"):
            pdf.ln(4)
            if pdf.get_y() > 240:
                pdf.add_page()

            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 8, "Improvement Suggestions", ln=True)
            pdf.set_draw_color(200, 200, 220)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(3)

            for insight in ats_result["insights"][:12]:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(50, 50, 80)
                # Strip emojis and special chars
                safe = insight.replace("\U0001f4a1", "[TIP]")   # 💡
                safe = safe.replace("\u26a0\ufe0f", "[WARN]")   # ⚠️
                safe = safe.replace("\u2705", "[OK]")            # ✅
                safe = clean(safe)
                pdf.multi_cell(0, 6, safe)
                pdf.ln(1)

        # ── Job Match ─────────────────────────────────────────────────
        if job_match and "match_score" in job_match:
            if pdf.get_y() > 220:
                pdf.add_page()

            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 8, clean(f"Job Role Match: {job_match['role']}"), ln=True)
            pdf.set_draw_color(200, 200, 220)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(3)

            pdf.set_font("Helvetica", "B", 12)
            match_color = (34, 197, 94) if job_match["match_score"] >= 70 else (234, 179, 8) if job_match["match_score"] >= 40 else (239, 68, 68)
            pdf.set_text_color(*match_color)
            pdf.cell(0, 8, f"Match Score: {job_match['match_score']}%", ln=True)

            if job_match.get("learning_path"):
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(15, 23, 42)
                pdf.cell(0, 7, "Recommended Learning Path:", ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(50, 50, 80)
                for step in job_match["learning_path"]:
                    safe = step.replace("\U0001f534", "[Required]")  # 🔴
                    safe = safe.replace("\U0001f7e1", "[Preferred]") # 🟡
                    safe = safe.replace("\U0001f7e2", "[Bonus]")     # 🟢
                    safe = clean(safe)
                    pdf.multi_cell(0, 6, safe)
                    pdf.ln(1)

        # ── Footer ────────────────────────────────────────────────────
        pdf.set_y(-20)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 170)
        pdf.cell(0, 5, "Generated by AI Resume Analyzer - Open Source, No API Keys Required", align="C")

        output = pdf.output()
        # fpdf2 >= 2.7 returns bytearray directly; older versions return a string
        if isinstance(output, (bytes, bytearray)):
            return bytes(output)
        return output.encode('latin-1')

    except ImportError:
        report_text = f"""
AI RESUME ATS ANALYSIS REPORT
==============================
Candidate: {candidate_name}
Generated: {datetime.now().strftime('%B %d, %Y')}

ATS SCORE: {ats_result['total_score']}/100

SECTION SCORES:
{chr(10).join(f"  {k}: {v}" for k, v in ats_result['section_scores'].items())}

INSIGHTS:
{chr(10).join(ats_result.get('insights', [])[:10])}
        """
        return report_text.encode('utf-8')