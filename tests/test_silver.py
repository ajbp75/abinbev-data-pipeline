# Databricks notebook source
import os
import tempfile
import random
import string
from datetime import datetime
from unittest.mock import MagicMock
from azure.storage.blob import BlobServiceClient
from pyspark.sql import SparkSession

# Mock do BlobServiceClient
class MockBlob:
    def __init__(self, name, content):
        self.name = name
        self.content = content

class MockContainerClient:
    def __init__(self):
        self.blobs = {}

    def upload_blob(self, name, content):
        self.blobs[name] = MockBlob(name, content)

    def list_blobs(self, name_starts_with=None):
        if name_starts_with:
            return [blob for name, blob in self.blobs.items() if name.startswith(name_starts_with)]
        return list(self.blobs.values())

    def get_blob_client(self, container, blob):
        return MagicMock(download_blob=MagicMock(return_value=MagicMock(readall=MagicMock(return_value=self.blobs[blob].content))))

# Função auxiliar para criar nomes aleatórios
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Função para criar timestamps
def generate_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M")

# Configurar Spark
spark = SparkSession.builder \
    .appName("Silver Layer Test") \
    .master("local[*]") \
    .getOrCreate()

# Funções existentes do script Silver

def list_bronze_folders(container_client):
    """Get Folders in the layer Bronze."""
    blob_list = container_client.list_blobs(name_starts_with="bronze/")
    folders = set(blob.name.split("/")[1] for blob in blob_list if "/" in blob.name)
    return folders

def process_bronze_to_silver(container_client, folder):
    """Process of Bronze to Silver."""
    blob_list = container_client.list_blobs(name_starts_with=f"bronze/{folder}/")
    timestamp = generate_timestamp()
    for blob in blob_list:
        if blob.name.endswith(".json"):
            blob_client = container_client.get_blob_client(None, blob.name)
            json_content = blob_client.download_blob().readall()
            try:
                records = json.loads(json_content)
                if not isinstance(records, list):
                    records = [records]

                if not records:
                    raise ValueError("None register.")

                df = spark.read.json(spark.sparkContext.parallelize([json.dumps(record) for record in records]))

                if "state" not in df.columns:
                    raise ValueError("The column 'state' not found.")

                partition_column = "state"
                output_path = f"/tmp/silver/{folder}/{timestamp}"
                df.write.partitionBy(partition_column).mode("overwrite").parquet(output_path)
                print(f"Data saved in: {output_path}")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error JSON: {e}")
                continue

# Simula o teste

def test_silver_layer():
    # Configuração inicial
    mock_container_client = MockContainerClient()

    # Criando pastas e arquivos aleatoriamente
    for _ in range(5):
        folder_name = random_string()
        for _ in range(random.randint(1, 3)):
            file_name = f"bronze/{folder_name}/{random_string()}.json"
            content = '{"state": "random_state", "value": 42}'
            mock_container_client.upload_blob(file_name, content)

    # Testando a listagem de pastas
    folders = list_bronze_folders(mock_container_client)
    assert len(folders) > 0, "Nenhuma pasta foi encontrada na camada Bronze"

    # Testando o processamento de cada pasta
    for folder in folders:
        process_bronze_to_silver(mock_container_client, folder)

    print("Testes da camada Silver concluídos com sucesso!")

if __name__ == "__main__":
    # Incluir a execução do notebook Silver antes dos testes
    print("Executando o notebook Silver")
    dbutils.notebook.run("/Users/re046620@qintess.com/silver", 60)
    
    # Run the silver script
    print("Executando o script Silver")
    test_silver_layer()


# COMMAND ----------


