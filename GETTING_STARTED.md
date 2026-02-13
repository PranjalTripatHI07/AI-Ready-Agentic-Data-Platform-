# 🚀 Getting Started: Baby-Step Guide

A complete beginner-friendly walkthrough to get the **AI-Ready Agentic Data Platform** running on your machine. Each step includes exactly what to type, what you should see, and how to verify it worked.

---

## 📖 What Does This Project Do? (Plain English)

Imagine an online store that tracks every time a customer:
- **Views** a product page
- **Adds** a product to their shopping cart
- **Purchases** a product

This platform:
1. **Generates** fake e-commerce events (simulating real customers)
2. **Streams** them through Kafka (a message broker — think of it like a post office for data)
3. **Processes** the data in three layers using Apache Spark:
   - **Bronze** — raw data, exactly as received
   - **Silver** — cleaned and validated data
   - **Gold** — business metrics (revenue, active users, conversion rates)
4. **Builds ML features** from the cleaned data
5. **Trains a model** that predicts which users are likely to buy
6. **Runs an AI agent** that lets you ask questions about the data in plain English

```
You (fake events) → Kafka → Bronze → Silver → Gold → ML Model / AI Agent
```

---

## 🧰 Step 0: Install Prerequisites

Before anything else, make sure these tools are installed on your machine.

### 0.1 — Python 3.10+

Check if you already have it:

```bash
python3 --version
```

✅ **Expected output:** `Python 3.10.x` (or higher)

If not installed:
- **macOS:** `brew install python@3.12`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install python3 python3-pip python3-venv`
- **Windows:** Download from [python.org](https://www.python.org/downloads/) and check "Add to PATH" during install

### 0.2 — Java 11+

Spark needs Java to run. Check:

```bash
java -version
```

✅ **Expected output:** Something like `openjdk version "11.0.x"` or `"17.0.x"`

If not installed:
- **macOS:** `brew install openjdk@17`
- **Ubuntu/Debian:** `sudo apt install openjdk-17-jdk`
- **Windows:** Download from [Adoptium](https://adoptium.net/)

### 0.3 — Docker & Docker Compose

Kafka and Zookeeper run inside Docker containers. Check:

```bash
docker --version
docker compose version
```

✅ **Expected output:** `Docker version 24.x.x` (or higher) and `Docker Compose version v2.x.x`

If not installed:
- **All platforms:** Follow [Docker Desktop install guide](https://docs.docker.com/get-docker/)
- Make sure Docker Desktop is **running** (you should see the whale icon in your system tray)

### 0.4 — Ollama (for the AI Agent — optional)

Ollama lets you run AI language models locally. Check:

```bash
ollama --version
```

If not installed:
- **macOS/Linux:** `curl -fsSL https://ollama.com/install.sh | sh`
- **Windows:** Download from [ollama.com](https://ollama.com/)

> 💡 **Tip:** Ollama is only needed for Step 9 (the AI Agent). You can skip it and still run everything else.

---

## 📂 Step 1: Clone the Repository

```bash
git clone https://github.com/PranjalTripatHI07/AI-Ready-Agentic-Data-Platform-.git
cd AI-Ready-Agentic-Data-Platform-
```

✅ **Verify:** You should see files like `README.md`, `LICENSE`, and a folder called `agentic_data_platform/`.

```bash
ls
```

Expected output:
```
GETTING_STARTED.md  LICENSE  README.md  agentic_data_platform
```

---

## 📦 Step 2: Install Python Dependencies

Navigate into the project folder and install all required packages:

```bash
cd agentic_data_platform
pip install -r requirements.txt
```

> 💡 **Tip:** It is a good practice to use a virtual environment to avoid conflicts:
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate    # On macOS/Linux
> # .venv\Scripts\activate     # On Windows
> pip install -r requirements.txt
> ```

✅ **Verify:** The install completes without errors. You can double-check:

```bash
python3 -c "import pyspark; import kafka; print('All good!')"
```

Expected output:
```
All good!
```

---

## 🐳 Step 3: Start Kafka & Zookeeper (Docker)

From the `agentic_data_platform/` directory, start the infrastructure:

```bash
docker compose up -d
```

This starts three services in the background:
| Service | What it does | Port |
|---|---|---|
| **Zookeeper** | Coordinates Kafka | 2181 |
| **Kafka** | Message broker for streaming events | 9092 |
| **Kafka-UI** | Web dashboard to inspect Kafka topics | 8080 |

✅ **Verify:** Check that all three containers are running:

```bash
docker compose ps
```

Expected output (all should show `Up` or `running`):
```
NAME         IMAGE                              STATUS
kafka        confluentinc/cp-kafka:7.5.0        Up (healthy)
kafka-ui     provectuslabs/kafka-ui:latest      Up
zookeeper    confluentinc/cp-zookeeper:7.5.0    Up (healthy)
```

> ⏳ **Wait 15–30 seconds** for Kafka to fully start and become healthy before proceeding.

### 3.1 — Create the Kafka Topic

Now create the topic that will hold our e-commerce events:

```bash
docker exec -it kafka kafka-topics --create \
  --topic ecommerce_events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

✅ **Expected output:**
```
Created topic ecommerce_events.
```

### 3.2 — Verify the Topic Exists

```bash
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

✅ **Expected output** (should include):
```
ecommerce_events
```

### 3.3 — (Optional) Open Kafka UI

Open your browser and go to **http://localhost:8080**. You should see a Kafka dashboard showing your cluster and the `ecommerce_events` topic.

---

## 📡 Step 4: Start the Event Generator

Open a **new terminal window** (keep it running), navigate to the project, and start generating events:

```bash
cd AI-Ready-Agentic-Data-Platform-/agentic_data_platform
python simulator/event_generator.py
```

✅ **Expected output** (events stream continuously, ~1 per second):
```
============================================================
E-commerce Event Generator (Kafka Mode)
Topic: ecommerce_events
Bootstrap Servers: localhost:9092
Generating 1 event per second...
Press Ctrl+C to stop
============================================================
✓ Connected to Kafka at localhost:9092
[Event #1] Sent: view | user: 4521 | product: 1203 | price: $0.00
[Event #2] Sent: view | user: 8832 | product: 4010 | price: $0.00
[Event #3] Sent: purchase | user: 1547 | product: 2999 | price: $149.99
[Event #4] Sent: cart | user: 6621 | product: 890 | price: $0.00
...
```

> 💡 **Let it run for 2–3 minutes** to generate enough events for the next steps. You can leave this running and continue in a **separate terminal**.

---

## 🥉 Step 5: Run the Bronze Layer (Raw Ingestion)

Open a **new terminal** and run:

```bash
cd AI-Ready-Agentic-Data-Platform-/agentic_data_platform

spark-submit \
  --packages io.delta:delta-spark_2.12:3.1.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  spark/bronze.py
```

**What this does:**
- Connects to Kafka
- Reads raw events from the `ecommerce_events` topic
- Writes them to `data/bronze/ecommerce_events/` as a Delta Lake table
- No cleaning, no filtering — just raw storage

> ⏳ The first run downloads Spark packages (may take 1–2 minutes). Subsequent runs are faster.

✅ **Verify:** After it finishes, check the data was written:

```bash
ls data/bronze/ecommerce_events/
```

Expected output (you should see `.parquet` files and a `_delta_log/` folder):
```
_delta_log/   part-00000-xxxxx.parquet   ...
```

---

## 🥈 Step 6: Run the Silver Layer (Clean & Validate)

```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.1.0 \
  spark/silver.py
```

**What this does:**
- Reads the raw Bronze data
- Removes events with missing user IDs or product IDs
- Validates that event types are one of: `view`, `cart`, `purchase`
- Removes duplicate events
- Converts timestamps to proper format
- **Fails the job** if invalid data is found (strict quality enforcement)

✅ **Verify:**

```bash
ls data/silver/ecommerce_events/
```

Expected output:
```
_delta_log/   part-00000-xxxxx.parquet   ...
```

---

## 🥇 Step 7: Run the Gold Layer (Business Metrics)

```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.1.0 \
  spark/gold.py
```

**What this does:** Creates three business-ready aggregated tables:

| Table | What it shows |
|---|---|
| `revenue_per_hour` | Total revenue, purchase count, avg order value per hour |
| `active_users_per_hour` | Number of distinct active users per hour |
| `conversion_rate` | View→Cart and Cart→Purchase conversion rates |

✅ **Verify:**

```bash
ls data/gold/
```

Expected output:
```
active_users_per_hour/   conversion_rate/   revenue_per_hour/
```

---

## 🔧 Step 8: Run Feature Engineering

```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.1.0 \
  features/build_features.py
```

**What this does:** Creates per-user ML features from the Silver data:
- Purchase count (last 24h and total)
- Average, max, and min order value
- Events per hour
- View→Cart and Cart→Purchase conversion ratios

✅ **Verify:**

```bash
ls data/features/user_features/
```

Expected output:
```
_delta_log/   part-00000-xxxxx.parquet   ...
```

---

## 🤖 Step 9: Train the ML Model

```bash
python ml/train_model.py
```

**What this does:**
- Loads the user features created in Step 8
- Trains a Logistic Regression model to predict which users are likely to purchase
- Saves the model, scaler, and performance metrics

✅ **Expected output:**
```
Loading features from data/features/user_features...
Training model...
Model Performance:
  Accuracy:  0.XX
  Precision: 0.XX
  Recall:    0.XX
  F1 Score:  0.XX
Model saved to data/models/purchase_predictor.pkl
```

✅ **Verify:**

```bash
ls data/models/
```

Expected output:
```
metrics.json   purchase_predictor.pkl   scaler.pkl
```

---

## 💬 Step 10: Start the AI Agent (Optional — Requires Ollama)

### 10.1 — Pull the Mistral model

```bash
ollama pull mistral
```

> ⏳ This downloads ~4 GB on the first run. Be patient.

### 10.2 — Start Ollama server

In a **separate terminal**:

```bash
ollama serve
```

### 10.3 — Run the agent

In another terminal:

```bash
cd AI-Ready-Agentic-Data-Platform-/agentic_data_platform
python agent/agent.py
```

### 10.4 — Try asking questions

Once the agent starts, you can type questions like:

```
🤖 Ask a question: What is the total revenue?
```

```
🤖 Ask a question: Show me the conversion rates
```

```
🤖 Ask a question: sql SELECT * FROM revenue_per_hour LIMIT 5
```

Type `quit` or `exit` to stop.

---

## 📊 Step 11: Launch the Dashboard (Optional)

```bash
cd AI-Ready-Agentic-Data-Platform-/agentic_data_platform
streamlit run ui/dashboard.py
```

✅ **Expected:** A browser window opens at **http://localhost:8501** showing an interactive analytics dashboard with charts for revenue, users, and conversion rates.

---

## 🧹 Cleanup

When you are done, stop everything:

### Stop the Event Generator
Press `Ctrl+C` in the terminal where it is running.

### Stop Docker Containers

```bash
cd AI-Ready-Agentic-Data-Platform-/agentic_data_platform
docker compose down
```

### (Optional) Remove Generated Data

```bash
rm -rf data/bronze/ data/silver/ data/gold/ data/features/ data/models/ data/checkpoints/
```

### (Optional) Remove Docker Volumes

```bash
docker compose down -v
```

---

## ❓ Troubleshooting

### "Connection refused" when running the Event Generator
- **Cause:** Kafka is not running or not yet healthy.
- **Fix:** Run `docker compose ps` and wait until Kafka shows `healthy`. Then retry.

### `spark-submit: command not found`
- **Cause:** Spark is not installed or not on your PATH.
- **Fix:** Install PySpark (`pip install pyspark`) and use `python spark/bronze.py` instead of `spark-submit`. Alternatively, install Apache Spark and add it to your PATH.

### Bronze layer fails with "No data found"
- **Cause:** The Event Generator has not sent enough events yet.
- **Fix:** Let the Event Generator run for at least 1–2 minutes, then retry.

### Silver layer exits with code 1
- **Cause:** The strict validation found invalid data (e.g., null IDs, negative prices).
- **Fix:** This is expected behavior — the Silver layer is designed to fail on bad data. Re-run the Bronze layer to get fresh data, then retry.

### `ModuleNotFoundError: No module named 'kafka'`
- **Cause:** Python dependencies are not installed.
- **Fix:** Run `pip install -r requirements.txt` from the `agentic_data_platform/` directory.

### Ollama errors ("connection refused" or "model not found")
- **Cause:** Ollama is not running or the Mistral model is not downloaded.
- **Fix:** Run `ollama serve` in a separate terminal, then `ollama pull mistral`.

### Docker Compose fails on older Docker versions
- **Cause:** Older Docker versions use `docker-compose` (with a hyphen) instead of `docker compose`.
- **Fix:** Try `docker-compose up -d` instead of `docker compose up -d`.

---

## 📋 Quick Reference: All Commands in Order

```bash
# Prerequisites (one-time setup)
cd AI-Ready-Agentic-Data-Platform-/agentic_data_platform
pip install -r requirements.txt

# Start infrastructure
docker compose up -d
docker exec -it kafka kafka-topics --create \
  --topic ecommerce_events \
  --bootstrap-server localhost:9092 \
  --partitions 3 --replication-factor 1

# Terminal 1: Event Generator (leave running)
python simulator/event_generator.py

# Terminal 2: Run pipeline steps (one at a time, in order)
spark-submit --packages io.delta:delta-spark_2.12:3.1.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 spark/bronze.py
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 spark/silver.py
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 spark/gold.py
spark-submit --packages io.delta:delta-spark_2.12:3.1.0 features/build_features.py
python ml/train_model.py

# Terminal 3: AI Agent (optional)
ollama pull mistral
ollama serve          # in one terminal
python agent/agent.py # in another terminal

# Terminal 4: Dashboard (optional)
streamlit run ui/dashboard.py

# Cleanup
docker compose down
```

---

## 🗺️ What Just Happened? (Full Picture)

```
Step 3: Docker starts Kafka (the "post office" for data)
         │
Step 4: Event Generator sends fake shopping events ──▶ Kafka
         │
Step 5: Bronze Layer reads Kafka ──▶ saves raw data to data/bronze/
         │
Step 6: Silver Layer reads Bronze ──▶ cleans & validates ──▶ saves to data/silver/
         │
Step 7: Gold Layer reads Silver ──▶ computes business metrics ──▶ saves to data/gold/
         │
Step 8: Feature Engineering reads Silver ──▶ creates per-user ML features ──▶ saves to data/features/
         │
Step 9: ML Model reads features ──▶ trains purchase predictor ──▶ saves to data/models/
         │
Step 10: AI Agent loads Gold + features ──▶ answers your questions using an LLM
         │
Step 11: Dashboard shows interactive charts from the Gold layer data
```

Congratulations! 🎉 You have successfully run an end-to-end AI-ready data platform.
