import os
import sys
from datetime import datetime

os.environ["JAVA_TOOL_OPTIONS"] = (
    "--add-opens java.base/javax.security.auth=ALL-UNNAMED "
    "--add-opens java.base/java.lang=ALL-UNNAMED "
    "--add-opens java.base/java.nio=ALL-UNNAMED "
    "--add-opens java.base/sun.nio.ch=ALL-UNNAMED"
)

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, FloatType, BooleanType,
)
from pyspark.sql.functions import col, lit, current_timestamp, when, isnull

from config import SPARK_APP_NAME, SPARK_MASTER, PDF_INPUT_DIR, METRICS_PARQUET, METRICS_CSV
from etl.pdf_extractor import extract_pdf
from etl.transformations import transform_record


PDF_SCHEMA = StructType([
    StructField("file_name",              StringType(),  True),
    StructField("file_path",              StringType(),  True),
    StructField("file_type",              StringType(),  True),
    StructField("has_text",               BooleanType(), True),
    StructField("domain",                 StringType(),  True),
    StructField("clean_text",             StringType(),  True),
    StructField("number_of_pages",        IntegerType(), True),
    StructField("word_count",             IntegerType(), True),
    StructField("sentence_count",         IntegerType(), True),
    StructField("avg_words_per_sentence", FloatType(),   True),
    StructField("reading_level_score",    FloatType(),   True),
    StructField("reading_ease_score",     FloatType(),   True),
    StructField("extraction_method",      StringType(),  True),
    StructField("extraction_error",       StringType(),  True),
])


def get_spark_session() -> SparkSession:
    _opens = (
        "--add-opens java.base/javax.security.auth=ALL-UNNAMED "
        "--add-opens java.base/java.lang=ALL-UNNAMED "
        "--add-opens java.base/java.nio=ALL-UNNAMED "
        "--add-opens java.base/sun.nio.ch=ALL-UNNAMED"
    )
    return (
        SparkSession.builder
        .appName(SPARK_APP_NAME)
        .master(SPARK_MASTER)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "2g")
        .config("spark.executor.memory", "2g")
        .config("spark.driver.extraJavaOptions", _opens)
        .config("spark.executor.extraJavaOptions", _opens)
        .getOrCreate()
    )


def _extract_and_transform(file_path: str) -> dict:
    raw = extract_pdf(file_path)
    return transform_record(raw)


def step1_extract_raw(spark: SparkSession, pdf_dir: str):
    pdf_files = [
        os.path.join(pdf_dir, f)
        for f in os.listdir(pdf_dir)
        if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        print(f"[ETL] No PDFs found in {pdf_dir}")
        return spark.createDataFrame([], PDF_SCHEMA)

    print(f"[ETL] Found {len(pdf_files)} PDFs. Extracting...")
    pdf_rdd = spark.sparkContext.parallelize(pdf_files, numSlices=min(len(pdf_files), 8))
    records_rdd = pdf_rdd.map(_extract_and_transform).map(lambda r: {
        k: (int(v) if isinstance(v, int) else float(v) if isinstance(v, float) else v)
        for k, v in r.items()
    })
    df = spark.createDataFrame(records_rdd, schema=PDF_SCHEMA)
    print(f"[ETL] Extracted {df.count()} records.")
    return df


def step2_transform_standardize(df):
    df = df.filter(col("has_text") == True)
    df = df.filter(isnull(col("extraction_error")) | (col("extraction_error") == ""))
    df = df.filter(col("word_count") > 50)
    df = df.withColumn("processed_at", lit(datetime.utcnow().isoformat()))
    df = df.withColumn(
        "domain",
        when(col("domain").isNull(), lit("general")).otherwise(col("domain"))
    )
    return df


def step3_compute_summary_metrics(df, summaries_df=None):
    if summaries_df is None:
        df = df.withColumn("summary_one_sentence",  lit(None).cast(StringType()))
        df = df.withColumn("summary_executive",     lit(None).cast(StringType()))
        df = df.withColumn("summary_bullet_points", lit(None).cast(StringType()))
        df = df.withColumn("summary_word_count",    lit(0).cast(IntegerType()))
        df = df.withColumn("summary_reading_level", lit(0.0).cast(FloatType()))
        return df

    df = df.join(summaries_df, on="file_name", how="left")

    from pyspark.sql.functions import udf as spark_udf
    from pyspark.sql.types import IntegerType as IT, FloatType as FT

    def _fk(text):
        try:
            import textstat
            return round(textstat.flesch_kincaid_grade(text), 2)
        except Exception:
            return 0.0

    wc_udf = spark_udf(lambda t: len(t.split()) if t else 0, IT())
    rl_udf = spark_udf(lambda t: float(_fk(t)) if t else 0.0, FT())

    df = df.withColumn("summary_word_count",    wc_udf(col("summary_executive")))
    df = df.withColumn("summary_reading_level", rl_udf(col("summary_executive")))
    return df


def step4_write_output(df, out_parquet: str, out_csv: str):
    os.makedirs(os.path.dirname(out_parquet), exist_ok=True)

    output_cols = [
        "file_name", "file_type", "domain",
        "number_of_pages", "word_count", "sentence_count",
        "avg_words_per_sentence", "reading_level_score", "reading_ease_score",
        "summary_word_count", "summary_reading_level",
        "summary_one_sentence", "summary_executive", "summary_bullet_points",
        "processed_at",
    ]
    final_df = df.select([c for c in output_cols if c in df.columns])
    final_df.write.mode("overwrite").parquet(out_parquet)
    final_df.coalesce(1).write.mode("overwrite").option("header", True).csv(out_csv)

    print(f"[ETL] Parquet -> {out_parquet}")
    print(f"[ETL] CSV     -> {out_csv}")
    return final_df


def run_etl_pipeline(pdf_dir: str = PDF_INPUT_DIR,
                     out_parquet: str = METRICS_PARQUET,
                     out_csv: str = METRICS_CSV):
    spark = get_spark_session()
    print("\n=== PDF ETL Pipeline Started ===")
    df = step1_extract_raw(spark, pdf_dir)
    if df.count() == 0:
        print("[ETL] No valid records to process.")
        return df
    df = step2_transform_standardize(df)
    df = step3_compute_summary_metrics(df)
    final = step4_write_output(df, out_parquet, out_csv)
    final.show(5, truncate=True)
    print("=== ETL Pipeline Complete ===\n")
    return final


if __name__ == "__main__":
    pdf_input = sys.argv[1] if len(sys.argv) > 1 else PDF_INPUT_DIR
    run_etl_pipeline(pdf_dir=pdf_input)
