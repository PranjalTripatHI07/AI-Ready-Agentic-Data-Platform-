# AI-Ready Agentic Data Platform

End-to-end, open-source AI-ready data platform with real-time streaming, lakehouse modeling, ML pipelines, and an LLM-based analytics agent.

> **New here?** Check out the [Getting Started Guide](GETTING_STARTED.md) for a beginner-friendly, baby-step walkthrough to run this project from scratch.

---

## 🏗️ Architecture

```
┌──────────────────┐     ┌─────────┐     ┌──────────────────────────────────┐
│ Event Generator   │────▶│  Kafka  │────▶│ Spark Structured Streaming       │
│ (simulator/)      │     │ (Docker)│     │                                  │
└──────────────────┘     └─────────┘     │  Bronze ──▶ Silver ──▶ Gold      │
                                          │  (raw)     (clean)   (business)  │
                                          └──────┬───────┬───────┬──────────┘
                                                 │       │       │
                                          ┌──────▼───────▼───────▼──────────┐
                                          │       Delta Lake (local FS)      │
                                          │  /data/bronze  /silver  /gold    │
                                          └──────┬───────────────┬──────────┘
                                                 │               │
                                          ┌──────▼──────┐ ┌─────▼──────────┐
                                          │  Feature     │ │  AI Agent       │
                                          │  Engineering │ │  (Ollama LLM)   │
                                          └──────┬──────┘ │  + FAISS search  │
                                                 │        └────────────────┘
                                          ┌──────▼──────┐
                                          │  ML Model    │
                                          │  (sklearn)   │
                                          └─────────────┘
```

### Components

| Component | Location | Purpose |
|---|---|---|
| **Event Simulator** | `simulator/event_generator.py` | Generates random e-commerce events (view, cart, purchase) and streams them to Kafka |
| **Kafka + Zookeeper** | `docker-compose.yml` | Message broker for real-time event ingestion |
| **Bronze Layer** | `spark/bronze.py` | Spark Structured Streaming from Kafka → raw Delta Lake (no transformation) |
| **Silver Layer** | `spark/silver.py` | Reads Bronze, validates quality (fails on bad data), cleans, deduplicates |
| **Gold Layer** | `spark/gold.py` | Reads Silver, computes revenue/hour, active users/hour, conversion rate |
| **Feature Engineering** | `features/build_features.py` | PySpark pipeline creating per-user ML features |
| **ML Pipeline** | `ml/train_model.py` | Logistic regression model predicting purchase behavior |
| **AI Agent** | `agent/agent.py` | LLM-powered (Ollama + Mistral) natural language interface over Gold tables with FAISS semantic search |
| **Orchestration** | `airflow/pipeline_dag.py` | Airflow DAGs scheduling Silver → Gold → Features → ML training |

---

## 📂 Project Structure

```
agentic_data_platform/
├── simulator/
│   └── event_generator.py       # Kafka event producer
├── spark/
│   ├── bronze.py                # Raw ingestion (Kafka → Delta)
│   ├── silver.py                # Data cleaning & validation
│   └── gold.py                  # Business aggregations
├── features/
│   └── build_features.py        # ML feature engineering
├── ml/
│   └── train_model.py           # Model training & evaluation
├── agent/
│   └── agent.py                 # LLM agent with FAISS + Ollama
├── airflow/
│   └── pipeline_dag.py          # Airflow DAG definitions
├── data/                        # Delta Lake storage (auto-created)
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── features/
│   └── models/
├── docker-compose.yml           # Kafka + Zookeeper infrastructure
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 📋 Event Schema

```json
{
  "user_id": "int — unique user identifier (1-10000)",
  "product_id": "int — product identifier (1-5000)",
  "event_type": "string — one of: view, cart, purchase",
  "price": "float — 0.0 for view/cart, > 0 for purchase",
  "timestamp": "string — ISO-8601 format"
}
```

---

## 🚀 Step-by-Step Run Instructions

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Java 11+ (for Spark)
- Ollama installed locally (`curl -fsSL https://ollama.com/install.sh | sh`)

### 1. Install Python Dependencies

```bash
cd agentic_data_platform
pip install -r requirements.txt
```

### 2. Start Kafka & Zookeeper

```bash
docker-compose up -d
```

Wait for services to be healthy, then create the topic:

```bash
docker exec -it kafka kafka-topics --create \
  --topic ecommerce_events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

Verify the topic:

```bash
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

### 3. Start Event Generator

```bash
python simulator/event_generator.py
```

This produces ~1 event/second to the `ecommerce_events` Kafka topic.

### 4. Run Bronze Layer (Streaming Ingestion)

```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.1.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  spark/bronze.py
```

### 5. Run Silver Layer (Cleaning & Validation)

```bash
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 spark/silver.py
```

### 6. Run Gold Layer (Business Aggregations)

```bash
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 spark/gold.py
```

### 7. Run Feature Engineering

```bash
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 features/build_features.py
```

### 8. Train ML Model

```bash
python ml/train_model.py
```

### 9. Start AI Agent

```bash
ollama pull mistral
ollama serve   # In a separate terminal
python agent/agent.py
```

**Example interaction:**

```
🤖 Ask a question: What is the total revenue?
📊 Answer: Based on the revenue_per_hour table, the total revenue is $X across Y hours...

🤖 Ask a question: sql SELECT * FROM revenue_per_hour LIMIT 5
📊 SQL Result:
   hour_window  total_revenue  purchase_count  avg_order_value
0  2025-01-01          150.5              12            12.54
...
```

---

## 📊 Data Flow

1. **Event Generator** → Produces JSON events to Kafka topic `ecommerce_events` at 1 event/second
2. **Bronze Layer** → Spark reads Kafka stream, writes raw data to `data/bronze/ecommerce_events` as Delta Lake (no transformation, checkpointed)
3. **Silver Layer** → Reads Bronze Delta table, applies validation & cleaning:
   - Removes null `user_id` and `product_id`
   - Validates `event_type` ∈ {view, cart, purchase}
   - Removes duplicate events
   - Converts ISO-8601 timestamps
   - **Fails the job** if invalid data is detected (strict quality enforcement)
4. **Gold Layer** → Reads Silver, computes business metrics:
   - `revenue_per_hour` — Total revenue, purchase count, avg order value per hour window
   - `active_users_per_hour` — Distinct active users per hour window
   - `conversion_rate` — View→cart and cart→purchase conversion rates
5. **Feature Engineering** → Reads Silver, creates per-user ML features:
   - Purchase statistics (last 24h count, total count, avg order value)
   - Revenue metrics (total, avg, max, min per user)
   - Event frequency (events/hour, total activity span)
   - Conversion ratios (view→cart rate, cart→purchase rate)
6. **ML Pipeline** → Loads user features, trains a logistic regression model to predict purchasers, saves model + metrics
7. **AI Agent** → Loads Gold + feature tables into pandas, builds a FAISS vector store for semantic search, and uses Ollama (Mistral) to answer natural language questions via context-rich prompts

---

## 🤖 How the AI Agent Uses Data

The agent (`agent/agent.py`) provides an interactive natural language interface:

1. **Data Loading** — On startup, loads all Gold layer Delta tables and user features as pandas DataFrames
2. **FAISS Indexing** — Builds a FAISS vector store from table schemas, summary statistics, and sample data using Ollama embeddings for semantic similarity search
3. **Question Answering** — When a user asks a question:
   - Uses FAISS to retrieve the most relevant table context (if available)
   - Falls back to loading all data context if FAISS is unavailable
   - Builds a prompt with table schemas + data context + the user's question
   - Sends the prompt to Ollama (Mistral model) for natural language response
4. **Direct SQL** — Users can prefix queries with `sql ` to run SELECT/WHERE/ORDER BY/LIMIT queries directly against loaded DataFrames
5. **Graceful Fallback** — If Ollama is not running, returns raw data context so users can still explore their data

### Example Queries

- `"What is the total revenue?"` — Summarizes revenue_per_hour data
- `"Why did revenue drop in the last hour?"` — Analyzes trends in revenue data
- `"Which users are inactive?"` — Examines active_users_per_hour and feature data
- `"Show me the conversion rates"` — Returns conversion funnel metrics
- `sql SELECT * FROM revenue_per_hour ORDER BY total_revenue DESC LIMIT 5` — Direct data query

---

## ⚠️ Failure Handling

| Component | Failure Strategy |
|---|---|
| **Bronze Layer** | Kafka checkpointing ensures exactly-once semantics; `failOnDataLoss=false` provides resilience against topic compaction |
| **Silver Layer** | Strict data quality validation — pipeline **fails with `sys.exit(1)`** if null user_ids, invalid event types, null product_ids, negative prices, or zero-price purchases are found |
| **Gold Layer** | Spark's Delta Lake ACID transactions ensure consistent writes; partial failures don't corrupt data |
| **ML Pipeline** | Warns on missing features; handles insufficient data gracefully with informative messages |
| **AI Agent** | Falls back to raw data display if Ollama LLM is unavailable or errors; FAISS search falls back to full data context on failure |
| **Airflow** | Retries configured (2-3 per task); branch logic skips ML training if fewer than 100 samples exist |
| **Event Generator** | Kafka producer uses `acks='all'` for reliability with success/error callbacks for monitoring |

---

## 📈 Scaling Discussion

### Current Design (Local / Single Node)
The platform runs entirely on a single machine using local filesystem storage and Docker containers. This is ideal for development, prototyping, and small-scale analytics.

### Horizontal Scaling Strategies

- **Kafka** — Add partitions to the `ecommerce_events` topic and deploy multiple broker instances for higher throughput. Consumer groups enable parallel consumption.
- **Spark** — The current local-mode Spark can be replaced with a cluster (Standalone, YARN, or Kubernetes) by changing the master URL. Spark's distributed processing scales linearly with added executors.
- **Delta Lake** — Supports ACID transactions, time travel, schema evolution, and Z-ordering for query optimization. Can be backed by distributed storage (HDFS, S3) for larger datasets.
- **Airflow** — Switch from `SequentialExecutor` to `CeleryExecutor` or `KubernetesExecutor` for distributed task scheduling across multiple workers.
- **ML Pipeline** — Replace logistic regression with gradient boosting (XGBoost/LightGBM) or deep learning models. Add MLflow for experiment tracking, model versioning, and A/B testing.
- **AI Agent** — Swap Ollama for a hosted LLM API (OpenAI, Anthropic) for production use. Scale FAISS with IVF indices for millions of documents. Add a proper SQL engine (DuckDB, Trino) for complex analytical queries.
- **Storage** — Migrate from local filesystem to object storage (MinIO for on-prem, S3 for cloud) to handle terabyte-scale data volumes.

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Primary language |
| Docker & Docker Compose | Latest | Infrastructure orchestration |
| Apache Kafka | 7.5.0 (Confluent) | Real-time event streaming |
| Apache Spark | 3.5.0+ | Distributed data processing |
| Delta Lake | 3.1.0+ | ACID lakehouse storage |
| Apache Airflow | 2.8.0+ | Workflow orchestration |
| scikit-learn | 1.3.0+ | ML model training |
| Ollama | Latest | Local LLM serving |
| Mistral | Latest | LLM model for agent |
| LangChain | 0.1.0+ | LLM application framework |
| FAISS | 1.7.4+ | Vector similarity search |
