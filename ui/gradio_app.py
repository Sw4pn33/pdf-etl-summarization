import os
import io
import time
import tempfile
import threading
import gradio as gr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

from etl.pdf_extractor import extract_pdf, extract_section
from etl.transformations import transform_record
from etl.metrics import compute_all_metrics
from summarization.multi_level_summary import (
    generate_all_summaries,
    summarize_section,
)

SUMMARY_STYLES = {
    "One-Sentence Abstract": "one_sentence",
    "Executive Summary (Paragraph)": "executive",
    "Bullet-Point Key Findings": "bullet_points",
}

DOMAIN_COLORS = {
    "legal":     "#4A90D9",
    "technical": "#50C878",
    "research":  "#F4A261",
    "general":   "#A78BFA",
}


def _reading_level_label(score: float) -> str:
    if score <= 6:   return f"{score} → Easy (≤ Grade 6)"
    if score <= 10:  return f"{score} → Moderate (Grade 7–10)"
    if score <= 14:  return f"{score} → Advanced (Grade 11–14)"
    return f"{score} → Expert (College+)"


def _ease_label(score: float) -> str:
    if score >= 70:  return f"{score}/100 → Easy"
    if score >= 50:  return f"{score}/100 → Fairly difficult"
    if score >= 30:  return f"{score}/100 → Difficult"
    return f"{score}/100 → Very difficult"


def _make_summary_file(content: str, filename: str) -> str:
    path = os.path.join(tempfile.gettempdir(), f"summary_{filename}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _make_reading_level_chart(doc_score: float, sum_score: float, domain: str):
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    color = DOMAIN_COLORS.get(domain, "#A78BFA")
    bars = ax.bar(
        ["Original Document", "Summary"],
        [doc_score, sum_score],
        color=[color, "#E2E8F0"],
        width=0.4,
        edgecolor="none",
    )

    for bar, val in zip(bars, [doc_score, sum_score]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f"Grade {val}",
            ha="center", va="bottom",
            color="white", fontsize=11, fontweight="bold"
        )

    for grade, label in [(6, "Easy ≤6"), (10, "Moderate ≤10"), (14, "Advanced ≤14")]:
        ax.axhline(grade, color="white", linewidth=0.5, alpha=0.3, linestyle="--")
        ax.text(1.85, grade + 0.1, label, color="white", alpha=0.5, fontsize=8)

    ax.set_ylim(0, max(doc_score, sum_score) * 1.25 + 3)
    ax.set_ylabel("Flesch-Kincaid Grade Level", color="white", fontsize=10)
    ax.set_title(f"Reading Level: Original vs Summary  [{domain.upper()}]",
                 color="white", fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(colors="white")
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color="white", alpha=0.08)
    fig.tight_layout()
    return fig


def _make_domain_dist_chart(domain: str, word_count: int, pages: int):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor("#1e1e2e")

    from config import METRICS_PARQUET
    etl_domains = None
    if os.path.exists(METRICS_PARQUET):
        try:
            df = pd.read_parquet(METRICS_PARQUET, columns=["domain"])
            etl_domains = df["domain"].value_counts().to_dict()
        except Exception:
            pass

    if etl_domains:
        labels  = list(etl_domains.keys())
        sizes   = list(etl_domains.values())
        title   = "ETL Domain Distribution"
    else:
        labels  = ["legal", "technical", "research", "general"]
        sizes   = [25, 35, 25, 15]
        title   = "Domain Distribution (demo)"

    colors = [DOMAIN_COLORS.get(l, "#888") for l in labels]
    ax0 = axes[0]
    ax0.set_facecolor("#1e1e2e")
    wedges, texts = ax0.pie(
        sizes, labels=None, colors=colors,
        startangle=140, wedgeprops=dict(width=0.6, edgecolor="#1e1e2e")
    )
    for i, label in enumerate(labels):
        if label == domain:
            wedges[i].set_linewidth(3)
            wedges[i].set_edgecolor("white")
    legend_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors, labels)]
    ax0.legend(handles=legend_patches, loc="lower center", ncol=2,
               fontsize=8, frameon=False,
               labelcolor="white", bbox_to_anchor=(0.5, -0.05))
    ax0.set_title(title, color="white", fontsize=11, pad=8)

    ax1 = axes[1]
    ax1.set_facecolor("#1e1e2e")
    metrics = ["Words (hundreds)", "Pages"]
    values  = [round(word_count / 100, 1), pages]
    bar_colors = [DOMAIN_COLORS.get(domain, "#A78BFA"), "#E2E8F0"]
    b = ax1.bar(metrics, values, color=bar_colors, width=0.4, edgecolor="none")
    for bar, val in zip(b, [f"{word_count:,} words", f"{pages} pages"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            val, ha="center", va="bottom",
            color="white", fontsize=9, fontweight="bold"
        )
    ax1.set_title("Document Size", color="white", fontsize=11, pad=8)
    ax1.tick_params(colors="white")
    ax1.spines[:].set_visible(False)
    ax1.yaxis.grid(True, color="white", alpha=0.08)
    ax1.set_facecolor("#1e1e2e")
    fig.tight_layout()
    return fig


def process_pdf(pdf_file, summary_style: str):
    no_charts = None, None

    if pdf_file is None:
        return "Please upload a PDF.", "", "", "", None, *no_charts

    start = time.time()
    extracted = extract_pdf(pdf_file.name)
    if not extracted.get("raw_text") and extracted.get("error"):
        return f"Extraction failed: {extracted['error']}", "", "", "", None, *no_charts

    record = transform_record(extracted)
    clean_text = record["clean_text"]
    domain     = record.get("domain", "general")

    if not clean_text or len(clean_text.strip()) < 50:
        return "Could not extract meaningful text from this PDF.", "", "", "", None, *no_charts

    try:
        summaries = generate_all_summaries(clean_text, domain=domain)
    except Exception as e:
        return f"Summarization error: {str(e)}", "", "", clean_text[:5000], None, *no_charts

    for k, v in summaries.items():
        if isinstance(v, str) and v.startswith("[Cohere Error]"):
            return f"Cohere API error:\n{v}", "", "", clean_text[:5000], None, *no_charts

    style_key = SUMMARY_STYLES.get(summary_style, "executive")
    style_map = {
        "one_sentence":  summaries["summary_one_sentence"],
        "executive":     summaries["summary_executive"],
        "bullet_points": summaries["summary_bullet_points"],
    }
    chosen = style_map.get(style_key, summaries["summary_executive"])

    elapsed = round(time.time() - start, 2)
    doc_m = compute_all_metrics(clean_text, record["number_of_pages"])
    sum_m = compute_all_metrics(summaries["summary_executive"])

    domain_emoji = {
        "legal": "⚖️", "technical": "⚙️",
        "research": "🔬", "general": "📄"
    }
    emoji = domain_emoji.get(domain, "📄")

    metrics_md = f"""## {emoji} Document Metrics
| Field | Value |
|-------|-------|
| **File Name** | {record['file_name']} |
| **Domain** | {domain.upper()} |
| **Cohere Prompt Template** | Domain-aware ({domain}) |
| **Pages** | {doc_m['number_of_pages']} |
| **Word Count** | {doc_m['word_count']:,} |
| **Sentence Count** | {doc_m['sentence_count']} |
| **Avg Words/Sentence** | {doc_m['avg_words_per_sentence']} |
| **Reading Level (FK Grade)** | {_reading_level_label(doc_m['reading_level_score'])} |
| **Reading Ease** | {_ease_label(doc_m['reading_ease_score'])} |

## 📊 Summary Metrics
| Field | Value |
|-------|-------|
| **Summary Word Count** | {sum_m['word_count']} |
| **Summary Reading Level** | {_reading_level_label(sum_m['reading_level_score'])} |
| **Summary Reading Ease** | {_ease_label(sum_m['reading_ease_score'])} |
| **Processing Time** | {elapsed}s |

### Compression Ratio
> Original **{doc_m['word_count']:,} words** → Summary **{sum_m['word_count']} words** ({round((1 - sum_m['word_count']/max(doc_m['word_count'],1))*100)}% reduction)
"""

    all_summaries = (
        f"ONE-SENTENCE ABSTRACT (Domain: {domain.upper()})\n{'─'*60}\n{summaries['summary_one_sentence']}\n\n"
        f"EXECUTIVE SUMMARY\n{'─'*60}\n{summaries['summary_executive']}\n\n"
        f"BULLET-POINT KEY FINDINGS\n{'─'*60}\n{summaries['summary_bullet_points']}"
    )

    dl_content = f"FILE: {record['file_name']}\nDOMAIN: {domain.upper()}\n\n{all_summaries}"
    dl_path = _make_summary_file(dl_content, record['file_name'].replace('.pdf', ''))
    raw_preview = f"[Extracted {doc_m['word_count']:,} words from {doc_m['number_of_pages']} pages]\n\n{clean_text}"

    rl_chart = _make_reading_level_chart(doc_m['reading_level_score'], sum_m['reading_level_score'], domain)
    domain_chart = _make_domain_dist_chart(domain, doc_m['word_count'], doc_m['number_of_pages'])

    return metrics_md, chosen, all_summaries, raw_preview, dl_path, rl_chart, domain_chart


def summarize_section_fn(pdf_file, section_input: str, section_style: str):
    if not section_input or not section_input.strip():
        return "Please enter section text or a keyword."

    style_key = SUMMARY_STYLES.get(section_style, "executive")
    text_to_summarize = section_input.strip()

    if pdf_file and len(text_to_summarize) < 150:
        extracted_section = extract_section(pdf_file.name, text_to_summarize)
        if extracted_section and len(extracted_section) > len(text_to_summarize) * 2:
            text_to_summarize = extracted_section
            record = transform_record({"raw_text": text_to_summarize, "file_name": "section", "number_of_pages": 1})
            domain = record.get("domain", "general")
        else:
            domain = "general"
    else:
        record = transform_record({"raw_text": text_to_summarize, "file_name": "section", "number_of_pages": 1})
        domain = record.get("domain", "general")

    if len(text_to_summarize) < 30:
        return "Section too short to summarize. Paste more text or upload a PDF."

    try:
        result = summarize_section(text_to_summarize, style=style_key, domain=domain)
        if result.startswith("[Cohere Error]"):
            return f"Error: {result}"
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def run_etl_pipeline(input_dir: str):
    from config import PDF_INPUT_DIR
    if not input_dir or not input_dir.strip():
        input_dir = PDF_INPUT_DIR

    input_dir = input_dir.strip()
    if not os.path.exists(input_dir):
        return f"Directory not found: `{input_dir}`\nCreate the folder and add PDFs, then retry."

    pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        return f"No PDFs found in `{input_dir}`. Add PDF files and retry."

    status_lines = [f"Found {len(pdfs)} PDF(s) in `{input_dir}`...", "Starting PySpark ETL pipeline..."]

    try:
        from etl.spark_pipeline import run_etl_pipeline as _run
        from config import METRICS_PARQUET, METRICS_CSV
        _run(pdf_dir=input_dir)
        results = []
        if os.path.exists(METRICS_PARQUET):
            results.append(f"Parquet output: `{METRICS_PARQUET}`")
        if os.path.exists(METRICS_CSV):
            results.append(f"CSV output: `{METRICS_CSV}`")
        status_lines += results
        status_lines.append(f"\nETL pipeline complete! Processed {len(pdfs)} PDFs.")
        status_lines.append("   Charts in the Analytics tab will now use live ETL data.")
    except Exception as e:
        status_lines.append(f"ETL pipeline error: {str(e)}")

    return "\n".join(status_lines)


def build_ui() -> gr.Blocks:
    theme = gr.themes.Soft(primary_hue="blue", secondary_hue="slate")

    with gr.Blocks(theme=theme, title="PDF Summarization System") as demo:

        gr.Markdown("""
# PDF Text Extraction & Summarization System
**PySpark ETL · Cohere API (command-r-plus-08-2024) · Domain-Aware Prompts · Gradio**
Upload a PDF to get instant multi-level summaries, reading level analysis, and visual analytics.
        """)

        with gr.Tab("Full Document Summary"):
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_upload = gr.File(
                        label="Upload PDF",
                        file_types=[".pdf"],
                        type="filepath",
                    )
                    summary_style = gr.Dropdown(
                        choices=list(SUMMARY_STYLES.keys()),
                        value="Executive Summary (Paragraph)",
                        label="Select Summary Style",
                        info="Cohere prompt adapts to detected domain"
                    )
                    submit_btn = gr.Button("Extract & Summarize", variant="primary", size="lg")
                    download_btn = gr.File(label="Download All Summaries", visible=True)

                    gr.Markdown("""
**Summary Styles:**
- **One-Sentence Abstract** — Core message in one sentence
- **Executive Summary** — 3-5 sentence professional paragraph
- **Bullet-Point Key Findings** — Top 5 key points

**Domain-Aware Prompts:**
ETL pipeline classifies each PDF into a domain
(legal / technical / research / general) and the
Cohere API uses domain-specific prompt templates.
                    """)

                with gr.Column(scale=2):
                    metrics_out = gr.Markdown(label="Metrics")
                    chosen_summary_out = gr.Textbox(
                        label="Selected Summary",
                        lines=8, interactive=False,
                    )

            with gr.Accordion("View All Three Summary Levels", open=False):
                all_summaries_out = gr.Textbox(
                    label="All Summaries",
                    lines=18, interactive=False,
                )

            with gr.Accordion("Full Extracted Text", open=False):
                raw_text_out = gr.Textbox(
                    label="Extracted & Cleaned Text",
                    lines=20, interactive=False,
                    placeholder="Extracted text will appear here after processing..."
                )

            chart_rl    = gr.State(None)
            chart_dom   = gr.State(None)

            submit_btn.click(
                fn=process_pdf,
                inputs=[pdf_upload, summary_style],
                outputs=[
                    metrics_out, chosen_summary_out, all_summaries_out,
                    raw_text_out, download_btn,
                    chart_rl, chart_dom,
                ],
            )

        with gr.Tab("Section-Specific Summary"):
            gr.Markdown("""
### Summarize a Specific Section
- **Paste section text** directly below, OR
- **Enter a keyword** (e.g., `Introduction`, `Conclusion`, `Methodology`) — system extracts it from the uploaded PDF.
The section's domain is auto-detected and the Cohere prompt adapts accordingly.
            """)
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_for_section = gr.File(
                        label="Upload PDF (for keyword extraction)",
                        file_types=[".pdf"],
                        type="filepath",
                    )
                    section_style = gr.Dropdown(
                        choices=list(SUMMARY_STYLES.keys()),
                        value="Bullet-Point Key Findings",
                        label="Summary Style for This Section"
                    )
                    section_btn = gr.Button("Summarize Section", variant="primary")

                with gr.Column(scale=2):
                    section_input = gr.Textbox(
                        label="Section Text or Keyword",
                        placeholder="Paste section text here, or type a keyword like 'Conclusion'...",
                        lines=10,
                    )
                    section_output = gr.Textbox(
                        label="Section Summary",
                        lines=10, interactive=False,
                    )

            section_btn.click(
                fn=summarize_section_fn,
                inputs=[pdf_for_section, section_input, section_style],
                outputs=[section_output],
            )

        with gr.Tab("Analytics & Charts"):
            gr.Markdown("""
### Visual Analytics
Charts are generated automatically when you process a PDF in the Full Document Summary tab.
They mirror the Grafana dashboard panels:
- **Panel 1**: Reading Level — Original vs Summary (Flesch-Kincaid Grade Level)
- **Panel 2**: Domain Distribution + Document Size
            """)
            with gr.Row():
                rl_chart_out = gr.Plot(label="Panel 1: Reading Level Comparison (Original vs Summary)")
                dom_chart_out = gr.Plot(label="Panel 2: Domain Distribution & Document Size")

            gr.Markdown("""
> **How to use**: Upload a PDF in the Full Document Summary tab, click Extract & Summarize,
then return here to see the charts auto-populated. If the ETL pipeline has been run (see ETL tab),
the Domain Distribution chart will show the actual distribution across all processed PDFs.
            """)

            refresh_btn = gr.Button("Refresh Charts", size="sm")

            def _refresh(rl, dom):
                return rl, dom

            refresh_btn.click(
                fn=_refresh,
                inputs=[chart_rl, chart_dom],
                outputs=[rl_chart_out, dom_chart_out],
            )

            submit_btn.click(
                fn=_refresh,
                inputs=[chart_rl, chart_dom],
                outputs=[rl_chart_out, dom_chart_out],
            )

        with gr.Tab("Run ETL Pipeline"):
            gr.Markdown("""
### PySpark ETL Pipeline
Batch-process a folder of PDFs using the PySpark ETL pipeline:
1. **Extracts** text from all PDFs (pdfplumber + PyMuPDF fallback)
2. **Cleans & standardizes** text (unicode normalization, noise removal)
3. **Classifies** domain (legal / technical / research / general)
4. **Computes** Flesch-Kincaid reading level metrics
5. **Writes** output to Parquet + CSV (`data/processed/`)

The Analytics tab domain chart will use live ETL data after the run.
            """)
            with gr.Row():
                with gr.Column(scale=1):
                    etl_input_dir = gr.Textbox(
                        label="PDF Input Directory",
                        value="data/sample_pdfs",
                        placeholder="Path to folder containing PDF files",
                        info="Relative to project root, e.g., data/pdfs"
                    )
                    etl_btn = gr.Button("Run PySpark ETL Pipeline", variant="primary", size="lg")
                    gr.Markdown("""
**Output files:**
- `data/processed/pdf_metrics.parquet`
- `data/processed/pdf_metrics.csv`
                    """)

                with gr.Column(scale=2):
                    etl_status = gr.Textbox(
                        label="ETL Pipeline Status",
                        lines=12,
                        interactive=False,
                        placeholder="ETL pipeline output will appear here...",
                    )

            etl_btn.click(
                fn=run_etl_pipeline,
                inputs=[etl_input_dir],
                outputs=[etl_status],
            )

        with gr.Tab("System Architecture"):
            gr.Markdown("""
## System Architecture

```
PDF Files (thousands)
       |
       v
+-------------------------------------+
|        PySpark ETL Pipeline         |
|  1. PDF Text Extraction             |  <- pdfplumber (primary) + PyMuPDF (fallback)
|  2. Text Standardization            |  <- unicode norm, regex cleaning
|  3. Domain Classification           |  <- keyword frequency -> legal/technical/research/general
|  4. Flesch-Kincaid Metrics          |  <- word_count, pages, reading_level_score
|  Output -> Parquet + CSV            |
+--------------+----------------------+
               |
               v
+-----------------------------------------------------+
|           Cohere API (command-r-plus-08-2024)        |
|  Domain-Aware Prompts:                               |
|  * legal     -> focus on parties, clauses, dates     |
|  * technical -> focus on architecture, metrics       |
|  * research  -> focus on hypothesis, methodology     |
|  * general   -> focus on main topics, conclusions    |
|                                                      |
|  3-Level Summarization:                              |
|  1. One-sentence abstract                            |
|  2. Executive summary (paragraph)                    |
|  3. Bullet-point key findings (5 points)             |
+--------------+--------------------------------------+
               |
       +-------+-------+
       v               v
+-------------+  +--------------------------+
|   Gradio UI |  |   Grafana Dashboard      |
|  * Upload   |  |   Panel 1: Reading Level | <- FK Grade: Original vs Summary
|  * Dropdown |  |   Panel 2: Daily Volume  | <- Domain distribution over time
|  * Metrics  |  +--------------------------+
|  * Charts   |
|  * Section  |
|  * ETL btn  |
+-------------+
```

## Metrics Computed (Original + Summary)
| Metric | Original | Summary |
|--------|:-------:|:-------:|
| `word_count` | Yes | Yes |
| `number_of_pages` | Yes | — |
| `reading_level_score` (FK Grade) | Yes | Yes |
| `reading_ease_score` (0-100) | Yes | Yes |
| `sentence_count` | Yes | Yes |
| `domain` | Yes | — |

## Domain-Aware Prompt System
| Domain | Cohere Prompt Focus |
|--------|---------------------|
| **Legal** | Parties, obligations, liability clauses, effective dates |
| **Technical** | Architecture, requirements, metrics, design decisions |
| **Research** | Research question, methodology, findings, conclusions |
| **General** | Main topics, key information, actionable insights |
            """)

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
