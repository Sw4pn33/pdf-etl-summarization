import os
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")

SPARK_APP_NAME = "PDF-ETL-Summarization"
SPARK_MASTER   = "local[*]"

PDF_INPUT_DIR        = "data/sample_pdfs"
PROCESSED_OUTPUT_DIR = "data/processed"
METRICS_PARQUET      = "data/processed/pdf_metrics.parquet"
METRICS_CSV          = "data/processed/pdf_metrics.csv"
METRICS_JSON         = "data/processed/grafana_metrics.json"

PROMETHEUS_PORT = 8000

DOMAIN_KEYWORDS = {
    "legal": [
        "contract", "agreement", "clause", "party", "liability", "indemnify",
        "jurisdiction", "whereas", "hereinafter", "arbitration", "breach",
    ],
    "technical": [
        "algorithm", "system", "implementation", "architecture", "framework",
        "protocol", "database", "api", "software", "hardware", "network",
        "computation", "module", "function", "class", "method",
    ],
    "research": [
        "abstract", "hypothesis", "methodology", "literature", "findings",
        "conclusion", "experiment", "dataset", "analysis", "results",
        "correlation", "regression", "statistical", "citation", "references",
    ],
}
