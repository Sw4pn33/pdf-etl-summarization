import sys


def run_etl():
    print("Starting PySpark ETL Pipeline...")
    from etl.spark_pipeline import run_etl_pipeline
    run_etl_pipeline()


def run_ui():
    print("Launching Gradio UI on http://localhost:7860 ...")
    from ui.gradio_app import build_ui
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)


def run_monitor():
    print("Starting Prometheus metrics exporter...")
    from monitoring.metrics_writer import start_prometheus_server
    start_prometheus_server()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ui"

    if mode == "etl":
        run_etl()
    elif mode == "ui":
        run_ui()
    elif mode == "monitor":
        run_monitor()
    elif mode == "all":
        run_etl()
        run_ui()
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python main.py [etl|ui|monitor|all]")
        sys.exit(1)
