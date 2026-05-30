# parsers/resume_parser.py
# Handles PDF text extraction with multiple fallback strategies

import re
import io
from pathlib import Path


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from uploaded PDF using pdfplumber (primary) and PyPDF2 (fallback).
    Returns cleaned text string.
    """
    text = ""

    # Try pdfplumber first (better layout preservation)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
        uploaded_file.seek(0)  # reset pointer
    except Exception:
        pass

    # Fallback to PyPDF2 if pdfplumber fails or returns empty
    if not text.strip():
        try:
            import PyPDF2
            uploaded_file.seek(0)
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
            uploaded_file.seek(0)
        except Exception as e:
            return f"ERROR: Could not extract text from PDF. {str(e)}"

    return clean_text(text)


def clean_text(text: str) -> str:
    """Clean and normalize extracted resume text."""
    if not text:
        return ""

    # Fix common PDF extraction artifacts
    text = re.sub(r'\s+', ' ', text)          # Collapse multiple spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)   # Normalize blank lines
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) # Remove non-ASCII noise
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Split camelCase words

    # Preserve email and phone patterns
    text = text.strip()
    return text


def extract_contact_info(text: str) -> dict:
    """Extract contact details using regex patterns."""
    contact = {}

    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    contact["email"] = emails[0] if emails else None

    # Phone
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        raw = phones[0] if isinstance(phones[0], str) else ''.join(phones[0])
        contact["phone"] = re.sub(r'\s+', '', raw)
    else:
        contact["phone"] = None

    # LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    contact["linkedin"] = linkedin[0] if linkedin else None

    # GitHub
    github_pattern = r'github\.com/[\w\-]+'
    github = re.findall(github_pattern, text, re.IGNORECASE)
    contact["github"] = github[0] if github else None

    # Portfolio / website
    web_pattern = r'(?:https?://)?(?:www\.)?[\w\-]+\.(?:com|io|dev|me|co|net|org)/[\w\-/.?=&]*'
    websites = re.findall(web_pattern, text, re.IGNORECASE)
    # Filter out known platforms already captured
    websites = [w for w in websites if 'linkedin' not in w.lower() and 'github' not in w.lower()]
    contact["website"] = websites[0] if websites else None

    return contact


def extract_name(text: str) -> str:
    """
    Attempt to extract candidate name from top of resume.
    Uses heuristic: first non-empty line that looks like a name.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:5]:
        # Name-like: 2-4 words, mostly alphabetic, no special chars except hyphen/apostrophe
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(re.match(r"^[A-Za-z'\-]+$", w) for w in words):
                return line
    return "Candidate"


def split_into_sections(text: str) -> dict:
    """
    Split resume text into logical sections using keyword detection.
    Returns dict of {section_name: section_text}
    """
    from data.skills_data import SECTION_KEYWORDS

    sections = {}
    text_lower = text.lower()
    lines = text.split('\n')

    # Find section boundaries by looking for header-like lines
    section_positions = {}
    for section_name, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            # Look for keyword as a standalone line or at line start
            pattern = rf'^[\s]*{re.escape(kw)}[\s:]*$'
            for i, line in enumerate(lines):
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    if section_name not in section_positions:
                        section_positions[section_name] = i
                    break

    if not section_positions:
        # Fallback: return full text as 'body'
        sections["body"] = text
        return sections

    # Sort by position
    sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])

    for idx, (section_name, start_line) in enumerate(sorted_sections):
        end_line = sorted_sections[idx + 1][1] if idx + 1 < len(sorted_sections) else len(lines)
        section_content = '\n'.join(lines[start_line:end_line])
        sections[section_name] = section_content

    return sections


def count_pages(uploaded_file) -> int:
    """Count number of pages in PDF."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            count = len(pdf.pages)
        uploaded_file.seek(0)
        return count
    except Exception:
        try:
            import PyPDF2
            uploaded_file.seek(0)
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            count = len(reader.pages)
            uploaded_file.seek(0)
            return count
        except Exception:
            return 1
