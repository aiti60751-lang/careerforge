"""
utils/ai_engine.py
AI calls via Groq API — structured outputs with validation.
"""
import os, json, re, streamlit as st
from openai import OpenAI

MODEL = "llama-3.3-70b-versatile"


@st.cache_resource
def get_client():
    from utils.config import get_groq_key
    key = get_groq_key()
    if not key:
        raise ValueError("GROQ_API_KEY not found. Add it to your .env file and restart.")
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")


def _parse_json(text: str):
    """Strip markdown fences and parse JSON safely."""
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    # Find first { or [
    start = next((i for i, c in enumerate(clean) if c in "{["), 0)
    return json.loads(clean[start:])


def _chat(system: str, user: str, temperature: float = 0.2, max_tokens: int = 2000) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


# ── CV contextual analysis ────────────────────────────────────────────────────
def ai_analyze_cv(cv_text: str, jd_text: str, rules_scores: dict) -> dict:
    """
    AI provides contextual insights ON TOP of rules-based scores.
    Rules scores are passed as context so AI enhances, not replaces.
    """
    system = """You are a senior talent acquisition expert. Analyze CVs objectively.
Return ONLY valid JSON with no markdown outside the JSON block.
Be concise and specific — no generic statements."""

    user = f"""
Analyze this CV against the job description. The rules-based system already scored:
- Overall: {rules_scores['overall_score']}/100
- Skills match: {rules_scores['skills_score']}/100
- Experience: {rules_scores['experience_score']}/100
- Matched skills: {rules_scores['matched_skills'][:10]}
- Missing skills: {rules_scores['missing_skills'][:10]}
- Risk flags: {rules_scores['risk_flags']}

Your job: provide contextual insights the rules engine can't detect.

Return EXACTLY this JSON:
{{
  "name": "<candidate full name>",
  "current_title": "<their most recent job title>",
  "summary": "<2-sentence professional summary specific to THIS role>",
  "strengths": ["<specific strength 1>", "<specific strength 2>", "<specific strength 3>"],
  "concerns": ["<specific concern 1>", "<specific concern 2>"],
  "recommendation": "Strong Hire|Hire|Maybe|Not Recommended",
  "recommendation_reason": "<one specific sentence explaining why>",
  "culture_fit_indicators": ["<indicator 1>", "<indicator 2>"],
  "interview_focus_areas": ["<area to probe 1>", "<area to probe 2>", "<area to probe 3>"]
}}

JOB DESCRIPTION:
{jd_text[:2000]}

CV TEXT:
{cv_text[:3500]}
"""
    try:
        raw = _chat(system, user)
        result = _parse_json(raw)
        # Validate required fields
        required = ["name", "summary", "strengths", "recommendation"]
        for f in required:
            if f not in result:
                result[f] = "N/A" if f != "strengths" else []
        return result
    except Exception as e:
        return {
            "name": "Unknown",
            "current_title": "Unknown",
            "summary": f"AI analysis failed: {e}",
            "strengths": [],
            "concerns": [],
            "recommendation": "Maybe",
            "recommendation_reason": "Could not complete AI analysis",
            "culture_fit_indicators": [],
            "interview_focus_areas": []
        }


# ── Interview questions ───────────────────────────────────────────────────────
def generate_interview_kit(cv_text: str, jd_text: str, analysis: dict) -> dict:
    system = "Expert technical interviewer. Return ONLY valid JSON."
    user = f"""
Create a targeted interview kit. Return this JSON:
{{
  "opening_questions": [
    {{"q": "...", "purpose": "..."}}
  ],
  "technical": [
    {{"q": "...", "ideal": "...", "difficulty": "Easy|Medium|Hard", "skill_tested": "..."}}
  ],
  "behavioral": [
    {{"q": "...", "look_for": "...", "competency": "..."}}
  ],
  "situational": [
    {{"q": "...", "ideal": "..."}}
  ],
  "red_flag_probes": [
    {{"concern": "...", "q": "..."}}
  ],
  "closing": "Recommended closing question for this specific candidate"
}}

Generate: 2 opening, 5 technical, 4 behavioral, 3 situational, questions for each risk flag.

Candidate: {analysis.get('name','?')}
Title: {analysis.get('current_title','?')}
Missing skills: {analysis.get('missing_skills', [])[:5]}
Concerns: {analysis.get('concerns', [])}
Focus areas: {analysis.get('interview_focus_areas', [])}

JOB: {jd_text[:1500]}
CV: {cv_text[:2000]}
"""
    try:
        raw = _chat(system, user, max_tokens=3000)
        return _parse_json(raw)
    except Exception as e:
        return {"error": str(e)}


# ── Candidate summary for report ─────────────────────────────────────────────
def generate_candidate_report(cv_text: str, jd_text: str, full_analysis: dict) -> str:
    """Generate a professional hiring manager report."""
    system = "Senior HR consultant writing formal candidate evaluation reports."
    user = f"""
Write a professional 300-word candidate evaluation report for a hiring manager.
Structure: Background | Key Strengths | Concerns | Recommendation | Next Steps

Candidate: {full_analysis.get('name','?')}
Score: {full_analysis.get('overall_score','?')}/100
Decision: {full_analysis.get('decision','?')}
Matched skills: {full_analysis.get('matched_skills',[])}
Missing skills: {full_analysis.get('missing_skills',[])}
Risk flags: {full_analysis.get('risk_flags',[])}

JOB: {jd_text[:1000]}
"""
    return _chat(system, user, temperature=0.4, max_tokens=600)


# ── Pool executive summary ────────────────────────────────────────────────────
def pool_executive_summary(ranked_candidates: list[dict], jd_text: str) -> str:
    system = "HR Director summarizing a talent pool for an executive committee."
    names = [
        f"{c.get('name','?')} ({c.get('overall_score','?')}/100, {c.get('decision','?')})"
        for c in ranked_candidates[:8]
    ]
    user = f"""
Write a 150-word executive summary of this candidate pool.
Cover: pool quality, top picks, notable gaps, hiring recommendation.

Candidates (ranked): {'; '.join(names)}
Role: {jd_text[:400]}
"""
    return _chat(system, user, temperature=0.5, max_tokens=300)
