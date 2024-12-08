# Databricks notebook source
import os
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from pyspark.sql import SparkSession

# COMMAND ----------

# set Azure Blob Storage
account_name = "abinbevajbpstoragedl"
container_name = "abinbev"
account_key = "QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA=="
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# COMMAND ----------

# set Spark
spark = SparkSession.builder \
    .appName("Silver") \
    .master("local[*]") \
    .getOrCreate()

spark.conf.set("fs.azure.account.key.abinbevajbpstoragedl.blob.core.windows.net", "QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA==")

# COMMAND ----------

def list_bronze_folders(container_client):
    """Get Folders in the layer Bronze."""
    blob_list = container_client.list_blobs(name_starts_with="bronze/")
    folders = set(blob.name.split("/")[1] for blob in blob_list if "/" in blob.name)
    return folders

# COMMAND ----------

def process_bronze_to_silver(container_client, folder):
    """Process of Bronze to Silver."""
    blob_list = container_client.list_blobs(name_starts_with=f"bronze/{folder}/")
    for blob in blob_list:
        if blob.name.endswith(".json"):
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
            json_content = blob_client.download_blob().readall().decode('utf-8')
            try:
                records = json.loads(json_content)
                if not isinstance(records, list):
                    records = [records]
                
                if not records:
                    raise ValueError("None register.")
                
                df = spark.read.json(spark.sparkContext.parallelize([json.dumps(record) for record in records]))

                if "state" not in df.columns:
                    raise ValueError("The column 'state' not find.")

                partition_column = "state"
                output_path = f"wasbs://{container_name}@{account_name}.blob.core.windows.net/silver/{folder}"
                df.write.partitionBy(partition_column).mode("overwrite").parquet(output_path)
                print(f"Data save in the: {output_path}")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error JSON: {e}")
                continue

# COMMAND ----------

def main():
    container_client = blob_service_client.get_container_client(container_name)

    folders = list_bronze_folders(container_client)
 
    for folder in folders:
        process_bronze_to_silver(container_client, folder)

    print("Process complete!")

# COMMAND ----------

if __name__ == "__main__":
    main()

# COMMAND ----------


