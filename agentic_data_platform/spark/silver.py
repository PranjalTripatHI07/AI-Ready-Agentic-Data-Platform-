#!/usr/bin/env python3

"""
Silver Layer - Clean and Validated Data
Reads Bronze Delta table, applies data quality rules, and writes cleaned data.
FAILS on invalid data - strict validation enforced.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, trim, lower, count, lit
)
from pyspark.sql.types import TimestampType
import sys

# Here we are defining the paths for bronze data storage, silver data storage, and Spark checkpointing
import os
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE_PATH = os.path.join(BASE_PATH, "data/bronze/ecommerce_events")
SILVER_PATH = os.path.join(BASE_PATH, "data/silver/ecommerce_events")
CHECKPOINT_PATH = os.path.join(BASE_PATH, "data/checkpoints/silver")

# Valid event types
VALID_EVENT_TYPES = ["view", "cart", "purchase"]


def create_spark_session() -> SparkSession:
    """
    Create and configure Spark session with Delta Lake support.
    """
    spark = SparkSession.builder \
        .appName("Silver_Layer_Cleaning") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_bronze_data(spark: SparkSession):
    """
    Read data from Bronze Delta table.
    """
    print(f"Reading from Bronze path: {BRONZE_PATH}")
    
    try:
        bronze_df = spark.read.format("delta").load(BRONZE_PATH)
        record_count = bronze_df.count()
        print(f"✓ Read {record_count} records from Bronze layer")
        return bronze_df
    except Exception as e:
        print(f"✗ Failed to read Bronze data: {e}")
        sys.exit(1)


def validate_data_quality(df, spark: SparkSession) -> bool:
    """
    Check for data quality issues that should cause failure.
    Returns True if data is valid, False otherwise.
    """
    print("\nRunning data quality validations...")
    
    issues = []
    
    # Check 1: Null user_id
    null_users = df.filter(col("user_id").isNull()).count()
    if null_users > 0:
        issues.append(f"Found {null_users} records with NULL user_id")
    
    # Check 2: Invalid event_type
    invalid_events = df.filter(
        ~lower(trim(col("event_type"))).isin([e.lower() for e in VALID_EVENT_TYPES])
    ).count()
    if invalid_events > 0:
        issues.append(f"Found {invalid_events} records with invalid event_type")
    
    # Check 3: Null product_id
    null_products = df.filter(col("product_id").isNull()).count()
    if null_products > 0:
        issues.append(f"Found {null_products} records with NULL product_id")
    
    # Check 4: Negative prices
    negative_prices = df.filter(col("price") < 0).count()
    if negative_prices > 0:
        issues.append(f"Found {negative_prices} records with negative price")
    
    # Check 5: Purchase events with zero price
    zero_price_purchases = df.filter(
        (lower(trim(col("event_type"))) == "purchase") & 
        ((col("price").isNull()) | (col("price") <= 0))
    ).count()
    if zero_price_purchases > 0:
        issues.append(f"Found {zero_price_purchases} purchase events with zero/null price")
    
    if issues:
        print("\n" + "=" * 60)
        print("DATA QUALITY ISSUES DETECTED - JOB WILL FAIL")
        print("=" * 60)
        for issue in issues:
            print(f"  ✗ {issue}")
        print("=" * 60)
        return False
    
    print("✓ All data quality checks passed")
    return True


def clean_data(df):
    """
    Apply cleaning transformations to the data.
    """
    print("\nApplying data cleaning transformations...")
    
    # Remove duplicates based on user_id, product_id, event_type, timestamp
    cleaned_df = df.dropDuplicates(["user_id", "product_id", "event_type", "event_timestamp"])
    
    # Remove null user_id records
    cleaned_df = cleaned_df.filter(col("user_id").isNotNull())
    
    # Normalize event_type to lowercase
    cleaned_df = cleaned_df.withColumn("event_type", lower(trim(col("event_type"))))
    
    # Filter only valid event types
    cleaned_df = cleaned_df.filter(col("event_type").isin(VALID_EVENT_TYPES))
    
    # Convert timestamp string to proper timestamp type
    cleaned_df = cleaned_df.withColumn(
        "event_timestamp_parsed",
        to_timestamp(col("event_timestamp"))
    )
    
    # Remove invalid timestamps
    cleaned_df = cleaned_df.filter(col("event_timestamp_parsed").isNotNull())
    
    # Select and rename columns for Silver layer
    silver_df = cleaned_df.select(
        col("user_id"),
        col("product_id"),
        col("event_type"),
        col("price"),
        col("event_timestamp_parsed").alias("event_timestamp"),
        col("kafka_timestamp").alias("ingestion_timestamp")
    )
    
    return silver_df


def write_to_silver(df, output_path: str):
    """
    Write cleaned data to Silver Delta table.
    """
    print(f"\nWriting to Silver path: {output_path}")
    
    record_count = df.count()
    
    df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save(output_path)
    
    print(f"✓ Wrote {record_count} records to Silver layer")
    return record_count


def main():
    """
    Main function to run the Silver layer processing pipeline.
    """
    print("=" * 60)
    print("Silver Layer - Data Cleaning & Validation")
    print("=" * 60)
    print(f"Bronze Path: {BRONZE_PATH}")
    print(f"Silver Path: {SILVER_PATH}")
    print("=" * 60)
    
    # Create Spark session
    spark = create_spark_session()
    print("✓ Spark session created")
    
    # Read Bronze data
    bronze_df = read_bronze_data(spark)
    
    # Validate data quality - FAIL if issues found
    is_valid = validate_data_quality(bronze_df, spark)
    
    if not is_valid:
        print("\n✗ PIPELINE FAILED: Data quality validation errors detected!")
        print("Please investigate and fix the data quality issues in Bronze layer.")
        spark.stop()
        sys.exit(1)
    
    # Clean data
    silver_df = clean_data(bronze_df)
    
    # Write to Silver
    records_written = write_to_silver(silver_df, SILVER_PATH)
    
    print("\n" + "=" * 60)
    print("Silver Layer Processing Complete")
    print(f"Records processed: {records_written}")
    print("=" * 60)
    
    spark.stop()


if __name__ == "__main__":
    main()
