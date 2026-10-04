import re
import unicodedata
from config import DOMAIN_KEYWORDS
from etl.metrics import compute_all_metrics


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\b\d+\b(?=\s*\n)', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def classify_domain(text: str) -> str:
    lower = text.lower()
    scores = {
        domain: sum(lower.count(kw) for kw in keywords)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def transform_record(record: dict) -> dict:
    raw   = record.get("raw_text", "") or ""
    clean = clean_text(raw)
    m     = compute_all_metrics(clean, record.get("number_of_pages", 0))
    return {
        "file_name":              record.get("file_name", "unknown"),
        "file_path":              record.get("file_path", ""),
        "file_type":              record.get("file_type", "pdf"),
        "has_text":               bool(clean.strip()),
        "domain":                 classify_domain(clean),
        "clean_text":             clean,
        "number_of_pages":        m["number_of_pages"],
        "word_count":             m["word_count"],
        "sentence_count":         m["sentence_count"],
        "avg_words_per_sentence": m["avg_words_per_sentence"],
        "reading_level_score":    m["reading_level_score"],
        "reading_ease_score":     m["reading_ease_score"],
        "extraction_method":      record.get("extraction_method", ""),
        "extraction_error":       record.get("error", ""),
    }
