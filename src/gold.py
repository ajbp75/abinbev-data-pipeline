# Databricks notebook source
import os
from azure.storage.blob import ContainerClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, max, min

# COMMAND ----------

#set enviroment spark
spark = SparkSession.builder.appName("GoldLayerJob").getOrCreate()
spark.conf.set("fs.azure.account.key.abinbevajbpstoragedl.blob.core.windows.net", "QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA==")

# COMMAND ----------

def get_latest_silver_folder(container_client):
    blob_list = container_client.list_blobs(name_starts_with="silver/")
    folders = sorted(set(blob.name.split("/")[1] for blob in blob_list if "/" in blob.name), reverse=True)
    if folders:
        return folders[0]  # Latest folder by name (yyyymmddhhmm)
    else:
        raise FileNotFoundError("No folders found in the Silver layer.")


# COMMAND ----------

# Get .parquet files and join in the dataframe
def load_silver_data(container_client, folder_name):
    parquet_files = [
        f"wasbs://abinbev@abinbevajbpstoragedl.blob.core.windows.net/silver/{blob.name.split('silver/', 1)[-1]}"
        for blob in container_client.list_blobs(name_starts_with=f'silver/{folder_name}/')
        if blob.name.endswith('.parquet')
    ]
    if parquet_files:
        return spark.read.option("mergeSchema", "true").parquet(*parquet_files)
    else:
        raise FileNotFoundError(f"No parquet files found in the Silver layer for folder: {folder_name}.")


# COMMAND ----------

def create_gold_table(silver_df):
    return silver_df.groupBy("brewery_type", "state_province")\
                    .agg(
                        avg(col("latitude")).alias("average_latitude"),
                        max(col("longitude")).alias("max_longitude"),
                        min(col("longitude")).alias("min_longitude"),
                        count(col("id")).alias("total_entries")
                        )

# COMMAND ----------

def save_gold_data(gold_df, folder_name):
    output_path = f"wasbs://abinbev@abinbevajbpstoragedl.blob.core.windows.net/gold/{folder_name}/{folder_name}_gold_table_output.parquet"
    gold_df.write.mode("overwrite").parquet(output_path)
    print(f"Gold data saved to: {output_path}")

# COMMAND ----------

def main():
    try:
        container_client = ContainerClient.from_connection_string(
            conn_str="DefaultEndpointsProtocol=https;AccountName=abinbevajbpstoragedl;AccountKey=QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA==;EndpointSuffix=core.windows.net",
            container_name="abinbev"
        )

        # Get the latest folder from the Silver layer
        latest_folder = get_latest_silver_folder(container_client)
        print(f"Latest folder in Silver layer: {latest_folder}")

        # Load data from the Silver layer
        silver_df = load_silver_data(container_client, latest_folder)

        # Create the Gold layer DataFrame
        gold_df = create_gold_table(silver_df)

        # Save the Gold layer data
        save_gold_data(gold_df, latest_folder)

        print("Gold layer processing complete!")

    except Exception as e:
        print(f"An error occurred: {e}")


# COMMAND ----------

if __name__ == "__main__":
    main()


# COMMAND ----------


