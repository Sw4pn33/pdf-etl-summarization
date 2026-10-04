<div align="center">

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="900">

<br>

# 📄 PDF Text Extraction & Summarization System

<br>

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/PySpark-3.5.0-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white">
<img src="https://img.shields.io/badge/Cohere-command--r--plus-6236FF?style=for-the-badge&logoColor=white">
<img src="https://img.shields.io/badge/Gradio-UI-FF7C00?style=for-the-badge&logo=gradio&logoColor=white">
<img src="https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=for-the-badge&logo=prometheus&logoColor=white">
<img src="https://img.shields.io/badge/Grafana-Dashboard-F46800?style=for-the-badge&logo=grafana&logoColor=white">

<br><br>

<img src="https://img.shields.io/badge/ETL-Pipeline-blue?style=flat-square">
<img src="https://img.shields.io/badge/NLP-Summarization-green?style=flat-square">
<img src="https://img.shields.io/badge/Domain-Aware%20Prompts-purple?style=flat-square">
<img src="https://img.shields.io/badge/Flesch--Kincaid-Metrics-orange?style=flat-square">
<img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square">

<br><br>

> **Enterprise-grade PDF intelligence platform — ETL pipeline · AI summarization · real-time monitoring**
>
> *Case Study Q16 · Data Engineering · NLP · Performance Monitoring*

<br>

[🚀 Quick Start](#-quick-start) &nbsp;·&nbsp; [📖 Usage Guide](#-usage-guide) &nbsp;·&nbsp; [📊 Grafana Dashboard](#-grafana-dashboard) &nbsp;·&nbsp; [🛠️ Troubleshooting](#-troubleshooting)

<br>

<img src="https://user-images.githubusercontent.com/74038190/212748842-9fcbad5b-6173-4175-8a61-521f3dbb7514.gif" width="500">

</div>

---

## ✨ What This System Does

<img src="https://user-images.githubusercontent.com/74038190/212284158-e840e285-664b-44d7-b79b-e264b5e54825.gif" width="380" align="right">

This system transforms a large collection of PDF documents into structured intelligence through three integrated layers:

**🔧 1. PySpark ETL Pipeline**
Processes thousands of PDFs in parallel. Classifies each by domain — legal, technical, research, or general — and computes Flesch-Kincaid reading-level metrics for both the original document and its AI-generated summary.

**🤖 2. Cohere AI Summarization**
Uses domain-aware prompt templates derived directly from the ETL classification to generate three summary levels per document: one-sentence abstract, executive paragraph, and bullet-point key findings.

**📊 3. Prometheus + Grafana Monitoring**
A metrics exporter feeds live KPI panels in Grafana: reading level comparison (original vs summary) and daily processing volume by domain.

<br clear="right">

---

## 🌟 Key Features

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/212749447-bfb7e725-6987-49d9-ae85-2015e3e7cc41.gif" width="600">
</div>

<br>

| Feature | Details |
|---------|---------|
| 🔍 **Dual PDF Extraction** | pdfplumber (primary) + PyMuPDF fallback for maximum compatibility |
| 🏷️ **Domain Auto-Detection** | Keyword-frequency classifier → legal / technical / research / general |
| 🎯 **Domain-Aware Prompts** | ETL domain feeds directly into Cohere prompt templates |
| 📝 **3-Level Summarization** | One-sentence abstract, executive summary, bullet-point findings |
| 📐 **Flesch-Kincaid Metrics** | FK Grade + Reading Ease for both original and summary |
| 🔎 **Section Summarizer** | Keyword extraction OR paste custom text for targeted summaries |
| ⚡ **PySpark Scalability** | `local[*]` mode works on any laptop; scales to multi-node clusters |
| 💾 **Parquet + CSV Output** | Structured ETL output ready for downstream analytics |
| 📈 **Grafana Dashboard** | 7 KPI panels with Prometheus time-series metrics |
| 🛠️ **One-Command Setup** | `python setup.py` installs everything and verifies the installation |

---

## 🏗️ Architecture

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/212748830-4c709398-a386-4761-84d7-9e10b98fbe6e.gif" width="500">
</div>

```
PDF Files (thousands)
       │
       ▼
┌──────────────────────────────────────────────────┐
│              PySpark ETL Pipeline                │
│                                                  │
│  Step 1 ── Extract    pdfplumber + PyMuPDF       │
│  Step 2 ── Clean      unicode norm, noise strip  │
│  Step 3 ── Classify   legal/tech/research/gen    │
│  Step 4 ── Metrics    Flesch-Kincaid Grade       │
│  Step 5 ── Write      Parquet + CSV output       │
└─────────────────────┬────────────────────────────┘
                      │  domain + structured data
                      ▼
┌──────────────────────────────────────────────────┐
│        Cohere API  (command-r-plus-08-2024)      │
│                                                  │
│  Domain-Aware Prompt Templates:                  │
│  • legal     → parties, clauses, effective dates │
│  • technical → architecture, requirements, KPIs  │
│  • research  → hypothesis, methodology, findings │
│  • general   → main topics, actionable insights  │
│                                                  │
│  3 Summary Levels Per Document:                  │
│  1. One-sentence abstract    (≤30 words)         │
│  2. Executive summary        (paragraph)         │
│  3. Bullet-point findings    (5 key points)      │
└──────────┬────────────────────────────────────────┘
           │
   ┌───────┴──────────┐
   ▼                  ▼
Gradio UI          Prometheus Exporter
(port 7860)        (port 8000)
                       │
                       ▼
                  Grafana Dashboard
                  (7 KPI panels)
```

---

## 📋 Case Study Q16 — Requirements Checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | PySpark ETL for massive heterogeneous PDF collections | ✅ |
| 2 | Domain classification (legal, technical, research, general) | ✅ |
| 3 | Flesch-Kincaid metrics for **original** document | ✅ |
| 4 | Flesch-Kincaid metrics for **summary** | ✅ |
| 5 | Structured Parquet + CSV output | ✅ |
| 6 | ETL domain output used to fine-tune Cohere prompts | ✅ |
| 7 | One-sentence abstract | ✅ |
| 8 | Paragraph executive summary | ✅ |
| 9 | Bullet-point key findings | ✅ |
| 10 | Gradio UI with PDF upload + style dropdown | ✅ |
| 11 | Section-specific summary (keyword or paste) | ✅ |
| 12 | Grafana dashboard with ≥2 KPI panels | ✅ |
| 13 | Panel 1: Avg reading level — summary vs original | ✅ |
| 14 | Panel 2: Daily processing volume by domain | ✅ |
| 15 | PySpark data → Prometheus → Grafana pipeline | ✅ |
| 16 | Avg word count per domain panel | ✅ |
| 17 | Processing time monitoring | ✅ |
| 18 | Reading level score distribution (summaries) | ✅ |

---

## 🚀 Quick Start

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/218265814-3c16485b-1a0c-4b4f-a2cd-a23b3e3e8a75.gif" width="500">
</div>

<br>

### Prerequisites — Install These First

| Tool | Version | Download |
|------|---------|---------|
| 🐍 **Python** | 3.10, 3.11, or 3.12 | [python.org/downloads](https://www.python.org/downloads/) |
| ☕ **Java JDK 17** | 17 (recommended) | [adoptium.net](https://adoptium.net/temurin/releases/?version=17) |
| 🔀 **Git** | Any | [git-scm.com](https://git-scm.com/downloads) |

> ⚠️ **Java 23 users:** PySpark 3.5 has a compatibility issue with Java 23. Please install **Java 17** — it can coexist with other Java versions on the same machine.

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Sw4pn33/pdf-etl-summarization.git
cd pdf-etl-summarization
```

---

### Step 2 — Create a Virtual Environment

**Windows (PowerShell or Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ Your terminal prompt should now show `(venv)` — this means the virtual environment is active.

---

### Step 3 — Run Automated Setup

```bash
python setup.py
```

This single command does **everything**:

```
=========================================================
  PDF ETL Summarization — Automated Setup
=========================================================
  [OK]  Python 3.11.5
  [OK]  Java found: openjdk version "17.0.9"
  [OK]  .env created with Cohere API key
  [OK]  Created: data/sample_pdfs/
  [OK]  Created: data/processed/
  [OK]  All packages installed
  [OK]  ETL pipeline: domain=legal, FK grade=12.4
  [OK]  Cohere API: working (response: Hello)
  [OK]  3 sample PDFs created (legal, technical, research)

=========================================================
  SETUP COMPLETE
=========================================================

  Launch the application:

    python main.py ui

  Then open in your browser:

    http://localhost:7860
```

> ⏱️ Takes **3–5 minutes** on first run (PySpark is a large package).

---

### Step 4 — Add Your PDFs *(Optional)*

Copy any PDF files you want to analyze into:
```
data/sample_pdfs/
```
3 sample PDFs (legal contract, technical report, research paper) are already created automatically by the setup script.

---

### Step 5 — Launch the App

```bash
python main.py ui
```

**Open your browser and go to:**

<div align="center">

### 🌐 [http://localhost:7860](http://localhost:7860)

</div>

That's it! 🎉

---

## 📖 Usage Guide

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/229223263-cf2e4b07-2615-4f87-9c38-e37600f8381a.gif" width="500">
</div>

<br>

### 📋 Tab 1 — Full Document Summary

1. Click **Upload PDF** and select any PDF file
2. Choose a **Summary Style** from the dropdown:
   - `One-Sentence Abstract` — core message in ≤30 words
   - `Executive Summary` — 3–5 sentence professional paragraph
   - `Bullet-Point Key Findings` — top 5 key points
3. Click **Extract & Summarize**
4. View: domain detection, FK reading level, compression ratio, all 3 summaries
5. **Download** all summaries as a `.txt` file

**Example output you will see:**

```
╔══════════════════════════════════════════════════════════╗
║  Document Metrics                                        ║
╠══════════════════════════════════════════════════════════╣
║  File Name    : research_paper.pdf                       ║
║  Domain       : RESEARCH                                 ║
║  Pages        : 14                                       ║
║  Word Count   : 8,432                                    ║
║  FK Grade     : 14.2 → Advanced (Grade 11–14)            ║
║  Reading Ease : 38/100 → Difficult                       ║
╠══════════════════════════════════════════════════════════╣
║  Summary Metrics                                         ║
╠══════════════════════════════════════════════════════════╣
║  Summary Words     : 142                                 ║
║  Summary FK Grade  : 9.1 → Moderate (Grade 7–10)        ║
║  Summary Ease      : 61/100 → Fairly difficult           ║
║  Processing Time   : 4.3s                                ║
╠══════════════════════════════════════════════════════════╣
║  Compression: 8,432 words → 142 words  (98% reduction)  ║
╚══════════════════════════════════════════════════════════╝
```

---

### 🔍 Tab 2 — Section-Specific Summary

1. (Optional) Upload a PDF
2. **Type a keyword** — e.g., `Introduction`, `Conclusion`, `Methodology`
   — the system finds and extracts that section from the PDF
   OR **paste section text** directly into the text box
3. Select a summary style and click **Summarize Section**

---

### 📊 Tab 3 — Analytics & Charts

- **Panel 1** — Bar chart: FK Grade Level of original document vs generated summary
- **Panel 2** — Domain distribution pie chart + document size chart
- Charts auto-populate after processing in Tab 1
- After running the ETL pipeline, the domain chart shows real distribution across all PDFs

---

### ⚙️ Tab 4 — Run ETL Pipeline

1. Enter the PDF folder path (default: `data/sample_pdfs`)
2. Click **Run PySpark ETL Pipeline**
3. Outputs saved to:
   - `data/processed/pdf_metrics.parquet` — for Grafana / downstream analysis
   - `data/processed/pdf_metrics.csv` — human-readable

**ETL output table columns:**

| Column | Description |
|--------|-------------|
| `file_name` | Original PDF filename |
| `domain` | Detected domain (legal/technical/research/general) |
| `word_count` | Total word count |
| `sentence_count` | Total sentence count |
| `avg_words_per_sentence` | Average words per sentence |
| `reading_level_score` | Flesch-Kincaid Grade Level |
| `reading_ease_score` | Flesch Reading Ease (0–100) |
| `number_of_pages` | Page count |
| `extraction_method` | `pdfplumber` or `pymupdf` |

---

## 🔬 How Domain-Aware Prompting Works

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/212749171-b84692a8-2b04-4e3b-93ca-ac14705da224.gif" width="400">
</div>

<br>

The ETL pipeline classifies each PDF by counting domain-specific keyword frequencies:

| Domain | Sample Keywords |
|--------|----------------|
| ⚖️ **Legal** | agreement, contract, clause, liability, indemnification, jurisdiction, plaintiff |
| ⚙️ **Technical** | algorithm, architecture, deployment, API, latency, throughput, implementation |
| 🔬 **Research** | hypothesis, methodology, findings, conclusion, dataset, experiment, citation |
| 📄 **General** | (default when no domain reaches threshold) |

The detected domain selects a specialized Cohere prompt:

```
Legal document detected →
  "You are a legal analyst. Focus on key parties, obligations,
   liability clauses, effective dates, and governing jurisdiction..."

Technical document detected →
  "You are a technical writer. Focus on system architecture,
   performance metrics, design decisions, and requirements..."

Research document detected →
  "You are a research analyst. Focus on the research question,
   methodology, key findings, and implications..."
```

This domain-routing step makes summaries significantly more accurate than using a single generic prompt.

---

## ⚙️ All Run Modes

```bash
python main.py ui        # Launch Gradio web interface  (default)
python main.py etl       # Run PySpark ETL batch pipeline only
python main.py monitor   # Start Prometheus metrics exporter only
python main.py all       # Run ETL, then launch UI
```

---

## 📊 Grafana Dashboard

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/212284136-03988914-d899-44b4-b1d9-4eeccf656e44.gif" width="500">
</div>

<br>

Import `monitoring/grafana_dashboard.json` into your Grafana instance.

### Setup Steps

**1.** Start the Prometheus metrics exporter:
```bash
python main.py monitor
```

**2.** In Grafana: **Connections → Data Sources → Add → Prometheus**
- URL: `http://localhost:8000`
- Click **Save & Test**

**3.** **Dashboards → Import → Upload JSON file** → select `monitoring/grafana_dashboard.json`

### 7 Dashboard Panels

| Panel | Visualization | Prometheus Query |
|-------|-------------|-----------------|
| Total PDFs Processed | Stat | `sum(pdfs_processed_total)` |
| Avg Processing Time | Stat | `pdf_avg_processing_time_seconds` |
| Avg Word Count by Domain | Bar chart | `pdf_avg_word_count{domain="..."}` |
| **Reading Level: Summary vs Original** | **Bar chart** | `pdf_reading_level_original / summary` |
| **Daily Volume by Domain** | **Time series** | `increase(pdfs_processed_total[1d])` |
| Reading Level Distribution | Time series | `histogram_quantile(0.5 / 0.9 / 0.95, ...)` |
| PDFs Processed by Domain | Gauge | `pdfs_processed_total` |

---

## 📁 Project Structure

```
pdf-etl-summarization/
│
├── 📄 main.py                     ← Entry point (etl / ui / monitor / all)
├── ⚙️  config.py                  ← Paths, env vars, domain keywords
├── 🛠️  setup.py                   ← One-command automated setup
├── 📦 requirements.txt            ← 16 Python dependencies
├── 🔑 .env.example                ← Template for API key
│
├── 📂 etl/
│   ├── pdf_extractor.py           ← pdfplumber + PyMuPDF extraction
│   ├── transformations.py         ← Text cleaning + domain classification
│   ├── metrics.py                 ← Flesch-Kincaid grade + ease score
│   └── spark_pipeline.py          ← PySpark 4-step ETL pipeline
│
├── 📂 summarization/
│   ├── cohere_client.py           ← Cohere API v5 (command-r-plus-08-2024)
│   └── multi_level_summary.py     ← 3-level domain-aware summarization
│
├── 📂 ui/
│   └── gradio_app.py              ← Gradio Blocks UI (5 tabs + charts)
│
├── 📂 monitoring/
│   ├── metrics_writer.py          ← Prometheus exporter + Grafana JSON writer
│   └── grafana_dashboard.json     ← 7-panel Grafana dashboard (import-ready)
│
└── 📂 data/
    ├── sample_pdfs/               ← Input PDFs (auto-created by setup.py)
    └── processed/                 ← ETL outputs: Parquet + CSV
```

---

## 🛠️ Troubleshooting

<div align="center">
<img src="https://user-images.githubusercontent.com/74038190/212284087-bbe7e430-757e-4901-90bf-4cd2ce3e1852.gif" width="350">
</div>

<br>

### ❌ `Java not found` or `JAVA_HOME not set`

1. Download JDK 17 from [adoptium.net](https://adoptium.net/temurin/releases/?version=17)
2. Install it
3. **Windows:** Search *Edit the system environment variables* → *Environment Variables* → *New*:
   - Name: `JAVA_HOME`
   - Value: `C:\Program Files\Eclipse Adoptium\jdk-17.x.x.x-hotspot`
4. Restart your terminal and re-run `python setup.py`

### ❌ `ModuleNotFoundError: No module named 'xyz'`

Make sure your virtual environment is active:
```bash
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### ❌ `ModuleNotFoundError: No module named 'pkg_resources'`

```bash
pip install "textstat>=0.7.4" setuptools
```

### ❌ `[Cohere Error] 401` or API key error

Check that your `.env` file exists in the project root:
```
COHERE_API_KEY=your_actual_key_here
```
Get a free key at [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)

### ❌ PySpark `UnsupportedOperationException: getSubject` (Java 17/23)

Auto-handled by the pipeline. If it still occurs:
```bash
# Windows
set JAVA_TOOL_OPTIONS=--add-opens java.base/javax.security.auth=ALL-UNNAMED

# macOS/Linux
export JAVA_TOOL_OPTIONS="--add-opens java.base/javax.security.auth=ALL-UNNAMED"

python main.py etl
```

### ❌ Port 7860 already in use

```bash
# Windows
netstat -ano | findstr :7860
taskkill /PID <pid_number> /F

# macOS/Linux
lsof -i :7860 | grep LISTEN
kill -9 <pid>
```

### ❌ Empty or garbled text from PDF

Some PDFs are scanned images — they need OCR. The system extracts what it can via PyMuPDF. For scanned PDFs, pre-process with Tesseract OCR before running this pipeline.

---

## 🔑 Key Design Decisions

| Decision | Reason |
|----------|--------|
| **pdfplumber** as primary | Best text layout preservation for digital/structured PDFs |
| **PyMuPDF** as fallback | Handles encrypted, compressed, or malformed PDFs |
| **`command-r-plus-08-2024`** pinned | `command-r-plus` (unpinned) was removed from Cohere in Sep 2025 |
| **Domain-aware prompting** | Dramatically improves summary accuracy vs a generic prompt |
| **FK metrics on both** | Measures how well the summary reduces reading complexity |
| **Prometheus → Grafana** | Industry-standard observability stack; no vendor lock-in |
| **`local[*]` Spark mode** | Runs on any laptop; change master URL to scale to a Hadoop cluster |
| **Parquet output** | Columnar format — fast for large-scale downstream analytics |

---

## 📦 Tech Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=python,java,grafana,git&theme=dark" />

<br><br>

| Layer | Technology | Version |
|-------|-----------|---------|
| ⚡ ETL Engine | Apache PySpark | 3.5.0 |
| 📄 PDF Extraction | pdfplumber + PyMuPDF | 0.10.3 / 1.23.8 |
| 🤖 AI Summarization | Cohere API | v5 (command-r-plus-08-2024) |
| 📐 Reading Metrics | textstat (Flesch-Kincaid) | ≥0.7.4 |
| 🖥️ Web UI | Gradio + matplotlib | ≥4.19.2 / 3.8.2 |
| 📡 Monitoring | Prometheus client | 0.19.0 |
| 📊 Dashboard | Grafana | 10.x |
| 💾 Storage | Apache Parquet + CSV | pyarrow 14.0.2 |
| 🐍 Language | Python | 3.10+ |

</div>

---

## 📈 Sample Grafana Output

After running `python main.py monitor` and importing the dashboard JSON:

```
┌─────────────────────────────────────────────────────────────┐
│  Panel 1: Reading Level — Original vs Summary (by Domain)   │
│                                                             │
│  Grade                                                      │
│  16 ┤                                                       │
│  14 ┤  ████                                                 │
│  12 ┤  ████  ████                                           │
│  10 ┤  ████  ████  ████                                     │
│   8 ┤  ████  ████  ████  ████ ░░░░ ░░░░ ░░░░ ░░░░          │
│   6 ┤  ████  ████  ████  ████ ░░░░ ░░░░ ░░░░ ░░░░          │
│   0 └──────────────────────────────────────────────────     │
│       legal  tech  rsch  gen  legal  tech  rsch  gen        │
│       ←── Original Documents ───┤ ←── Summaries (lower) ──→│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Panel 2: Daily Processing Volume by Domain (Time Series)   │
│                                                             │
│  PDFs/day                                                   │
│  120 ┤ ╭─╮                                                  │
│   80 ┤ │ │  ╭──╮                                            │
│   40 ┤ │ ╰──╯  │  ╭──╮                                     │
│    0 └─────────────────────────────────────────────────     │
│       Mon   Tue   Wed   Thu   Fri                           │
│      ─ legal  ─ technical  ─ research  ─ general            │
└─────────────────────────────────────────────────────────────┘
```

---

<div align="center">

<img src="https://user-images.githubusercontent.com/74038190/212284115-f47cd8ff-2ffb-4b04-b5bf-4d1c14c0247f.gif" width="600">

<br>

**Built for Case Study Q16 — PDF Text Extraction and Summarization**

*PySpark ETL · Cohere API · Gradio UI · Prometheus · Grafana*

<br>

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="900">

</div>
