"""
data/skills_db.py
Comprehensive skills database for NLP-based skill extraction.
Organized by category for weighted matching.
"""

SKILLS_DB = {
    "programming_languages": {
        "weight": 1.0,
        "skills": [
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
            "swift", "kotlin", "ruby", "php", "scala", "r", "matlab", "perl",
            "bash", "shell", "powershell", "dart", "lua", "haskell", "elixir",
            "clojure", "f#", "cobol", "fortran", "assembly", "vba", "groovy"
        ]
    },
    "web_frontend": {
        "weight": 0.9,
        "skills": [
            "react", "vue", "angular", "svelte", "next.js", "nuxt", "gatsby",
            "html", "css", "sass", "tailwind", "bootstrap", "material ui",
            "webpack", "vite", "redux", "graphql", "apollo", "jquery",
            "web components", "pwa", "responsive design", "ui/ux"
        ]
    },
    "web_backend": {
        "weight": 0.9,
        "skills": [
            "node.js", "express", "fastapi", "django", "flask", "spring boot",
            "rails", "laravel", "asp.net", "nest.js", "gin", "fiber",
            "rest api", "soap", "microservices", "websockets", "grpc",
            "oauth", "jwt", "api design", "swagger"
        ]
    },
    "data_science_ml": {
        "weight": 1.0,
        "skills": [
            "machine learning", "deep learning", "nlp", "computer vision",
            "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost",
            "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
            "hugging face", "transformers", "bert", "gpt", "llm",
            "reinforcement learning", "neural networks", "cnn", "rnn", "lstm",
            "data analysis", "statistical modeling", "a/b testing", "feature engineering",
            "model deployment", "mlops", "data pipeline", "etl"
        ]
    },
    "databases": {
        "weight": 0.85,
        "skills": [
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "cassandra", "dynamodb", "sqlite", "oracle", "sql server",
            "firebase", "supabase", "neo4j", "influxdb", "clickhouse",
            "sql", "nosql", "database design", "query optimization", "indexing",
            "data modeling", "orm", "prisma", "sqlalchemy"
        ]
    },
    "cloud_devops": {
        "weight": 0.9,
        "skills": [
            "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
            "ansible", "jenkins", "github actions", "gitlab ci", "circleci",
            "helm", "prometheus", "grafana", "datadog", "new relic",
            "linux", "nginx", "apache", "cloudflare", "cdn",
            "ci/cd", "devops", "sre", "infrastructure as code", "serverless",
            "lambda", "cloud functions", "ec2", "s3", "rds"
        ]
    },
    "data_engineering": {
        "weight": 0.9,
        "skills": [
            "apache spark", "hadoop", "kafka", "airflow", "dbt",
            "snowflake", "bigquery", "redshift", "databricks",
            "data warehouse", "data lake", "streaming", "batch processing",
            "etl", "data pipeline", "apache beam", "flink", "nifi"
        ]
    },
    "mobile": {
        "weight": 0.85,
        "skills": [
            "ios", "android", "react native", "flutter", "swift",
            "kotlin", "xamarin", "ionic", "cordova", "expo",
            "mobile development", "app store", "google play"
        ]
    },
    "security": {
        "weight": 0.85,
        "skills": [
            "cybersecurity", "penetration testing", "ethical hacking",
            "owasp", "ssl/tls", "encryption", "authentication",
            "vulnerability assessment", "soc", "siem", "firewalls",
            "network security", "application security", "devsecops"
        ]
    },
    "soft_skills": {
        "weight": 0.6,
        "skills": [
            "leadership", "communication", "teamwork", "problem solving",
            "project management", "agile", "scrum", "kanban", "jira",
            "time management", "critical thinking", "mentoring",
            "stakeholder management", "presentation", "negotiation"
        ]
    },
    "business_tools": {
        "weight": 0.7,
        "skills": [
            "excel", "power bi", "tableau", "looker", "metabase",
            "salesforce", "hubspot", "sap", "jira", "confluence",
            "figma", "sketch", "adobe", "notion", "slack"
        ]
    },
    "certifications": {
        "weight": 0.8,
        "skills": [
            "aws certified", "google cloud certified", "azure certified",
            "pmp", "prince2", "cissp", "ceh", "comptia", "cisco",
            "tensorflow certified", "databricks certified",
            "scrum master", "product owner", "safe"
        ]
    }
}

# Flatten for quick lookup
ALL_SKILLS = set()
SKILL_TO_CATEGORY = {}
SKILL_WEIGHTS = {}

for category, data in SKILLS_DB.items():
    for skill in data["skills"]:
        ALL_SKILLS.add(skill.lower())
        SKILL_TO_CATEGORY[skill.lower()] = category
        SKILL_WEIGHTS[skill.lower()] = data["weight"]


def extract_skills(text: str) -> list[dict]:
    """
    NLP-based skill extraction from CV text.
    Returns list of {skill, category, weight} dicts.
    """
    text_lower = text.lower()
    found = []
    seen = set()

    for skill in ALL_SKILLS:
        if skill in seen:
            continue
        # Multi-word skills: exact match
        if " " in skill:
            if skill in text_lower:
                found.append({
                    "skill": skill,
                    "category": SKILL_TO_CATEGORY[skill],
                    "weight": SKILL_WEIGHTS[skill]
                })
                seen.add(skill)
        else:
            # Single-word: word boundary check
            import re
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.append({
                    "skill": skill,
                    "category": SKILL_TO_CATEGORY[skill],
                    "weight": SKILL_WEIGHTS[skill]
                })
                seen.add(skill)

    return sorted(found, key=lambda x: x["weight"], reverse=True)


def match_skills(cv_skills: list[dict], jd_skills: list[dict]) -> dict:
    """Compare CV skills against JD skills."""
    cv_set  = {s["skill"] for s in cv_skills}
    jd_set  = {s["skill"] for s in jd_skills}

    matched = cv_set & jd_set
    missing = jd_set - cv_set
    extra   = cv_set - jd_set

    # Weighted match score
    total_weight   = sum(SKILL_WEIGHTS.get(s, 0.5) for s in jd_set) or 1
    matched_weight = sum(SKILL_WEIGHTS.get(s, 0.5) for s in matched)
    score = min(100, int((matched_weight / total_weight) * 100))

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra":   sorted(extra),
        "score":   score,
        "coverage": f"{len(matched)}/{len(jd_set)}"
    }
