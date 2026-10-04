import os


def extract_pdf(file_path: str) -> dict:
    base = {
        "file_name":        os.path.basename(file_path),
        "file_path":        file_path,
        "file_type":        "pdf",
        "number_of_pages":  0,
        "raw_text":         "",
        "extraction_method": "",
        "error":            "",
    }

    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages = pdf.pages
            base["number_of_pages"] = len(pages)
            text = "\n".join(p.extract_text() or "" for p in pages)
            if text.strip():
                base["raw_text"] = text
                base["extraction_method"] = "pdfplumber"
                return base
    except Exception as e:
        base["error"] = str(e)

    try:
        import fitz
        doc = fitz.open(file_path)
        base["number_of_pages"] = len(doc)
        text = "\n".join(page.get_text() for page in doc)
        base["raw_text"] = text
        base["extraction_method"] = "pymupdf"
        base["error"] = ""
    except Exception as e:
        base["error"] = str(e)

    return base


def extract_section(file_path: str, keyword: str) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            full = "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        try:
            import fitz
            doc = fitz.open(file_path)
            full = "\n".join(page.get_text() for page in doc)
        except Exception:
            return ""

    lower = full.lower()
    idx   = lower.find(keyword.lower())
    if idx == -1:
        return ""
    return full[idx: idx + 3000]


def batch_extract(directory: str) -> list:
    results = []
    for fname in os.listdir(directory):
        if fname.lower().endswith(".pdf"):
            results.append(extract_pdf(os.path.join(directory, fname)))
    return results
