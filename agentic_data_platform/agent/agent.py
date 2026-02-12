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






# LLM Configuration

# OLLAMA_MODEL:
#   Specifies the local Ollama model to use for generating responses.
#   "phi" is selected because it is lightweight and faster than larger models
#   like Mistral, making it suitable for local development and quick inference.
#
# OLLAMA_BASE_URL:
#   Defines the endpoint where the Ollama server is running.
#   By default, Ollama serves models locally at http://localhost:11434.
#   This allows the application to send prompts to the model via API calls.
OLLAMA_MODEL = "phi"  # Specifing the model to use with Ollama (phi is a smaller, faster model suitable for local use)
OLLAMA_BASE_URL = "http://localhost:11434" # Default Ollama endpoint



# Import the built-in 'os' module with an alias (os_module)
# to avoid potential naming conflicts with other variables named 'os'.
import os as os_module 


# Determine the project’s base directory dynamically.
# Step-by-step:
# 1. __file__ → Gets the current file's path.
# 2. abspath(__file__) → Converts it to an absolute path.
# 3. dirname(...) → Moves one level up (parent directory).
# 4. dirname(...) again → Moves one more level up.
#
# Result:
# BASE_PATH points to the root directory of the project.
# This ensures file paths work correctly regardless of where the script is executed from.
BASE_PATH = os_module.path.dirname(os_module.path.dirname(os_module.path.abspath(__file__))) # Get the base path of the project by going up two levels from the current file's location

GOLD_PATHS = {
    "revenue_per_hour": os_module.path.join(BASE_PATH, "data/gold/revenue_per_hour"), 
    "active_users_per_hour": os_module.path.join(BASE_PATH, "data/gold/active_users_per_hour"),
    "conversion_rate": os_module.path.join(BASE_PATH, "data/gold/conversion_rate")
} # Define paths to the Gold layer Delta tables for revenue, active users, and conversion rate


# Define path to the features table (user_features) in the features layer
FEATURES_PATH = os_module.path.join(BASE_PATH, "data/features/user_features") 





# DataQueryEngine class is responsible for loading Delta Lake tables as pandas DataFrames and executing SQL-like queries on them.
# It provides methods to load tables, get schema information, execute queries, and summarize data for LLM context.
# The class abstracts away the complexities of reading Delta tables and allows the AI agent to interact with the data in a more intuitive way.
# Key functionalities include:
# - Loading Delta tables from specified paths and storing them in a dictionary for easy access.
# - Providing schema information for all loaded tables.
# - Executing simple SQL-like queries (SELECT, WHERE, ORDER BY, LIMIT) on the loaded DataFrames.
# - Summarizing data for use in LLM prompts, giving the AI agent context about the available data when answering questions.         
class DataQueryEngine:
    """
    Engine for querying Delta Lake tables using pandas SQL.
    Loads tables from the Gold layer and features, and allows executing SQL-like queries.

    Methods:
    - __init__: Initializes the engine and loads tables.
    - _load_delta_table: Helper method to load a Delta table as a pandas DataFrame.
    - _load_tables: Loads all specified tables into memory.
    - get_table_schemas: Returns schema information for all loaded tables.
    - execute_query: Executes a SQL-like query on the loaded tables and returns results.
    - _execute_select: Helper method to execute SELECT queries using pandas.
    - get_summary_stats: Provides summary statistics for a specified table.
    - get_data_context: Summarizes all loaded data for use in LLM context.  
    """
    
    def __init__(self): #Initialize the DataQueryEngine and load tables into memory
        self.tables: Dict[str, pd.DataFrame] = {} #  define a dictionary to hold the loaded tables, where keys are table names and values are pandas DataFrames
        self._load_tables() # Load all tables from the specified paths into memory when the engine is initialized
    


    # _load_delta_table is a helper method that takes a file path as input and attempts to load all parquet files 
    # in that directory into a single pandas DataFrame. 
    # It uses glob to find all parquet files, reads them into DataFrames, and concatenates them. 
    # If successful, it returns the combined DataFrame; 
    # if no parquet files are found or an error occurs, it returns None and prints a warning message.
    def _load_delta_table(self, path: str) -> Optional[pd.DataFrame]: # 
        """
        Load a Delta table as pandas DataFrame.
        Args: path (str): The file path to the Delta table (parquet files). 
        Returns: Optional[pd.DataFrame]: A pandas DataFrame containing the table data, or None if loading fails. 

        """
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
    


    # _load_tables is a helper method that iterates through the GOLD_PATHS dictionary, loading each specified Delta table using the _load_delta_table method.
    # It stores the loaded DataFrames in the self.tables dictionary with the table name as the key.
    # # It also loads the user_features table from the FEATURES_PATH. 
    # The method prints the status of each table loading operation, 
    # including the number of rows loaded or any warnings if loading fails. 
    def _load_tables(self):
        """
        Load all available tables.
          - Iterates through the GOLD_PATHS to load each Gold layer table.
          - Also loads the user_features table from the features layer. 
          - Stores loaded tables in the self.tables dictionary for easy access.

        """
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
    



    # get_table_schemas returns a string containing schema information for all loaded tables.
    # It iterates through self.tables, extracting column names and their data types for each table.
    def get_table_schemas(self) -> str:
        """
        Get schema information for all tables.

        Returns a formatted string with table names, columns, data types, and row counts. 
          - If no tables are loaded, it returns a message indicating that the Spark pipeline should be run first. 

        
        """
        schemas = []
        for table_name, df in self.tables.items():
            columns = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
            schemas.append(f"Table: {table_name}\n  Columns: {columns}\n  Rows: {len(df)}")
        return "\n\n".join(schemas) if schemas else "No tables loaded yet. Run the Spark pipeline first."




    # execute_query takes a SQL-like query as input and attempts to execute it against the loaded tables.
    # It supports basic SELECT queries with optional WHERE, ORDER BY, and LIMIT clauses.
    def execute_query(self, query: str) -> str:
        """
        Execute a pandas query on the available tables.

         - Parses the query to identify the table and any conditions.
         - Supports basic SELECT queries with optional WHERE, ORDER BY, and LIMIT clauses. 
         - If the query is a DESCRIBE or SHOW TABLES command, it returns the schema information. 
         - If the query references a table directly, it returns the first few rows of that table.
         - If the query cannot be parsed, it returns an error message with available tables. 
         - Catches and returns any exceptions that occur during query execution.

       Args: query (str): The SQL-like query to execute.
       Returns: str: The result of the query execution or an error message.

        """
        try:
            query = query.strip() # Remove leading and trailing whitespace from the query for cleaner parsing
            
            if query.lower().startswith("select"): #If the query starts with "SELECT", we will attempt to execute it as a SQL-like query using pandas
                return self._execute_select(query) #Call the helper method to execute the SELECT query and return the result
            elif query.lower().startswith("describe") or query.lower().startswith("show"): #If the query starts with "DESCRIBE" or "SHOW", we will return the schema information for all loaded tables
                return self.get_table_schemas() #Call the method to get table schemas and return it as the result
            else: # For any other query, we will check if it references a table directly and return the first few rows of that table
                for table_name in self.tables: # Iterate through the loaded tables to see if the query references any of them   
                    if table_name.lower() in query.lower(): # If the table name is found in the query (case-insensitive match), we will return the first few rows of that table
                        df = self.tables[table_name] # Get the DataFrame for the matched table
                        return f"Table {table_name}:\n{df.head(10).to_string()}" # Return the first 10 rows of the matched table as a string
                
                return f"Could not parse query. Available tables: {list(self.tables.keys())}"
        except Exception as e:
            return f"Query error: {str(e)}" #Catch and return any exceptions that occur during query execution as an error message
    



    # execute_select is a helper method that executes SELECT-like queries using pandas.
    # It parses the query to identify the table name, optional WHERE conditions, ORDER BY clauses, and LIMIT.
    # It uses regular expressions to extract these components from the query string and applies them to the corresponding DataFrame.
    # The method returns the resulting DataFrame as a string. If any errors occur during parsing or execution, it returns an error message.
    # This method allows the AI agent to execute simple SQL-like queries on the loaded DataFrames without needing a full SQL engine, enabling it to answer questions based on the data effectively.
    def _execute_select(self, query: str) -> str:
        """
        Execute a SELECT-like query using pandas.
         - Parses the query to identify the table, optional WHERE conditions, ORDER BY clauses, and LIMIT. 
         - Uses regular expressions to extract these components from the query string. 
         - Applies the conditions and sorting to the corresponding DataFrame. - Returns the resulting DataFrame as a string. 
         - If any errors occur during parsing or execution, it returns an error message. Args: query (str): 
         The SQL-like SELECT query to execute. Returns: str: The result of the query execution or an error message.
        
        """
        try:
            from_match = re.search(r'from\s+(\w+)', query, re.IGNORECASE) # Use regular expression to find the table name after the "FROM" keyword in the query (case-insensitive match)
            if not from_match:
                return "Could not identify table in query"
            
            table_name = from_match.group(1) # Extract the table name from the regex match group
            
            matched_table = None
            for t in self.tables: # Iterate through the loaded tables to find a match for the table name in the query (case-insensitive match or partial match)
                if t.lower() == table_name.lower() or table_name.lower() in t.lower(): # If the table name in the query matches a loaded table name (case-insensitive) or is a substring of a loaded table name, we consider it a match
                    matched_table = t #
                    break
            
            if not matched_table: # If no matching table is found, return an error message with the available tables
                return f"Table '{table_name}' not found. Available: {list(self.tables.keys())}" # 
            
            df = self.tables[matched_table].copy() # Get a copy of the matched table's DataFrame to work with for query execution
            
            where_match = re.search(r'where\s+(.+?)(?:order|group|limit|$)', query, re.IGNORECASE) # Use regular expression to find the WHERE clause and its conditions in the query (case-insensitive match). It captures everything after "WHERE" until it hits "ORDER", "GROUP", "LIMIT", or the end of the string.
            if where_match: # If a WHERE clause is found in the query, we will attempt to apply the conditions to filter the DataFrame accordingly
                condition = where_match.group(1).strip() # Extract the conditions from the regex match group and remove any leading/trailing whitespace
                condition = condition.replace("=", "==").replace("<>", "!=") # Replace SQL-style operators with pandas query operators (e.g., "=" becomes "==", "<>" becomes "!=") to make the condition compatible with pandas' query method
                try:
                    df = df.query(condition) # Use the pandas query method to filter the DataFrame based on the extracted conditions. If the condition is valid, it will return a new DataFrame with only the rows that satisfy the condition.
                except: # If there is an error in the condition (e.g., syntax error, invalid column name), we will ignore the WHERE clause and proceed without filtering the DataFrame. This allows us to still return results even if the condition is not perfectly formatted.
                    pass
             
            order_match = re.search(r'order\s+by\s+(\w+)\s*(asc|desc)?', query, re.IGNORECASE) # Use regular expression to find the ORDER BY clause in the query (case-insensitive match). It captures the column name to sort by and an optional sorting direction (ASC or DESC).
            if order_match: # If an ORDER BY clause is found in the query, we will attempt to sort the DataFrame based on the specified column and sorting direction
                col = order_match.group(1) # Extract the column name to sort by from the regex match group
                ascending = order_match.group(2) is None or order_match.group(2).lower() == 'asc' # Determine the sorting direction based on the optional second regex group. If it is not specified or is "ASC", we will sort in ascending order; if it is "DESC", we will sort in descending order.
                if col in df.columns:  # Check if the specified column for sorting exists in the DataFrame. If it does, we will sort the DataFrame based on that column and the determined sorting direction.
                    df = df.sort_values(col, ascending=ascending) # Use the pandas sort_values method to sort the DataFrame by the specified column and sorting direction. If the column does not exist, we will skip sorting and proceed with the original order of the DataFrame.
            
            limit_match = re.search(r'limit\s+(\d+)', query, re.IGNORECASE) # Use regular expression to find the LIMIT clause in the query (case-insensitive match). It captures the number of rows to limit the result to.     
            if limit_match: # If a LIMIT clause is found in the query, we will attempt to limit the number of rows in the resulting DataFrame to the specified number. This allows us to return only a subset of the results if the query includes a LIMIT clause.
                limit = int(limit_match.group(1)) # Extract the number of rows to limit to from the regex match group and convert it to an integer
                df = df.head(limit) # Use the pandas head method to limit the DataFrame to the specified number of rows. If no LIMIT clause is found, we will return the first 10 rows of the resulting DataFrame by default to avoid overwhelming the output with too much data.
            else: # If no LIMIT clause is found in the query, we will return the first 10 rows of the resulting DataFrame by default to provide a manageable amount of data in the output. This ensures that even if the query does not specify a limit, we won't return an excessively large result set that could be difficult to read or process.
                df = df.head(10) # Return the first 10 rows of the resulting DataFrame as a string. This provides a snapshot of the query results while keeping the output concise and readable. If the resulting DataFrame is empty, it will return an empty string or indicate that no results were found based on how pandas handles empty DataFrames when converted to strings.
            
            return df.to_string() # Convert the resulting DataFrame to a string format for display. This allows us to return the query results in a readable format that can be easily printed or included in responses from the AI agent. If the DataFrame is large, it will be truncated based on the earlier LIMIT clause or default head(10) to ensure the output remains manageable.
        except Exception as e: # Catch and return any exceptions that occur during the parsing or execution of the query as an error message. This helps to provide feedback on what went wrong if the query is not properly formatted or if there are issues with the data.
            return f"Query execution error: {str(e)}" # Return an error message indicating that there was an issue executing the query, along with the specific error message from the exception. This allows users to understand what went wrong and potentially adjust their query accordingly.
    


    
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
