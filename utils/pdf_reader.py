"""utils/pdf_reader.py — Best-effort PDF text extraction."""
import io

def extract_text(file_bytes: bytes) -> str:
    """Try pdfplumber first, fall back to PyPDF2."""
    text = ""

    # Attempt 1: pdfplumber (better accuracy)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages).strip()
        if len(text) > 50:
            return text
    except Exception:
        pass

    # Attempt 2: PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n".join(pages).strip()
        if len(text) > 50:
            return text
    except Exception:
        pass

    return "[⚠️ Could not extract text — PDF may be scanned/image-based. Please use a text-based PDF.]"
