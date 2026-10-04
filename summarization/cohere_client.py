import cohere
from config import COHERE_API_KEY

_client = None


def get_client() -> cohere.Client:
    global _client
    if _client is None:
        _client = cohere.Client(api_key=COHERE_API_KEY)
    return _client


def generate_text(prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
    try:
        response = get_client().chat(
            model="command-r-plus-08-2024",
            message=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.text.strip()
    except Exception as e:
        return f"[Cohere Error] {str(e)}"


def summarize_text(
    text: str,
    length: str = "medium",
    extractiveness: str = "medium",
    additional_command: str = "Focus on the key findings and important information.",
) -> str:
    if len(text) > 50000:
        text = text[:50000]
    try:
        response = get_client().summarize(
            text=text,
            length=length,
            format="paragraph",
            extractiveness=extractiveness,
            additional_command=additional_command,
            model="command-r-plus-08-2024",
        )
        return response.summary.strip()
    except Exception:
        return generate_text(
            f"Summarize the following document in a {length} paragraph:\n\n{text[:3000]}\n\nSummary:",
            max_tokens=400,
        )
