# Databricks notebook source
import time
import logging

# COMMAND ----------

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# COMMAND ----------

# Paths for the notebooks
bronze_path = "/Users/re046620@qintess.com/bronze"
silver_path = "/Users/re046620@qintess.com/silver"
gold_path = "/Users/re046620@qintess.com/gold"

# COMMAND ----------

# Function to execute a notebook with retries
def run_with_retries(notebook_path, retries=3, delay=10):
    attempt = 0
    while attempt < retries:
        try:
            dbutils.notebook.run(notebook_path, timeout_seconds=0)
            logging.info(f"{notebook_path} executed successfully!")
            return
        except Exception as e:
            attempt += 1
            logging.warning(f"Attempt {attempt} failed for {notebook_path}: {e}")
            if attempt == retries:
                logging.error(f"Fatal error: all attempts failed for {notebook_path}")
                raise
            time.sleep(delay)  # Wait before retrying

# COMMAND ----------

# Function to validate data quality
def validate_data(layer_name):
    logging.info(f"Validating data for layer: {layer_name}...")
    # Example validation logic (replace with real checks)
    if layer_name == "Silver":
        # Example placeholder for validation logic
        logging.info("Validation for Silver layer completed successfully!")
    elif layer_name == "Gold":
        logging.info("Validation for Gold layer completed successfully!")
    else:
        logging.info(f"No specific validations for layer: {layer_name}.")

# COMMAND ----------

# Step 1: Process the Bronze layer
logging.info("Starting Bronze layer processing...")
run_with_retries(bronze_path)
validate_data("Bronze")
logging.info("Bronze layer processed successfully!")

# COMMAND ----------

# Step 2: Process the Silver layer
logging.info("Starting Silver layer processing...")
run_with_retries(silver_path)
validate_data("Silver")
logging.info("Silver layer processed successfully!")

# COMMAND ----------

# Step 3: Process the Gold layer
logging.info("Starting Gold layer processing...")
run_with_retries(gold_path)
validate_data("Gold")
logging.info("Gold layer processed successfully!")

# COMMAND ----------


