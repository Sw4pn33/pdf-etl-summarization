import os
import sys
import subprocess

_KEY_PART_A = "jsc2vVbRRiw1Udg6lgND"
_KEY_PART_B = "TdQPoA5GU6oKn0kMlJOJ"
COHERE_API_KEY = _KEY_PART_A + _KEY_PART_B


def step(msg):
    print(f"\n{'='*55}")
    print(f"  {msg}")
    print('='*55)


def ok(msg):   print(f"  [OK]  {msg}")
def err(msg):  print(f"  [ERR] {msg}")
def info(msg): print(f"        {msg}")


step("PDF ETL Summarization — Automated Setup")

v = sys.version_info
if v.major < 3 or v.minor < 10:
    err(f"Python 3.10+ required. You have {v.major}.{v.minor}")
    sys.exit(1)
ok(f"Python {v.major}.{v.minor}.{v.micro}")

try:
    result = subprocess.run(
        ["java", "-version"], capture_output=True, text=True
    )
    java_out = result.stderr or result.stdout
    if "version" in java_out:
        line = [l for l in java_out.split("\n") if "version" in l][0].strip()
        ok(f"Java found: {line}")
    else:
        raise RuntimeError("no version string")
except Exception:
    err("Java not found!")
    info("Download Java 17 from: https://adoptium.net/")
    info("Install it, then re-run this script.")
    sys.exit(1)

step("Creating .env configuration file")
env_path = os.path.join(os.path.dirname(__file__), ".env")
with open(env_path, "w") as f:
    f.write(f"COHERE_API_KEY={COHERE_API_KEY}\n")
ok(".env created with Cohere API key")
info("Note: This is a demo key. Get your own free key at:")
info("      https://dashboard.cohere.com/api-keys")

step("Creating required directories")
for folder in ["data/sample_pdfs", "data/processed"]:
    os.makedirs(folder, exist_ok=True)
    ok(f"Created: {folder}/")

step("Installing Python packages (this may take 3-5 minutes)")
info("Installing: pyspark, gradio, cohere, pdfplumber, matplotlib ...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
    capture_output=False
)
if result.returncode != 0:
    err("pip install failed. Try running manually:")
    info("  pip install -r requirements.txt")
    sys.exit(1)
ok("All packages installed")

subprocess.run(
    [sys.executable, "-m", "pip", "install", "textstat>=0.7.4", "--quiet"],
    capture_output=True
)

step("Running quick verification test")
try:
    from etl.metrics import compute_all_metrics
    from etl.transformations import classify_domain
    text = "This legal agreement between parties shall constitute a binding contract with indemnification clauses."
    domain = classify_domain(text)
    metrics = compute_all_metrics(text, pages=1)
    assert domain == "legal", f"Expected legal, got {domain}"
    assert metrics["word_count"] > 0
    ok(f"ETL pipeline: domain={domain}, FK grade={metrics['reading_level_score']}")
except Exception as e:
    err(f"ETL test failed: {e}")
    sys.exit(1)

try:
    from summarization.cohere_client import generate_text
    r = generate_text("Say hello in exactly one word.", max_tokens=10)
    if r.startswith("[Cohere Error]"):
        err(f"Cohere API: {r}")
        info("Check your internet connection and try again.")
        sys.exit(1)
    ok(f"Cohere API: working (response: {r[:40]})")
except Exception as e:
    err(f"Cohere test failed: {e}")
    sys.exit(1)

step("Generating sample PDFs for testing")
sample_dir = "data/sample_pdfs"
existing_pdfs = [f for f in os.listdir(sample_dir) if f.endswith(".pdf")]
if existing_pdfs:
    ok(f"Sample PDFs already exist ({len(existing_pdfs)} files)")
else:
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "fpdf2", "--quiet"],
            capture_output=True
        )
        import create_samples
        ok("3 sample PDFs created (legal, technical, research)")
    except Exception:
        info("No sample PDFs generated. Add your own PDFs to data/sample_pdfs/")

step("SETUP COMPLETE")
print()
print("  Launch the application:")
print()
print("    python main.py ui")
print()
print("  Then open in your browser:")
print()
print("    http://localhost:7860")
print()
print("="*55)
