# Databricks notebook source

from pyspark.sql import SparkSession
from azure.storage.blob import ContainerClient
import re
import matplotlib.pyplot as plt

# COMMAND ----------

# set spark
spark = SparkSession.builder.appName("GoldLayerJob").getOrCreate()
spark.conf.set("fs.azure.account.key.abinbevajbpstoragedl.blob.core.windows.net", "QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA==")


# COMMAND ----------

# set Azure Blob Storage
connection_string = "DefaultEndpointsProtocol=https;AccountName=abinbevajbpstoragedl;AccountKey=QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA==;EndpointSuffix=core.windows.net"
container_name = "abinbev"
container_client = ContainerClient.from_connection_string(connection_string, container_name)

# COMMAND ----------

# get data layer gold in the Azure Blob Storage
try:
    gold_files = container_client.list_blobs(name_starts_with="gold/")
    blobs_list = list(gold_files)  # Convertendo o iterador em uma lista para depuração
    if not blobs_list:
        print("None Files")
except Exception as e:
    print(f"Error blobs: {e}")
    raise

# COMMAND ----------

# recover subdirectory name
folder_path = None
for blob in blobs_list:
    if blob.name.endswith('_gold_table_output.parquet'):
        folder_path = blob.name
        break

if folder_path is None:
    raise ValueError("none subdicrectoty")


# COMMAND ----------

#get just parquet files
file_name = None
for blob in blobs_list:
    if blob.name.startswith(folder_path) and 'part' in blob.name and blob.name.endswith('.parquet'):
        file_name = blob.name
        break

# COMMAND ----------

# Get partitions
file_name = None
for blob in blobs_list:
    if blob.name.startswith(folder_path) and 'part' in blob.name and blob.name.endswith('.parquet'):
        file_name = blob.name
        break

if file_name is None:
    raise ValueError("Nenhum arquivo encontrado na camada gold com o padrão especificado.")


# COMMAND ----------

# Path directoty
gold_path = f"wasbs://abinbev@abinbevajbpstoragedl.blob.core.windows.net/{file_name}"

# COMMAND ----------

# loading datas parquet for dataframe spark
gold_df = spark.read.parquet(gold_path)

# COMMAND ----------

# show data recover
gold_df.show()

# COMMAND ----------

#some analyses
type_count_df = gold_df.groupBy('brewery_type').count()
state_count_df = gold_df.groupBy('state_province').count()

colorado_df = gold_df.filter(gold_df.state_province == 'Colorado')
brewery_type_count_df = colorado_df.groupBy('brewery_type').count()

# COMMAND ----------

# transform dataframe spark to pandas to make graphics
type_count_pd = type_count_df.orderBy('count', ascending=False).toPandas()
state_count_pd = state_count_df.orderBy('count', ascending=False).toPandas()
brewery_type_count_pd = brewery_type_count_df.orderBy('count', ascending=True).toPandas()


# COMMAND ----------

# First graph
plt.figure(figsize=(10, 6))
plt.bar(type_count_pd['brewery_type'], type_count_pd['count'])
plt.xlabel('Brewery Type')
plt.ylabel('Count')
plt.title('Count of Brewery Types')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# COMMAND ----------

# Second Graph
plt.figure(figsize=(10, 6))
plt.bar(state_count_pd['state_province'], state_count_pd['count'])
plt.xlabel('State/Province')
plt.ylabel('Count')
plt.title('Count of Breweries by State/Province')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# COMMAND ----------

spark.stop()
