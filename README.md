# ⚡ CareerForge AI v2 — HR Intelligence Platform

> **SaaS-grade MVP**: Upload CVs → Hybrid AI + Rules Analysis → Ranked Candidates → Interview Kits

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key
cp .env.example .env
# Edit .env → add GROQ_API_KEY=your_key_here

# 3. Run
streamlit run app.py
```

---

## 🏗️ Architecture

```
careerforge_v2/
├── app.py                        # Entry point + sidebar navigation
├── requirements.txt
├── .env.example
│
├── data/
│   └── skills_db.py              # 251-skill NLP database (12 categories)
│
├── utils/
│   ├── styles.py                 # Global SaaS CSS theme
│   ├── state.py                  # Centralized session state
│   ├── ui_components.py          # Reusable UI building blocks
│   ├── pdf_reader.py             # pdfplumber + PyPDF2 fallback
│   ├── scoring_engine.py         # Rules-based hybrid scoring engine
│   └── ai_engine.py              # Groq API (contextual AI layer)
│
└── pages/
    ├── dashboard.py              # KPI cards + charts + executive summary
    ├── job_setup.py              # JD input + weight configuration
    ├── upload_analyze.py         # Bulk upload + hybrid analysis
    ├── ranking.py                # Filtered/sorted leaderboard
    ├── profile.py                # Deep candidate profile
    ├── comparison.py             # Side-by-side comparison table
    └── interview_kit.py          # AI interview question generator
```

---

## ⚙️ Hybrid Scoring Engine

Unlike pure AI systems, CareerForge uses a **Rules + AI hybrid**:

| Layer | What it does | Speed |
|---|---|---|
| **Rules Engine** | Skills NLP, experience extraction, ATS scoring, risk flags | ~0.1s |
| **AI Layer** | Contextual summary, culture fit, nuanced recommendation | ~5-8s |
| **Decision Engine** | Combines both for final hire/reject decision | instant |

### Score Components (configurable weights)
- **Skills Match** (default 40%) — NLP matching against 251-skill database
- **Experience** (default 30%) — Years detected vs required
- **Education** (default 15%) — Degree level scoring
- **ATS Keywords** (default 15%) — Keyword density overlap

---

## 📋 Workflow

```
Job Setup → Upload CVs → Auto Analysis → Ranking → Profile → Compare → Interview Kit
```

1. **Job Setup** — Paste JD, configure weights, load preset (Technical/Management/Entry)
2. **Upload & Analyze** — Drop 1–100 PDFs, choose AI or rules-only mode
3. **Candidate Ranking** — Filter by decision, sort by any score dimension
4. **Candidate Profile** — Full scorecard, skills gap, AI report
5. **Comparison** — Side-by-side table for up to 4 candidates
6. **Interview Kit** — Opening/Technical/Behavioral/Situational/Red-flag questions

---

## 🔑 Getting a Groq API Key

1. Go to [console.groq.com](https://console.groq.com) (free tier available)
2. Create an API key
3. Add to `.env` as `GROQ_API_KEY=gsk_...`

---

## 🎯 Target Clients

- **HR Departments** — Automate CV screening at scale
- **Recruitment Agencies** — Process high volumes efficiently
- **Career Centers** — Match applicants to roles objectively
- **Hiring Managers** — Get structured, bias-reduced comparisons

---

## 💡 v2 Improvements Over v1

| Feature | v1 | v2 |
|---|---|---|
| Scoring | AI only | Hybrid Rules + AI |
| Skills | AI prompt | 251-skill NLP database |
| Risk Detection | None | 5 automated rule-based checks |
| Candidate Comparison | None | Side-by-side table (up to 4) |
| Weights | Fixed | Configurable per job type |
| PDF Extraction | PyPDF2 only | pdfplumber + PyPDF2 fallback |
| Session State | Ad-hoc | Centralized manager |
| UI | Basic Streamlit | Custom SaaS CSS theme |
| Decision Engine | AI only | Rules guardrails + AI nuance |
