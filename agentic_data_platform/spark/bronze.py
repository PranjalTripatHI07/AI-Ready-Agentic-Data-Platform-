#!/usr/bin/env python3
"""
Bronze Layer - Raw Data Ingestion
Reads streaming data from Kafka and writes raw data to Delta Lake.
NO filtering, NO cleaning - stores everything as-it is.
"""


# # SparkSession is the entry point to Spark.
# It starts the Spark engine and lets us read, process, and write data using DataFrames.
from pyspark.sql import SparkSession  


# Used to parse JSON strings into structured columns
# col()	-> Refer to DataFrame columns safely
# from_json() ->	Convert JSON string → structured columns
from pyspark.sql.functions import col, from_json # Used to parse JSON strings into structured columns



# here We are telling Spark what columns exist and what type of data each column holds.
# all below are spark built - in classes which is used to define schema for our data
# StructType → represents the whole schema (table structure) 

# StructField → represents one column

# IntegerType → integer values (e.g. user_id)

# StringType → text values (e.g. event_type)

# DoubleType → decimal numbers (e.g. price)

from pyspark.sql.types import ( 
    StructType, StructField, IntegerType, StringType, DoubleType
)





# Kafka Configuration 
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "ecommerce_events"


# Here we are defining the paths for bronze data storage and Spark checkpointing
import os # importing os module To handle file paths
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Get the base directory of the project
BRONZE_PATH = os.path.join(BASE_PATH, "data/bronze/ecommerce_events") # Path to store raw bronze data
CHECKPOINT_PATH = os.path.join(BASE_PATH, "data/checkpoints/bronze") # Path for Spark checkpointing


# Here We are telling Spark what fields exist in the JSON event and what type of data each field contains.
# Event Schema matching the generator 
EVENT_SCHEMA = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])


def create_spark_session() -> SparkSession:
    """
    Create and configure Spark session with Delta Lake and Kafka support.
    """
    spark = SparkSession.builder \
        .appName("Bronze_Layer_Ingestion") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "io.delta:delta-spark_2.12:3.1.0") \
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_PATH) \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_kafka_stream(spark: SparkSession):
    """
    Read streaming data from Kafka topic.
    """
    print(f"Reading from Kafka topic: {KAFKA_TOPIC}")
    
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    return kafka_df


def parse_events(kafka_df):
    """
    Parse JSON events from Kafka messages.
    Keeps raw data - no filtering or cleaning.
    """
    # Convert binary value to string and parse JSON
    parsed_df = kafka_df \
        .selectExpr("CAST(key AS STRING) as kafka_key",
                    "CAST(value AS STRING) as json_value",
                    "topic",
                    "partition",
                    "offset",
                    "timestamp as kafka_timestamp") \
        .select(
            col("kafka_key"),
            from_json(col("json_value"), EVENT_SCHEMA).alias("event"),
            col("topic"),
            col("partition"),
            col("offset"),
            col("kafka_timestamp")
        ) \
        .select(
            col("kafka_key"),
            col("event.user_id").alias("user_id"),
            col("event.product_id").alias("product_id"),
            col("event.event_type").alias("event_type"),
            col("event.price").alias("price"),
            col("event.timestamp").alias("event_timestamp"),
            col("topic"),
            col("partition"),
            col("offset"),
            col("kafka_timestamp")
        )
    
    return parsed_df


def write_to_delta(df, output_path: str, checkpoint_path: str):
    """
    Write streaming data to Delta Lake with checkpointing.
    """
    print(f"Writing to Delta Lake: {output_path}")
    print(f"Checkpoint location: {checkpoint_path}")
    
    query = df.writeStream \
        .format("delta") \
        .outputMode("append") \
        .option("checkpointLocation", checkpoint_path) \
        .option("mergeSchema", "true") \
        .start(output_path)
    
    return query


def main():
    """
    Main function to run the Bronze layer ingestion pipeline.
    """
    print("=" * 60)
    print("Bronze Layer - Raw Data Ingestion")
    print("=" * 60)
    print(f"Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Kafka Topic: {KAFKA_TOPIC}")
    print(f"Bronze Path: {BRONZE_PATH}")
    print(f"Checkpoint Path: {CHECKPOINT_PATH}")
    print("=" * 60)
    
    # Create Spark session
    spark = create_spark_session()
    print("✓ Spark session created")
    
    # Read from Kafka
    kafka_df = read_kafka_stream(spark)
    print("✓ Kafka stream connected")
    
    # Parse events
    parsed_df = parse_events(kafka_df)
    print("✓ Event parsing configured")
    
    # Write to Delta Lake
    query = write_to_delta(parsed_df, BRONZE_PATH, CHECKPOINT_PATH)
    print("✓ Delta Lake writer started")
    
    print("\nStreaming query running... Press Ctrl+C to stop")
    
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nStopping streaming query...")
        query.stop()
        spark.stop()
        print("Bronze layer ingestion stopped.")


if __name__ == "__main__":
    main()
