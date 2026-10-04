import re
import textstat


def word_count(text: str) -> int:
    if not text:
        return 0
    return len(text.split())


def sentence_count(text: str) -> int:
    if not text:
        return 0
    return len([s for s in re.split(r'[.!?]+', text) if s.strip()])


def avg_words_per_sentence(text: str) -> float:
    sc = sentence_count(text)
    return 0.0 if sc == 0 else round(word_count(text) / sc, 2)


def flesch_kincaid_grade(text: str) -> float:
    if not text or len(text.strip()) < 10:
        return 0.0
    try:
        return round(textstat.flesch_kincaid_grade(text), 2)
    except Exception:
        return 0.0


def flesch_reading_ease(text: str) -> float:
    if not text or len(text.strip()) < 10:
        return 0.0
    try:
        return round(textstat.flesch_reading_ease(text), 2)
    except Exception:
        return 0.0


def compute_all_metrics(text: str, pages: int = 0) -> dict:
    return {
        "word_count":             word_count(text),
        "sentence_count":         sentence_count(text),
        "avg_words_per_sentence": avg_words_per_sentence(text),
        "number_of_pages":        pages,
        "reading_level_score":    flesch_kincaid_grade(text),
        "reading_ease_score":     flesch_reading_ease(text),
    }
