

<div align="center">
  
# InsightFlux AI (AI-Ready Agentic Data Platform)
  


![Platform Overview](agentic_data_platform/images/platform_overview.png)

**An intelligent, end-to-end data platform that processes e-commerce events in real-time, engineers features, trains ML models, and provides AI-powered insights through an interactive dashboard.**

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5.0-orange)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.1.0-green)](https://delta.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

Architecture • Quick Start • Features • Components • Usage

</div>

---

## 📋 Table of Contents

- Overview
- Architecture
- Key Features
- Technology Stack
- System Components
- Quick Start Guide
- Installation
- Running the Platform
- Using the Dashboard
- Using the AI Agent
- Data Flow
- Configuration
- API Reference
- Troubleshooting
- Contributing
- License

---

## 🎯 Overview

The **AI-Ready Agentic Data Platform** is a comprehensive, production-grade data engineering solution designed to process real-time e-commerce events with the power of Apache Spark, Delta Lake, and machine learning.

**What makes it special:**

✨ **Real-time streaming** from Kafka  
✨ **Multi-layer data architecture** (Bronze → Silver → Gold)  
✨ **Automated feature engineering** for ML  
✨ **Intelligent ML pipeline** with purchase prediction  
✨ **Interactive dashboard** with live analytics  
✨ **AI-powered assistant** that answers natural language queries  
✨ **Orchestrated workflows** with Apache Airflow  
✨ **Production-ready** with error handling and validation

---

## Architecture

### 🏗️ Data Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    E-commerce Events                        │
│                    (Kafka Streaming)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │    BRONZE LAYER (Raw Ingestion)    │
        │  ✓ Receives all events as-is       │
        │  ✓ No transformations              │
        │  ✓ Delta Lake storage              │
        └────────────┬───────────────────────┘
                     │ (Every 15 min)
                     ▼
        ┌────────────────────────────────────┐
        │   SILVER LAYER (Clean & Validate)  │
        │  ✓ Data quality checks             │
        │  ✓ Schema standardization          │
        │  ✓ Removes duplicates/nulls        │
        │  ✓ Type conversions                │
        └────────────┬───────────────────────┘
                     │ (Every 15 min)
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
    ┌────────────┐        ┌──────────────┐
    │   GOLD     │        │   FEATURES   │
    │ (Business  │        │ (ML Ready)   │
    │Aggregations)│       └──────┬───────┘
    └──────┬─────┘               │
           │                      ▼
           │              ┌──────────────────┐
           │              │  ML Training     │
           │              │  ✓ Purchase pred │
           │              │  ✓ Classification│
           │              └────────┬─────────┘
           │                       │
           └───────────┬───────────┘
                       ▼
        ┌──────────────────────────────────┐
        │  Dashboard & AI Agent            │
        │  ✓ Interactive analytics         │
        │  ✓ Natural language queries      │
        │  ✓ Real-time monitoring          │
        │  ✓ ML predictions                │
        └──────────────────────────────────┘
```

### Data Flow Diagram

![Data Flow](agentic_data_platform/images/data_flow.png)

---

## 🎨 Key Features

### 1. **Real-Time Data Streaming**
- Kafka event ingestion
- Continuous event generation (1 event/second)
- E-commerce event types: view, cart, purchase
- Real-time monitoring and alerts

### 2. **Multi-Layer Data Architecture**

| Layer | Purpose | Storage | Processing |
|-------|---------|---------|------------|
| **Bronze** | Raw ingestion | Delta Lake | No transformations |
| **Silver** | Cleaning & validation | Delta Lake | PySpark jobs |
| **Gold** | Business aggregations | Delta Lake | Spark SQL |
| **Features** | ML-ready vectors | Delta Lake | Feature engineering |

### 3. **Advanced Feature Engineering**
```python
Purchase Features:
  • Purchases in last 24 hours
  • Total purchases per user
  • Total revenue per user
  • Average/Min/Max order value

Event Features:
  • Total events viewed/carted
  • Unique products interacted
  • Activity span (hours)
  • Events per hour ratio

Conversion Features:
  • View-to-cart ratio
  • Cart-to-purchase ratio
  • Overall conversion rate

Temporal Features:
  • First activity timestamp
  • Last activity timestamp
  • Feature generation timestamp
```

### 4. **Machine Learning Pipeline**
- **Model Type**: Logistic Regression (Binary Classification)
- **Target**: Is Purchaser (1/0)
- **Metrics**: Accuracy, Precision, Recall, F1, ROC-AUC
- **Prediction**: Real-time purchase likelihood for users

### 5. **Interactive Dashboard**
- 8 comprehensive tabs covering all aspects
- Real-time KPI monitoring
- Advanced visualizations with Plotly
- Data exploration interface
- ML model performance tracking
- System health monitoring

### 6. **AI-Powered Assistant**
- Natural language query interface
- Automatic SQL generation
- Delta Lake table querying
- Intelligent context awareness
- Powered by Ollama LLM (TinyLlama)

### 7. **Workflow Orchestration**
- Apache Airflow DAGs
- Automated pipeline scheduling
- Dependency management
- Error handling and retries
- Data quality validation

---

## 🛠️ Technology Stack

### Data Engineering
- **Apache Spark 3.5.0** - Distributed data processing
- **Delta Lake 3.1.0** - ACID transactions, data versioning
- **Apache Kafka** - Event streaming
- **PySpark** - Spark programming interface

### Storage & Formats
- **Parquet** - Columnar storage format
- **Delta Format** - Transactional data lake format
- **Local File System** - Data persistence

### Machine Learning
- **Scikit-learn** - ML algorithms
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Joblib** - Model serialization

### Orchestration & Scheduling
- **Apache Airflow** - Workflow orchestration
- **Python APScheduler** - Task scheduling

### AI & LLMs
- **Ollama** - Local LLM serving
- **TinyLlama** - Lightweight language model
- **LangChain** - LLM framework

### Frontend & Visualization
- **Streamlit** - Interactive web dashboard
- **Plotly** - Interactive visualizations
- **Pandas** - Data display

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Ubuntu 24.04 LTS** - Operating system
- **Python 3.9+** - Programming language

---

## System Components

### 1. **Event Simulator** (event_generator.py)
```
Purpose: Generates realistic e-commerce events
Output:  Sends to Kafka topic "ecommerce_events"
Format:  {user_id, product_id, event_type, price, timestamp}
Rate:    1 event per second
Events:  70% views, 20% carts, 10% purchases
```

**Key Functions:**
```python
generate_event()          # Create single event
create_kafka_producer()   # Setup Kafka connection
main()                    # Event generation loop
```

### 2. **Bronze Layer** (bronze.py)
```
Purpose: Raw data ingestion from Kafka
Input:   Kafka stream (ecommerce_events)
Output:  /data/bronze/ecommerce_events (Delta)
Process: Stream → Parse JSON → Delta Lake
```

**Key Functions:**
```python
create_spark_session()    # Setup Spark with Delta
read_kafka_stream()       # Connect to Kafka
parse_events()            # JSON parsing
write_to_delta()          # Stream to Delta
```

### 3. **Silver Layer** (silver.py)
```
Purpose: Data cleaning and validation
Input:   /data/bronze/ecommerce_events
Output:  /data/silver/ecommerce_events
Process: Validate → Clean → Transform → Delta
```

**Data Quality Rules:**
- ✓ Check for null values
- ✓ Validate data types
- ✓ Verify event types (view/cart/purchase)
- ✓ Ensure positive prices
- ✓ Timestamp validation
- ✗ FAIL pipeline on validation errors

**Key Functions:**
```python
read_bronze_data()        # Read raw data
validate_data_quality()   # Quality checks
clean_data()              # Cleaning transformations
write_to_silver()         # Persist cleaned data
```

### 4. **Gold Layer** (gold.py)
```
Purpose: Business aggregations
Input:   /data/silver/ecommerce_events
Output:  3 business tables
         - revenue_per_hour
         - active_users_per_hour
         - conversion_rate
```

**Aggregations:**
```python
calculate_revenue_per_hour()      # Hourly revenue metrics
calculate_active_users_per_hour() # Hourly user activity
calculate_conversion_rate()       # Funnel conversion metrics
```

### 5. **Feature Engineering** (build_features.py)
```
Purpose: Create ML-ready feature vectors
Input:   /data/silver/ecommerce_events
Output:  /data/features/user_features
Process: Aggregate → Calculate → Engineer → Delta
```

**Feature Groups:**
- Purchase features (6 features)
- Event features (6 features)
- Conversion features (3 features)
- Metadata (4 features)
- Target variable (1 feature)

### 6. **ML Training** (train_model.py)
```
Purpose: Train purchase prediction model
Input:   /data/features/user_features
Output:  Model artifacts in /data/models/
Process: Load → Prepare → Train → Evaluate → Save
```

**Model Pipeline:**
```
Load Features → Handle Missing Values → Scale Features
                                          ↓
                        Train/Test Split (80/20)
                                          ↓
              Logistic Regression Training
                                          ↓
                    Model Evaluation & Metrics
                                          ↓
                 Save: model.pkl, scaler.pkl
```

### 7. **AI Agent** (agent.py)
```
Purpose: Natural language query interface
Input:   User questions + SQL commands
Output:  Results from Gold & Feature tables
LLM:     TinyLlama via Ollama
```

**Components:**
- `DataQueryEngine`: Loads and queries Delta tables
- `AIAgent`: LLM-powered query generation
- `run_interactive_session()`: User interaction loop

### 8. **Dashboard** (dashboard.py)
```
Purpose: Interactive analytics interface
Framework: Streamlit
Tabs:     8 comprehensive data exploration tabs
Updates:  Real-time with caching (TTL: 120-300s)
```

**Dashboard Tabs:**
1. **Overview** - KPIs from Gold layer
2. **Business Analytics** - Detailed Silver layer breakdowns
3. **AI Assistant** - Chat with your data
4. **Data Explorer** - Browse all layers
5. **ML & Predictions** - Model performance & live inference
6. **Streaming Monitor** - Real-time Bronze layer activity
7. **Pipeline Status** - Layer freshness & health
8. **System Health** - Infrastructure checks

### 9. **Airflow Orchestration** (pipeline_dag.py)
```
Purpose: Automated workflow scheduling
Schedule: Every 15 minutes (data), hourly (features), daily (ML)
Tasks:    Silver → Gold → Features → ML → Validation
```

---

## Quick Start Guide

### ⚡ 5-Minute Setup

**Prerequisites:**
- Docker & Docker Compose
- Python 3.9+
- 8GB+ RAM
- 10GB+ disk space

```bash
# 1. Clone repository
git clone <repository-url>
cd agentic_data_platform

# 2. Start infrastructure
docker-compose up -d

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the data pipeline
bash scripts/start_pipeline.sh

# 5. Open dashboard
streamlit run ui/dashboard.py
```

**Dashboard will be available at:** `http://localhost:8501`

---

## Installation

### Step 1: System Requirements

```bash
# Check Python version
python --version  # Should be 3.9+

# Check Docker
docker --version
docker-compose --version

# Check Java (required for Spark)
java -version  # Should be Java 17+
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/PranjalTripatHI07/AI-Ready-Agentic-Data-Platform-.git
cd agentic_data_platform
```

### Step 3: Start Infrastructure

```bash
# Start Kafka, Zookeeper, and other services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
```
pyspark==3.5.0
delta-spark==3.1.0
kafka-python==2.0.2
pandas==2.1.0
scikit-learn==1.3.0
streamlit==1.28.0
plotly==5.17.0
langchain==0.1.0
langchain-ollama==0.1.0
joblib==1.3.0
requests==2.31.0
```

### Step 6: Verify Installation

```bash
# Check Spark installation
spark-shell --version

# Test Kafka connection
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Test Python packages
python -c "import pyspark; print(pyspark.__version__)"
```

---

## Running the Platform

### Option 1: Complete Automated Setup

```bash
# Start all components in sequence
bash scripts/start_all.sh
```

### Option 2: Manual Step-by-Step

#### Terminal 1: Start Event Generator
```bash
python simulator/event_generator.py
```

**Output:**
```
============================================================
E-commerce Event Generator (Kafka Mode)
Topic: ecommerce_events
Bootstrap Servers: localhost:9092
Generating 1 event per second...
Press Ctrl+C to stop
============================================================
[Event #1] Sent: view | user: 4521 | product: 234 | price: $0.00
[Event #2] Sent: purchase | user: 7823 | product: 1245 | price: $234.56
...
```

#### Terminal 2: Start Bronze Layer
```bash
spark-submit --packages io.delta:delta-spark_2.12:3.1.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  spark/bronze.py
```

**Output:**
```
============================================================
Bronze Layer - Raw Data Ingestion
============================================================
Kafka Bootstrap Servers: localhost:9092
Kafka Topic: ecommerce_events
Bronze Path: /path/to/data/bronze/ecommerce_events
Checkpoint Path: /path/to/data/checkpoints/bronze
============================================================
✓ Spark session created
✓ Kafka stream connected
✓ Event parsing configured
✓ Delta Lake writer started

Streaming query running... Press Ctrl+C to stop
```

#### Terminal 3: Setup Ollama LLM
```bash
# Pull the model (first time only)
ollama pull mistral

# Start Ollama server
ollama serve
```

**Output:**
```
time=2024-01-15T10:30:45.123Z level=INFO msg="Listening on 127.0.0.1:11434 (version 0.0.1)"
```

#### Terminal 4: Run Data Pipelines (after ~1 minute)

```bash
# Run Silver layer (after Bronze collects some data)
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 \
  spark/silver.py
```

```bash
# Run Gold layer
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 \
  spark/gold.py
```

```bash
# Run Feature engineering
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 \
  features/build_features.py
```

```bash
# Run ML training
python ml/train_model.py
```

#### Terminal 5: Start AI Agent (Optional)
```bash
python agent/agent.py
```

**Interactive Session:**
```
============================================================
🤖 E-commerce AI Data Agent
============================================================
Ask questions about your e-commerce data in natural language.
Commands: 'quit' to exit, 'sql <query>' for direct SQL
============================================================

Example questions:
  • What is the total revenue?
  • Show me the conversion rates
  • How many active users do we have?
  • sql SELECT * FROM revenue_per_hour

🤖 Ask a question: What is the total revenue?
```

#### Terminal 6: Launch Dashboard
```bash
streamlit run ui/dashboard.py
```

**Dashboard URL:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

---

## Using the Dashboard

### 📊 Tab 0: Overview
**Real-time KPIs from Gold layer**

- **Total Revenue**: Sum of all purchases
- **Active Users**: Unique users in time period
- **Conversion Rate**: Purchase/View ratio
- **Avg Order Value**: Average purchase amount

**Visualizations:**
- Revenue trend (time series)
- Active users per hour (bar chart)
- Conversion rate metrics (gauge)

### 📈 Tab 1: Business Analytics
**Detailed breakdowns from Silver & Gold layers**

- Revenue by product (top 15)
- Event type distribution (pie chart)
- Top users by revenue
- Hourly activity patterns

**Filters:**
- Date range selection
- Event type filtering
- User segments

### 🤖 Tab 2: AI Assistant
**Chat with your data using natural language**

**Example Questions:**
```
✓ "What is the total revenue?"
✓ "Show me conversion rates by hour"
✓ "How many active users do we have?"
✓ "Which products generate most revenue?"
✓ "sql SELECT * FROM revenue_per_hour LIMIT 10"
```

**Features:**
- Chat history
- Auto-generated SQL display
- Result data table
- Chart visualization

### 🔍 Tab 3: Data Explorer
**Browse any layer of the lakehouse**

**Available Tables:**
- Bronze Layer (raw events)
- Silver Layer (cleaned events)
- Gold - Revenue per Hour
- Gold - Active Users per Hour
- Gold - Conversion Rate
- Feature Table (user_features)

**Actions:**
- View table schema
- Browse data preview
- Summary statistics
- Auto chart generation

### 🧠 Tab 4: ML & Predictions
**Model performance and live inference**

**Performance Metrics:**
- Accuracy gauge
- Precision gauge
- Recall gauge
- F1 Score gauge
- ROC AUC score
- Confusion matrix
- Feature importance bar chart

**Live Prediction:**
```
Enter user_id: 42
→ Model predicts: Likely Purchaser
→ Confidence: 87.3%
```

### ⚡ Tab 5: Streaming Monitor
**Real-time events from Bronze layer**

**KPIs:**
- Total events ingested
- Unique users today
- Event types count
- Events per minute throughput

**Visualizations:**
- Event throughput trend
- Event type distribution
- Latest event feed

### 🔧 Tab 6: Pipeline Status
**Data layer freshness and health**

**Layers Monitored:**
- ✓ Bronze Layer
- ✓ Silver Layer
- ✓ Gold Layer
- ✓ Feature Table
- ✓ ML Model Artifacts

**Status Indicators:**
- Available (data exists)
- Missing (no data)
- Last modified timestamp

### 🏥 Tab 7: System Health
**Infrastructure component checks**

**Services Checked:**
- ✓ Kafka Broker (port 9092)
- ✓ Spark Session
- ✓ Ollama LLM (port 11434)
- ✓ Airflow Scheduler (port 8793)
- ✓ Delta Lake library

**Status:**
-  Running
-  Not detected
-  Not reachable

---

## Using the AI Agent

### Terminal Interface

```bash
python agent/agent.py
```

### Available Commands

```bash
# Natural language questions
🤖 Ask a question: What is my total revenue?
→ AI generates SQL → Queries Gold tables → Returns results

# Direct SQL queries
🤖 Ask a question: sql SELECT * FROM revenue_per_hour LIMIT 5
→ Executes SQL directly → Returns DataFrame

# Schema information
🤖 Ask a question: describe
🤖 Ask a question: show tables
→ Lists all available tables and columns

# Exit session
🤖 Ask a question: quit
```

### Example Interactions

```
🤖 Ask a question: What is the conversion rate by hour?

SQL Generated:
SELECT hour, overall_conversion_rate 
FROM conversion_rate 
ORDER BY hour DESC

Result:
                    hour overall_conversion_rate
0 2024-01-15 18:00:00                     0.145
1 2024-01-15 17:00:00                     0.132
2 2024-01-15 16:00:00                     0.156
...

Explanation: The conversion rate varies between 13-16% across hours,
with peak performance in the afternoon...
```

---

## Data Flow

### Complete Pipeline Flow

```
E-commerce Events (Kafka)
         ↓
    [BRONZE LAYER]
    Raw Ingestion (Delta)
         ↓
    [SILVER LAYER]
    Clean & Validate
         ↓
    ┌─────────────────────────┬─────────────────────────┐
    ↓                         ↓                         ↓
[GOLD LAYER]          [FEATURE ENGINEERING]      [DASHBOARD]
Revenue/Users/Conv    User Purchase Features     Real-time KPIs
         │                     │                         │
         ├─────────────────────┴─────────────────────────┤
         │                                               │
         ▼                                               ▼
    [ML TRAINING]                                 [AI ASSISTANT]
    Purchase Predictor                            Natural Language
         │                                               │
         └────────────────┬──────────────────────────────┘
                          ▼
                    USER INTERFACE
                    Dashboard + Chat
```

### Timing & Scheduling

```
Real-time (Continuous):
├─ Event Generation: 1 event/second
└─ Bronze Ingestion: Streaming

Every 15 minutes:
├─ Silver Layer: Clean & validate
└─ Gold Layer: Aggregate metrics

Every hour:
└─ Feature Engineering: Create ML features

Every day:
└─ ML Training: Retrain purchase predictor

On-Demand:
├─ AI Agent: Query anytime
└─ Dashboard: View anytime
```

---

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=ecommerce_events

# Spark Configuration
SPARK_HOME=/opt/spark
SPARK_MASTER=local[*]

# Paths
DATA_DIR=/path/to/data
BRONZE_PATH=/path/to/data/bronze/ecommerce_events
SILVER_PATH=/path/to/data/silver/ecommerce_events
GOLD_PATH=/path/to/data/gold

# LLM Configuration
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434

# Streamlit
STREAMLIT_LOGGER_LEVEL=info
STREAMLIT_CLIENT_SHOWERRORDETAILS=true
```

### Spark Configuration

**Memory Allocation:**
```python
# For large datasets, increase memory
spark-submit \
  --driver-memory 4g \
  --executor-memory 4g \
  script.py
```

**Partitioning:**
```python
# Adjust for your cluster
df.repartition(8)  # 8 partitions
```

### Event Generator Tuning

```python
# In simulator/event_generator.py
EVENT_TYPES = ["view", "cart", "purchase"]
EVENT_WEIGHTS = [0.7, 0.2, 0.1]      # Adjust ratios
USER_ID_RANGE = (1, 10000)            # User pool
PRODUCT_ID_RANGE = (1, 5000)          # Product catalog
PRICE_MIN = 5.0
PRICE_MAX = 500.0
# Events per second: modify time.sleep(1)
```

---

## API Reference

### DataQueryEngine Class

```python
from agent.agent import DataQueryEngine

# Initialize
engine = DataQueryEngine()

# Get table schemas
schemas = engine.get_table_schemas()

# Execute query
result = engine.execute_query("SELECT * FROM revenue_per_hour LIMIT 10")

# Get summary stats
stats = engine.get_summary_stats("user_features")

# Get data context for LLM
context = engine.get_data_context()
```

### AIAgent Class

```python
from agent.agent import AIAgent, DataQueryEngine

# Initialize
engine = DataQueryEngine()
agent = AIAgent(engine)

# Ask a question
response = agent.answer_question("What is the total revenue?")

# Get context
context = agent.get_data_context()
```

### Dashboard Functions

```python
# Load Delta tables
from ui.dashboard import load_delta_table, get_gold_table

table = get_gold_table("revenue_per_hour")
features = load_delta_table(FEATURES_PATH)
```

---

## Troubleshooting

### Common Issues & Solutions

#### 1. **Kafka Connection Failed**

```
Error: Failed to connect to Kafka: localhost:9092
```

**Solution:**
```bash
# Check Kafka container
docker-compose ps

# Verify Kafka is running
docker logs kafka

# Restart Kafka
docker-compose down
docker-compose up -d kafka zookeeper
```

#### 2. **Spark OutOfMemory Error**

```
Error: java.lang.OutOfMemoryError: Java heap space
```

**Solution:**
```bash
# Increase Spark memory
spark-submit --driver-memory 4g --executor-memory 4g script.py

# Reduce partition size
df.coalesce(4)
```

#### 3. **Delta Lake Read Error**

```
Error: Failed to read Delta table: path/not/exists
```

**Solution:**
```bash
# Ensure paths exist
ls -la data/bronze/ecommerce_events/

# Fix permissions
chmod -R 755 data/

# Regenerate data
python simulator/event_generator.py
spark-submit spark/bronze.py
```

#### 4. **LLM Response Slow**

```
Error: Ollama server timeout
```

**Solution:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Use smaller model
# In agent.py: OLLAMA_MODEL = "TinyLlama"
```

#### 5. **Dashboard Not Loading**

```
Error: streamlit.StreamlitAPIException
```

**Solution:**
```bash
# Clear cache
rm -rf ~/.streamlit/

# Kill Port 8501
lsof -i :8501 | awk 'NR!=1 {print $2}' | xargs kill -9

# Restart dashboard
streamlit run ui/dashboard.py --logger.level=debug
```

#### 6. **Airflow DAG Not Running**

```
Error: Failed to import DAG from pipeline_dag.py
```

**Solution:**
```bash
# Check Airflow logs
airflow dags test ecommerce_data_pipeline 2024-01-15

# Validate DAG syntax
python airflow/pipeline_dag.py

# Restart Airflow
airflow webserver
airflow scheduler
```

### Debug Mode

Enable detailed logging:

```python
# In any Python script
import logging
logging.basicConfig(level=logging.DEBUG)

# In Spark
spark.sparkContext.setLogLevel("DEBUG")

# In Streamlit
streamlit run ui/dashboard.py --logger.level=debug
```

### Health Check Script

```bash
#!/bin/bash
echo "🔍 Platform Health Check"
echo "========================"

# Check services
echo "Kafka: $(curl -s localhost:9092 | head -c 1 && echo 'OK' || echo 'FAIL')"
echo "Postgres: $(curl -s localhost:5432 | head -c 1 && echo 'OK' || echo 'FAIL')"
echo "Ollama: $(curl -s http://localhost:11434 | head -c 1 && echo 'OK' || echo 'FAIL')"
echo "Spark: $(spark-shell --version 2>&1 | grep -q 'version' && echo 'OK' || echo 'FAIL')"

# Check data paths
echo "Data directories:"
du -sh data/*/
```

---

## Contributing

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/PranjalTripatHI07/AI-Ready-Agentic-Data-Platform-.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   ```bash
   # Edit files
   git add .
   git commit -m "Feature: Description of your changes"
   ```

4. **Push the branch**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Describe your changes
   - Reference any related issues
   - Include test results

### Development Guidelines

- ✅ Follow PEP 8 style guide
- ✅ Add docstrings to all functions
- ✅ Include error handling
- ✅ Write unit tests for new features
- ✅ Update README documentation
- ✅ Test on local environment first

### Code Style

```python
# Good example
def calculate_conversion_rate(purchases: pd.DataFrame, views: pd.DataFrame) -> float:
    """
    Calculate conversion rate from views to purchases.
    
    Args:
        purchases: DataFrame with purchase events
        views: DataFrame with view events
        
    Returns:
        float: Conversion rate (0-1)
    """
    if len(views) == 0:
        return 0.0
    return len(purchases) / len(views)
```

---

## Performance Tuning

### Spark Optimization

```python
# Enable adaptive query execution
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# Optimize for small tables
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100MB")

# Cache frequently used DataFrames
df.cache()
```

### Kafka Optimization

```python
# Increase consumer threads
spark.readStream.option("kafka.consumer.max.poll.records", "500")

# Enable compression
spark.readStream.option("kafka.compress.codec", "snappy")
```

### Memory Management

```bash
# Monitor Spark memory
spark.sparkContext.getConf().get("spark.driver.memory")

# Adjust executors
--executor-cores 4 --num-executors 8
```

---

## Monitoring & Logging

### Spark UI

Access Spark jobs in real-time:
- **URL**: `http://localhost:4040`
- **Tabs**: 
  - Jobs
  - Stages
  - Tasks
  - Storage (cached DataFrames)
  - SQL

### Logs Directory

```bash
# Check application logs
tail -f logs/spark_*.log

# Check pipeline logs
tail -f logs/silver_layer.log
tail -f logs/gold_layer.log
tail -f logs/ml_training.log
```

### Metrics & Alerts

```python
# Log metrics
print(f"Processed: {record_count} records")
print(f"Time taken: {elapsed_time} seconds")
print(f"Throughput: {record_count/elapsed_time} records/sec")
```

---

## FAQ

**Q: How do I reset the data?**
```bash
rm -rf data/
python simulator/event_generator.py
# Run pipelines again
```

**Q: Can I use a different LLM?**
```python
# In agent.py, change:
OLLAMA_MODEL = "neural-chat"  # or any available Ollama model
```

**Q: How do I scale this to production?**
- Deploy Kafka cluster
- Use standalone Spark cluster
- Setup Postgres for Airflow
- Deploy Streamlit with Gunicorn
- Add monitoring (Prometheus, Grafana)

**Q: What's the data volume limit?**
- Bronze: Limited by Kafka retention
- Silver/Gold: Limited by disk space
- Feature Table: Typical 100K-1M user records

**Q: Can I add more features?**
```python
# Edit features/build_features.py
def calculate_custom_features(df, spark):
    # Your feature logic here
    return custom_features_df
```

---

## Project Structure

```
agentic_data_platform/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # Service containers
│
├── simulator/
│   └── event_generator.py            # Kafka event producer
│
├── spark/
│   ├── bronze.py                     # Raw ingestion layer
│   ├── silver.py                     # Cleaning & validation
│   └── gold.py                       # Business aggregations
│
├── features/
│   └── build_features.py             # Feature engineering
│
├── ml/
│   └── train_model.py                # ML training pipeline
│
├── agent/
│   └── agent.py                      # AI data agent
│
├── ui/
│   └── dashboard.py                  # Streamlit dashboard
│
├── airflow/
│   └── pipeline_dag.py               # Workflow orchestration
│
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── features/
│   ├── models/
│   └── checkpoints/
│
├── images/                           # Documentation images
│   └── [Platform overview, diagrams, etc]
│
└── scripts/
    ├── start_all.sh                  # Automated startup
    └── health_check.sh               # Diagnostics
```

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

**MIT License Summary:**
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute copies
- ✅ Private use
- ⚠️ Include license notice
- ⚠️ No liability provided

---

## Acknowledgments

This platform was built as a demonstration of modern data engineering techniques combining:
- **Stream Processing**: Kafka + Spark
- **Data Lakehouses**: Delta Lake
- **Machine Learning**: Scikit-learn
- **AI/LLMs**: Ollama + TinyLlama
- **Analytics**: Streamlit + Plotly
- **Orchestration**: Apache Airflow



---

## Contact & Support

**Author:** PranjalTripatHI07

### Filing Issues
- Report bugs on GitHub Issues
- Include logs and error messages
- Describe steps to reproduce

### Discussion & Questions
- Open GitHub Discussions
- Ask in Issues section
- Check FAQ above

### Getting Help
```bash
# Get help on any component
python component.py --help

# Check logs
tail -f logs/*.log

# Run diagnostics
bash scripts/health_check.sh
```

---

<div align="center">

### ⭐ If you found this helpful, please star the repository!

 **Built by PranjalTripatHI07 for the data engineering community**

Back to Top

</div>
