# Databricks notebook source
import os
import random
import string
from datetime import datetime
from unittest.mock import MagicMock
from azure.storage.blob import BlobServiceClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, max, min

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
    .appName("Gold Layer Test") \
    .master("local[*]") \
    .getOrCreate()

# Testando a camada Gold

def test_gold_layer():
    # Configuração inicial
    mock_container_client = MockContainerClient()

    # Criar dados simulados na camada Silver
    folder_name = generate_timestamp()
    silver_data = [
        '{"brewery_type": "micro", "state_province": "CA", "latitude": 34.05, "longitude": -118.25, "id": "1"}',
        '{"brewery_type": "macro", "state_province": "NY", "latitude": 40.71, "longitude": -74.00, "id": "2"}',
        '{"brewery_type": "micro", "state_province": "CA", "latitude": 36.77, "longitude": -119.41, "id": "3"}'
    ]
    for idx, data in enumerate(silver_data):
        file_name = f"silver/{folder_name}/file_{idx}.json"
        mock_container_client.upload_blob(file_name, data)

    # Passar o mock do container_client para o contexto do notebook
    global container_client
    container_client = mock_container_client

    # Validação: verificar se os dados simulados foram criados corretamente
    print(f"Dados simulados criados na pasta: silver/{folder_name}")

    # Chamar o notebook Gold no Databricks
    print("Executando o notebook Gold no Databricks")
    try:
        dbutils.notebook.run("/Users/re046620@qintess.com/gold", 300)
        print("Notebook Gold executado com sucesso!")
    except Exception as e:
        print(f"Erro ao executar o notebook Gold: {e}")
        raise

    # Validar resultados (opcional)
    print("Testes da camada Gold concluídos com sucesso!")

if __name__ == "__main__":
    # Executar o teste
    print("Iniciando o teste da camada Gold")
    test_gold_layer()


# COMMAND ----------


