# Databricks notebook source
import logging
import requests
import os
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient

# COMMAND ----------

# set logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# COMMAND ----------

# set Azure Blob Storage
# I´ll can use the environment variable, but it is a test, I get directly the credentials
account_name = "abinbevajbpstoragedl"
container_name = "abinbev"
account_key = "QA1OX5Dc/nM+XYFfZKwKFYweO8QVLkAbui110uAFv3zRqDrci+BC6FK7iPyqwxqOklFL3nSloOOy+AStAGtXTA=="
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# COMMAND ----------

def fetch_data_from_api(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()

# COMMAND ----------

def upload_to_blob(data, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(json.dumps(data, indent=4), overwrite=True)

# COMMAND ----------

def main():
    # step 1: consumer API
    api_url = "https://api.openbrewerydb.org/breweries"
    data = fetch_data_from_api(api_url)
    
    # step 2: create path
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    folder_name = f"bronze/{timestamp}"
    blob_name = f"{folder_name}/{timestamp}.json"
    
    # step 3: upload for the Blob Storage
    upload_to_blob(data, container_name, blob_name)
    logging.info("Upload sucess!")

# COMMAND ----------

if __name__ == "__main__":
    main()

# COMMAND ----------


