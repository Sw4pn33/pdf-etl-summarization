import json
import os
import time
from datetime import datetime

from prometheus_client import start_http_server, Gauge, Counter, Histogram
from config import PROMETHEUS_PORT, METRICS_CSV, METRICS_JSON


PDFS_PROCESSED_TOTAL = Counter(
    "pdfs_processed_total",
    "Total number of PDFs processed",
    ["domain"]
)

AVG_WORD_COUNT = Gauge(
    "pdf_avg_word_count",
    "Average word count per document domain",
    ["domain"]
)

AVG_PROCESSING_TIME = Gauge(
    "pdf_avg_processing_time_seconds",
    "Average processing time per document"
)

READING_LEVEL_ORIGINAL = Gauge(
    "pdf_reading_level_original",
    "Average Flesch-Kincaid grade level of original documents",
    ["domain"]
)

READING_LEVEL_SUMMARY = Gauge(
    "pdf_reading_level_summary",
    "Average Flesch-Kincaid grade level of summaries",
    ["domain"]
)

READING_LEVEL_DIST = Histogram(
    "pdf_reading_level_distribution",
    "Distribution of reading level scores for summaries",
    buckets=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
)

DAILY_VOLUME = Counter(
    "pdf_daily_processing_volume",
    "Daily processing volume by document domain",
    ["domain", "date"]
)


def load_metrics_csv() -> list:
    import csv
    rows = []
    if not os.path.exists(METRICS_CSV):
        return rows
    target = METRICS_CSV
    if os.path.isdir(METRICS_CSV):
        for f in os.listdir(METRICS_CSV):
            if f.endswith(".csv") and not f.startswith("_"):
                target = os.path.join(METRICS_CSV, f)
                break

    if not os.path.isfile(target):
        return rows

    with open(target, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def update_prometheus_metrics(rows: list):
    from collections import defaultdict

    domain_word_counts = defaultdict(list)
    domain_reading_levels = defaultdict(list)
    domain_summary_levels = defaultdict(list)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for row in rows:
        domain = row.get("domain", "general")
        PDFS_PROCESSED_TOTAL.labels(domain=domain).inc()

        wc = row.get("word_count", 0)
        if wc:
            domain_word_counts[domain].append(float(wc))

        rl = row.get("reading_level_score", 0)
        if rl:
            domain_reading_levels[domain].append(float(rl))

        sl = row.get("summary_reading_level", 0)
        if sl:
            domain_summary_levels[domain].append(float(sl))
            READING_LEVEL_DIST.observe(float(sl))

        DAILY_VOLUME.labels(domain=domain, date=today).inc()

    for domain, wcs in domain_word_counts.items():
        AVG_WORD_COUNT.labels(domain=domain).set(sum(wcs) / len(wcs))

    for domain, rls in domain_reading_levels.items():
        READING_LEVEL_ORIGINAL.labels(domain=domain).set(sum(rls) / len(rls))

    for domain, sls in domain_summary_levels.items():
        READING_LEVEL_SUMMARY.labels(domain=domain).set(sum(sls) / len(sls))


def write_grafana_json(rows: list):
    from collections import defaultdict

    domain_stats = defaultdict(lambda: {
        "count": 0, "word_count_sum": 0,
        "reading_level_sum": 0, "summary_level_sum": 0
    })

    today = datetime.utcnow().strftime("%Y-%m-%d")

    for row in rows:
        domain = row.get("domain", "general")
        s = domain_stats[domain]
        s["count"] += 1
        s["word_count_sum"] += float(row.get("word_count", 0) or 0)
        s["reading_level_sum"] += float(row.get("reading_level_score", 0) or 0)
        s["summary_level_sum"] += float(row.get("summary_reading_level", 0) or 0)

    panels = {
        "panel_1_reading_level_comparison": {
            "title": "Avg Reading Level Score: Summary vs Original (by Domain)",
            "type": "bar_chart",
            "data": [
                {
                    "domain": domain,
                    "avg_original_reading_level": round(s["reading_level_sum"] / s["count"], 2) if s["count"] > 0 else 0,
                    "avg_summary_reading_level": round(s["summary_level_sum"] / s["count"], 2) if s["count"] > 0 else 0,
                }
                for domain, s in domain_stats.items()
            ]
        },
        "panel_2_daily_volume_by_domain": {
            "title": "Daily Processing Volume by Document Domain",
            "type": "time_series",
            "data": [
                {
                    "date": today,
                    "domain": domain,
                    "count": s["count"],
                    "avg_word_count": round(s["word_count_sum"] / s["count"], 1) if s["count"] > 0 else 0,
                }
                for domain, s in domain_stats.items()
            ]
        },
        "summary": {
            "total_documents": len(rows),
            "domains": list(domain_stats.keys()),
            "generated_at": datetime.utcnow().isoformat(),
        }
    }

    os.makedirs(os.path.dirname(METRICS_JSON), exist_ok=True)
    with open(METRICS_JSON, 'w') as f:
        json.dump(panels, f, indent=2)
    print(f"[Monitoring] Grafana JSON written -> {METRICS_JSON}")


def start_prometheus_server():
    start_http_server(PROMETHEUS_PORT)
    print(f"[Monitoring] Prometheus exporter running on http://localhost:{PROMETHEUS_PORT}/metrics")

    rows = load_metrics_csv()
    write_grafana_json(rows)
    update_prometheus_metrics(rows)
    print(f"[Monitoring] Loaded {len(rows)} records from CSV. Metrics updated.")

    print("[Monitoring] Refreshing metrics every 60 seconds...")
    while True:
        time.sleep(60)
        rows = load_metrics_csv()
        update_prometheus_metrics(rows)
        write_grafana_json(rows)


if __name__ == "__main__":
    start_prometheus_server()
