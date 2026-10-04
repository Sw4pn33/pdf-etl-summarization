from summarization.cohere_client import generate_text, summarize_text

DOMAIN_CONTEXT = {
    "legal": {
        "doc_type":   "legal document (contract, agreement, or legal filing)",
        "focus":      "parties involved, key obligations, liability clauses, important legal terms, and effective dates",
        "one_sent":   "the legal agreement type and its primary obligation or outcome",
        "exec_style": "formal legal language. Mention parties, purpose, key terms, and any critical clauses",
        "bullet_kw":  "legal obligations, rights, penalties, deadlines, or contractual terms",
    },
    "technical": {
        "doc_type":   "technical document (system design, engineering report, or software specification)",
        "focus":      "system architecture, technical requirements, implementation details, performance metrics, and key technologies",
        "one_sent":   "the technical solution described and its primary purpose or benefit",
        "exec_style": "technical but clear language. Cover the problem, technical approach, components, and outcomes",
        "bullet_kw":  "technical requirements, system components, algorithms, performance metrics, or design decisions",
    },
    "research": {
        "doc_type":   "academic research paper",
        "focus":      "research question, hypothesis, methodology, dataset, key findings, statistical results, and conclusions",
        "one_sent":   "the research question and the primary finding or conclusion",
        "exec_style": "academic language. Cover the research objective, methodology, key findings, and implications",
        "bullet_kw":  "research findings, statistical results, hypotheses confirmed/rejected, limitations, or future work",
    },
    "general": {
        "doc_type":   "general document",
        "focus":      "main topics, key information, important conclusions, and actionable insights",
        "one_sent":   "the main topic and most important point",
        "exec_style": "clear and professional language. Cover the purpose, main content, and conclusions",
        "bullet_kw":  "key points, important facts, conclusions, or action items",
    },
}


def _truncate(text: str, max_chars: int = 8000) -> str:
    return text[:max_chars] if len(text) > max_chars else text


def _ctx(domain: str) -> dict:
    return DOMAIN_CONTEXT.get(domain.lower() if domain else "general", DOMAIN_CONTEXT["general"])


def one_sentence_abstract(text: str, domain: str = "general") -> str:
    ctx = _ctx(domain)
    prompt = (
        f"You are summarizing a {ctx['doc_type']}.\n"
        f"Write ONE concise sentence (maximum 30 words) that captures {ctx['one_sent']}.\n\n"
        f"Document:\n{_truncate(text, 4000)}\n\nOne-sentence abstract:"
    )
    result = generate_text(prompt, max_tokens=80, temperature=0.2)
    sentence = result.split('.')[0].strip()
    return (sentence + '.') if not sentence.endswith('.') else sentence


def executive_summary(text: str, domain: str = "general") -> str:
    ctx = _ctx(domain)
    try:
        return summarize_text(
            text, length="medium", extractiveness="medium",
            additional_command=f"Focus on: {ctx['focus']}. Write in {ctx['exec_style']}.",
        )
    except Exception:
        prompt = (
            f"You are summarizing a {ctx['doc_type']}.\n"
            f"Write a professional executive summary in ONE paragraph (3-5 sentences).\n"
            f"Focus on: {ctx['focus']}. Write in {ctx['exec_style']}.\n\n"
            f"Document:\n{_truncate(text, 6000)}\n\nExecutive Summary:"
        )
        return generate_text(prompt, max_tokens=350, temperature=0.3)


def bullet_point_summary(text: str, domain: str = "general", num_points: int = 5) -> str:
    ctx = _ctx(domain)
    prompt = (
        f"You are analyzing a {ctx['doc_type']}.\n"
        f"Extract the {num_points} most important {ctx['bullet_kw']}.\n"
        f"Format as a numbered list. Each point must be concise (max 20 words).\n\n"
        f"Document:\n{_truncate(text, 6000)}\n\nKey Findings:\n1."
    )
    raw    = generate_text(prompt, max_tokens=400, temperature=0.2)
    lines  = [l.strip() for l in raw.strip().split('\n') if l.strip()]
    bullets = [f"• {l.lstrip('0123456789.-) ').strip()}" for l in lines if l.lstrip('0123456789.-) ').strip()]
    return '\n'.join((bullets or [f"• {raw.strip()}"])[:num_points])


def generate_all_summaries(text: str, domain: str = "general") -> dict:
    from etl.metrics import compute_all_metrics
    one_sent = one_sentence_abstract(text, domain)
    exec_sum = executive_summary(text, domain)
    bullets  = bullet_point_summary(text, domain)
    sm       = compute_all_metrics(exec_sum)
    return {
        "domain_used":           domain,
        "summary_one_sentence":  one_sent,
        "summary_executive":     exec_sum,
        "summary_bullet_points": bullets,
        "summary_word_count":    sm["word_count"],
        "summary_reading_level": sm["reading_level_score"],
    }


def summarize_section(section_text: str, style: str = "executive", domain: str = "general") -> str:
    if not section_text or len(section_text.strip()) < 20:
        return "Section too short to summarize."
    dispatch = {
        "one_sentence":  lambda t: one_sentence_abstract(t, domain),
        "executive":     lambda t: executive_summary(t, domain),
        "bullet_points": lambda t: bullet_point_summary(t, domain),
    }
    return dispatch.get(style, dispatch["executive"])(section_text)
