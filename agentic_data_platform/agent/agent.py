#!/usr/bin/env python3
"""
AI Agent for E-commerce Data Platform
Uses Ollama with Mistral model to answer natural language questions.
Executes SQL queries on Gold layer Delta tables.
"""

import os # For path handling
import json # For any JSON handling if needed
import re # For parsing SQL-like queries



# Import typing utilities for type hints.
# - List: Represents a list of specific data types (e.g., List[int])
# - Dict: Represents a dictionary with defined key-value types (e.g., Dict[str, int])
# - Any: Allows any data type when the type is unknown or flexible
# - Optional: Indicates a value can be of a specific type or None
from typing import List, Dict, Any, Optional  



# Import datetime class to work with date and time operations
# (e.g., timestamps, logging execution time, time calculations)
from datetime import datetime

# LangChain imports for working with LLMs and prompts
# LangChain is a Python (and JavaScript) framework that helps you build applications using Large Language Models (LLMs) like GPT, Llama, Mistral, etc.:
# LangChain = A toolkit to build AI-powered apps easily

# Import Ollama LLM from LangChain - Ollama is a local LLM server that can run models like Mistral and Phi on your machine, providing fast and private access to powerful language models.
try: 
    from langchain_ollama import OllamaLLM  # Try to import from langchain_ollama first (newer versions)
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM # Fallback to older import path if the first one fails



# For reading Delta tables
import pandas as pd # For data manipulation and analysis (e.g., reading parquet files, handling DataFrames)
import glob # For file pattern matching (e.g., to find all parquet files in a directory)



# Configuration
OLLAMA_MODEL = "phi"  # Faster than mistral
OLLAMA_BASE_URL = "http://localhost:11434"

import os as os_module
BASE_PATH = os_module.path.dirname(os_module.path.dirname(os_module.path.abspath(__file__)))

GOLD_PATHS = {
    "revenue_per_hour": os_module.path.join(BASE_PATH, "data/gold/revenue_per_hour"),
    "active_users_per_hour": os_module.path.join(BASE_PATH, "data/gold/active_users_per_hour"),
    "conversion_rate": os_module.path.join(BASE_PATH, "data/gold/conversion_rate")
}

FEATURES_PATH = os_module.path.join(BASE_PATH, "data/features/user_features")


class DataQueryEngine:
    """
    Engine for querying Delta Lake tables using pandas SQL.
    """
    
    def __init__(self):
        self.tables: Dict[str, pd.DataFrame] = {}
        self._load_tables()
    
    def _load_delta_table(self, path: str) -> Optional[pd.DataFrame]:
        """Load a Delta table as pandas DataFrame."""
        try:
            parquet_files = glob.glob(f"{path}/*.parquet")
            if parquet_files:
                df = pd.concat([pd.read_parquet(f) for f in parquet_files], ignore_index=True)
                return df
            else:
                print(f"  ⚠ No parquet files found in {path}")
                return None
        except Exception as e:
            print(f"  ⚠ Error loading {path}: {e}")
            return None
    
    def _load_tables(self):
        """Load all available tables."""
        print("Loading Gold layer tables...")
        
        for table_name, path in GOLD_PATHS.items():
            df = self._load_delta_table(path)
            if df is not None:
                self.tables[table_name] = df
                print(f"  ✓ Loaded {table_name}: {len(df)} rows")
        
        # Also load features table
        df = self._load_delta_table(FEATURES_PATH)
        if df is not None:
            self.tables["user_features"] = df
            print(f"  ✓ Loaded user_features: {len(df)} rows")
    
    def get_table_schemas(self) -> str:
        """Get schema information for all tables."""
        schemas = []
        for table_name, df in self.tables.items():
            columns = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
            schemas.append(f"Table: {table_name}\n  Columns: {columns}\n  Rows: {len(df)}")
        return "\n\n".join(schemas) if schemas else "No tables loaded yet. Run the Spark pipeline first."
    
    def execute_query(self, query: str) -> str:
        """Execute a pandas query on the available tables."""
        try:
            query = query.strip()
            
            if query.lower().startswith("select"):
                return self._execute_select(query)
            elif query.lower().startswith("describe") or query.lower().startswith("show"):
                return self.get_table_schemas()
            else:
                for table_name in self.tables:
                    if table_name.lower() in query.lower():
                        df = self.tables[table_name]
                        return f"Table {table_name}:\n{df.head(10).to_string()}"
                
                return f"Could not parse query. Available tables: {list(self.tables.keys())}"
        except Exception as e:
            return f"Query error: {str(e)}"
    
    def _execute_select(self, query: str) -> str:
        """Execute a SELECT-like query using pandas."""
        try:
            from_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE)
            if not from_match:
                return "Could not identify table in query"
            
            table_name = from_match.group(1)
            
            matched_table = None
            for t in self.tables:
                if t.lower() == table_name.lower() or table_name.lower() in t.lower():
                    matched_table = t
                    break
            
            if not matched_table:
                return f"Table '{table_name}' not found. Available: {list(self.tables.keys())}"
            
            df = self.tables[matched_table].copy()
            
            where_match = re.search(r'where\s+(.+?)(?:order|group|limit|$)', query, re.IGNORECASE)
            if where_match:
                condition = where_match.group(1).strip()
                condition = condition.replace("=", "==").replace("<>", "!=")
                try:
                    df = df.query(condition)
                except:
                    pass
            
            order_match = re.search(r'order\s+by\s+(\w+)\s*(asc|desc)?', query, re.IGNORECASE)
            if order_match:
                col = order_match.group(1)
                ascending = order_match.group(2) is None or order_match.group(2).lower() == 'asc'
                if col in df.columns:
                    df = df.sort_values(col, ascending=ascending)
            
            limit_match = re.search(r'limit\s+(\d+)', query, re.IGNORECASE)
            if limit_match:
                limit = int(limit_match.group(1))
                df = df.head(limit)
            else:
                df = df.head(10)
            
            return df.to_string()
        except Exception as e:
            return f"Query execution error: {str(e)}"
    
    def get_summary_stats(self, table_name: str) -> str:
        """Get summary statistics for a table."""
        if table_name not in self.tables:
            return f"Table '{table_name}' not found"
        
        df = self.tables[table_name]
        return f"Summary for {table_name}:\n{df.describe().to_string()}"
    
    def get_data_context(self) -> str:
        """Get a summary of all data for LLM context."""
        context_parts = []
        
        for table_name, df in self.tables.items():
            context_parts.append(f"\n=== {table_name} ===")
            context_parts.append(f"Columns: {list(df.columns)}")
            context_parts.append(f"Data:\n{df.to_string()}")
        
        return "\n".join(context_parts)


class AIAgent:
    """AI Agent that uses Ollama to answer questions about e-commerce data."""
    
    def __init__(self, query_engine: DataQueryEngine):
        self.query_engine = query_engine
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize the Ollama LLM."""
        try:
            self.llm = OllamaLLM(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=0.1
            )
            print(f"✓ Configured Ollama ({OLLAMA_MODEL})")
        except Exception as e:
            print(f"✗ Failed to configure Ollama: {e}")
            print("  Make sure Ollama is running: ollama serve")
            self.llm = None
    
    def answer_question(self, question: str) -> str:
        """Answer a question about the e-commerce data."""
        
        # Get data context
        data_context = self.query_engine.get_data_context()
        schema_info = self.query_engine.get_table_schemas()
        
        # Build prompt
        prompt = f"""You are an AI data analyst for an e-commerce platform.
Answer the user's question based on the data provided below.

AVAILABLE TABLES:
{schema_info}

CURRENT DATA:
{data_context}

USER QUESTION: {question}

Provide a clear, concise answer based on the data above. Include specific numbers and insights.
If the data is insufficient, say so clearly.

ANSWER:"""

        if self.llm:
            try:
                print("  🤔 Thinking...")
                response = self.llm.invoke(prompt)
                return response.strip()
            except Exception as e:
                return f"LLM Error: {str(e)}\n\nFalling back to data display:\n{self.query_engine.get_table_schemas()}"
        else:
            return f"LLM not available. Here's the raw data:\n{data_context}"


def run_interactive_session():
    """Run an interactive question-answering session."""
    print("=" * 60)
    print("🤖 E-commerce AI Data Agent")
    print("=" * 60)
    print("Ask questions about your e-commerce data in natural language.")
    print("Commands: 'quit' to exit, 'sql <query>' for direct SQL")
    print("=" * 60)
    
    # Initialize
    query_engine = DataQueryEngine()
    agent = AIAgent(query_engine)
    
    print("\n📝 Example questions:")
    print("  • What is the total revenue?")
    print("  • Show me the conversion rates")
    print("  • How many active users do we have?")
    print("  • sql SELECT * FROM revenue_per_hour")
    print()
    
    while True:
        try:
            question = input("\n🤖 Ask a question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("\n" + "-" * 50)
            
            # Handle direct SQL queries
            if question.lower().startswith("sql "):
                sql_query = question[4:].strip()
                result = query_engine.execute_query(sql_query)
                print(f"\n📊 SQL Result:\n{result}")
            elif question.lower() in ['describe', 'show tables', 'schema']:
                print(f"\n📊 Available Tables:\n{query_engine.get_table_schemas()}")
            else:
                # Use AI to answer
                answer = agent.answer_question(question)
                print(f"\n📊 Answer:\n{answer}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    run_interactive_session()


if __name__ == "__main__":
    main()
