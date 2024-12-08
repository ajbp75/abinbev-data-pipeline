# Databricks notebook source
# DBTITLE 1,est
import time
from azure.storage.blob import ContainerClient

def test_pipeline_performance():
    """
    Measures the performance of the pipeline for Bronze, Silver, and Gold layers.
    """
    try:
        # Initialize the Azure Blob Container Client
        container_client = ContainerClient.from_connection_string(
            conn_str="DefaultEndpointsProtocol=https;AccountName=abinbevajbpstoragedl;"
                     "AccountKey=QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA==;"
                     "EndpointSuffix=core.windows.net",
            container_name="abinbev"
        )

        # Track performance metrics
        metrics = {}

        # 1. Measure Bronze layer performance
        print("Measuring Bronze layer performance...")
        start_time = time.time()
        dbutils.notebook.run("/Users/re046620@qintess.com/bronze", 300)
        metrics['bronze_time'] = time.time() - start_time
        print(f"Bronze layer completed in {metrics['bronze_time']:.2f} seconds.")

        # 2. Measure Silver layer performance
        print("Measuring Silver layer performance...")
        start_time = time.time()
        dbutils.notebook.run("/Users/re046620@qintess.com/silver", 300)
        metrics['silver_time'] = time.time() - start_time
        print(f"Silver layer completed in {metrics['silver_time']:.2f} seconds.")

        # 3. Measure Gold layer performance
        print("Measuring Gold layer performance...")
        start_time = time.time()
        dbutils.notebook.run("/Users/re046620@qintess.com/gold", 300)
        metrics['gold_time'] = time.time() - start_time
        print(f"Gold layer completed in {metrics['gold_time']:.2f} seconds.")

        # Report performance metrics
        print("Pipeline Performance Metrics:")
        for layer, duration in metrics.items():
            print(f"{layer.capitalize()} Layer: {duration:.2f} seconds")

        return metrics

    except Exception as e:
        print(f"An error occurred during the pipeline performance test: {e}")
        raise

if __name__ == "__main__":
    print("Starting Pipeline Performance Test...")
    test_pipeline_performance()


# COMMAND ----------


