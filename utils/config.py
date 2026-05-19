"""utils/config.py — Robust API key loader for Windows."""
import os


def get_groq_key() -> str:
    # 1. Already loaded in environment
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key

    # 2. Read .env manually with multiple encodings
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")

    if not os.path.exists(env_path):
        return ""

    for encoding in ["utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"]:
        try:
            with open(env_path, "r", encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key_name, _, val = line.partition("=")
                        if key_name.strip() == "GROQ_API_KEY":
                            val = val.strip().strip('"').strip("'")
                            if val:
                                os.environ["GROQ_API_KEY"] = val
                                return val
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue

    return ""
