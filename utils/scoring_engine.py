"""
utils/scoring_engine.py
Hybrid scoring: Rules-based (fast, deterministic) + AI (contextual).
This makes results reliable and explainable.
"""
import re
from data.skills_db import extract_skills, match_skills

# ── Experience extraction ─────────────────────────────────────────────────────
EXP_PATTERNS = [
    r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',
    r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
    r'experience\s+of\s+(\d+)\+?\s*years?',
    r'(\d{4})\s*[-–]\s*(?:present|current|now)',  # date range
]

EDU_LEVELS = {
    "phd": 100, "doctorate": 100, "ph.d": 100,
    "master": 85, "msc": 85, "m.sc": 85, "mba": 85, "m.eng": 85,
    "bachelor": 70, "bsc": 70, "b.sc": 70, "b.eng": 70, "b.tech": 70,
    "associate": 50, "diploma": 45, "certificate": 40,
    "high school": 20, "secondary": 20
}

SENIORITY_KEYWORDS = {
    "junior": 1, "entry": 1, "intern": 0, "trainee": 0,
    "mid": 2, "intermediate": 2,
    "senior": 3, "lead": 3, "principal": 4,
    "staff": 3, "architect": 4, "manager": 3,
    "director": 5, "vp": 5, "head": 4, "chief": 5, "cto": 5, "ceo": 5
}

JOB_GAP_PATTERN = r'(\d{4})\s*[-–]\s*(\d{4})'

RISK_PATTERNS = {
    "frequent_job_hopping": lambda exp_list: _check_job_hopping(exp_list),
    "employment_gaps":      lambda text: _check_gaps(text),
    "no_quantified_results": lambda text: not bool(re.search(r'\d+%|\$\d+|increased|reduced|improved|grew', text, re.I)),
    "short_cv":             lambda text: len(text.split()) < 200,
}


def _check_job_hopping(text: str) -> bool:
    """Flag if more than 3 jobs each under 18 months."""
    ranges = re.findall(r'(\d{4})\s*[-–]\s*(\d{4})', text)
    short = sum(1 for s, e in ranges if abs(int(e) - int(s)) <= 1)
    return short >= 3


def _check_gaps(text: str) -> bool:
    years = sorted(set(int(y) for y in re.findall(r'\b(20\d{2}|19\d{2})\b', text)))
    if len(years) < 2:
        return False
    for i in range(1, len(years)):
        if years[i] - years[i-1] > 2:
            return True
    return False


def extract_experience_years(text: str) -> float:
    """Extract years of experience from CV text."""
    for pattern in EXP_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = int(match.group(1))
                if val > 1900:  # It's a year, not duration
                    current_year = 2024
                    return min(current_year - val, 30)
                return min(val, 40)
            except (ValueError, IndexError):
                continue

    # Fallback: count date ranges
    ranges = re.findall(r'(\d{4})\s*[-–]\s*(?:(\d{4})|present|current)', text, re.IGNORECASE)
    if ranges:
        total = 0
        for start, end in ranges:
            try:
                s = int(start)
                e = int(end) if end else 2024
                total += max(0, e - s)
            except ValueError:
                pass
        return min(total, 30)
    return 0


def extract_education_level(text: str) -> tuple[str, int]:
    """Returns (level_name, score_0_100)."""
    text_lower = text.lower()
    best_score = 0
    best_level = "Not Specified"
    for keyword, score in EDU_LEVELS.items():
        if keyword in text_lower and score > best_score:
            best_score = score
            best_level = keyword.title()
    return best_level, best_score


def extract_seniority(text: str) -> tuple[str, int]:
    """Returns (seniority_label, level_0_5)."""
    text_lower = text.lower()
    best_level = 0
    best_label = "Not Specified"
    for keyword, level in SENIORITY_KEYWORDS.items():
        if keyword in text_lower and level > best_level:
            best_level = level
            best_label = keyword.title()
    return best_label, best_level


def detect_risk_flags(text: str) -> list[str]:
    """Rule-based risk flag detection."""
    flags = []
    if _check_job_hopping(text):
        flags.append("Frequent job changes (possible retention risk)")
    if _check_gaps(text):
        flags.append("Employment gaps detected")
    if not re.search(r'\d+%|\$\d+|increased|reduced|improved|grew|saved|delivered', text, re.I):
        flags.append("No quantified achievements (hard to measure impact)")
    if len(text.split()) < 200:
        flags.append("Very short CV (may lack detail)")
    if not re.search(r'github|linkedin|portfolio|project', text, re.I):
        flags.append("No portfolio or online presence mentioned")
    return flags


# ── Weighted scoring ──────────────────────────────────────────────────────────
DEFAULT_WEIGHTS = {
    "skills":     40,
    "experience": 30,
    "education":  15,
    "ats":        15,
}


def compute_rules_score(
    cv_text: str,
    jd_text: str,
    weights: dict = None
) -> dict:
    """
    Pure rules-based scoring. Fast and deterministic.
    Returns a full scoring breakdown.
    """
    w = weights or DEFAULT_WEIGHTS

    # 1. Skills
    cv_skills  = extract_skills(cv_text)
    jd_skills  = extract_skills(jd_text)
    skill_data = match_skills(cv_skills, jd_skills)
    skills_score = skill_data["score"]

    # 2. Experience
    exp_years = extract_experience_years(cv_text)
    # Try to find required experience from JD
    jd_exp_match = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', jd_text, re.I)
    required_exp  = int(jd_exp_match.group(1)) if jd_exp_match else 3
    exp_score = min(100, int((exp_years / max(required_exp, 1)) * 100))
    exp_score = max(0, min(100, exp_score))

    # 3. Education
    edu_level, edu_score = extract_education_level(cv_text)

    # 4. ATS (keyword density in JD vs CV)
    jd_words  = set(re.findall(r'\b\w{4,}\b', jd_text.lower()))
    cv_words  = set(re.findall(r'\b\w{4,}\b', cv_text.lower()))
    stopwords = {"with","that","this","from","have","will","your","they","their","been","were","what"}
    jd_kw     = jd_words - stopwords
    matched_kw = jd_kw & cv_words
    ats_score  = min(100, int((len(matched_kw) / max(len(jd_kw), 1)) * 100))

    # 5. Weighted overall
    overall = (
        skills_score * w["skills"]    / 100 +
        exp_score    * w["experience"] / 100 +
        edu_score    * w["education"]  / 100 +
        ats_score    * w["ats"]        / 100
    )

    # 6. Seniority + risk flags
    seniority_label, seniority_level = extract_seniority(cv_text)
    risk_flags = detect_risk_flags(cv_text)

    return {
        "overall_score":    round(overall),
        "skills_score":     skills_score,
        "experience_score": exp_score,
        "education_score":  edu_score,
        "ats_score":        ats_score,
        "experience_years": round(exp_years, 1),
        "education_level":  edu_level,
        "seniority":        seniority_label,
        "seniority_level":  seniority_level,
        "matched_skills":   skill_data["matched"],
        "missing_skills":   skill_data["missing"],
        "extra_skills":     skill_data["extra"],
        "skill_coverage":   skill_data["coverage"],
        "risk_flags":       risk_flags,
        "cv_skills":        [s["skill"] for s in cv_skills],
        "jd_skills":        [s["skill"] for s in jd_skills],
    }


def make_hiring_decision(scores: dict, ai_analysis: dict = None) -> dict:
    """
    Combine rules + AI to make final hiring decision.
    Rules act as guardrails; AI provides nuance.
    """
    overall = scores["overall_score"]
    risk_count = len(scores.get("risk_flags", []))

    # Base decision from score
    if overall >= 75 and risk_count == 0:
        decision = "Strong Hire"
        confidence = "High"
    elif overall >= 75 and risk_count <= 1:
        decision = "Hire"
        confidence = "High"
    elif overall >= 60 and risk_count <= 2:
        decision = "Maybe"
        confidence = "Medium"
    elif overall >= 45:
        decision = "Weak Maybe"
        confidence = "Low"
    else:
        decision = "Not Recommended"
        confidence = "High"

    # AI override (if provided)
    if ai_analysis:
        ai_rec = ai_analysis.get("recommendation", "")
        if ai_rec == "Strong Hire" and overall >= 65:
            decision = "Strong Hire"
        elif ai_rec == "Reject" and overall < 60:
            decision = "Not Recommended"

    return {
        "decision":   decision,
        "confidence": confidence,
        "score":      overall,
    }
