# Databricks notebook source
import unittest
from unittest.mock import patch, MagicMock

# COMMAND ----------

# MAGIC %run "./bronze"

# COMMAND ----------

class TestBronzeLayer(unittest.TestCase):
    @patch('requests.get')
    def test_fetch_data_from_api(self, mock_get):
        # Configurar o mock
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1, "name": "Brewery"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Chamar a função
        api_url = "https://api.openbrewerydb.org/breweries"
        data = fetch_data_from_api(api_url)

        # Validar o resultado
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Brewery")

# COMMAND ----------

 @patch('azure.storage.blob.BlobServiceClient')
def test_upload_to_blob(self, mock_blob_service_client):
    # Configurar o mock
    mock_blob_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    # Dados de teste
    data = [{"id": 1, "name": "Brewery"}]
    container_name = "test-container"
    blob_name = "test-blob.json"

    # Chamar a função
    upload_to_blob(data, container_name, blob_name)

    # Validar o upload
    mock_blob_client.upload_blob.assert_called_once()
    args, kwargs = mock_blob_client.upload_blob.call_args
    self.assertIn("Brewery", args[0])  # Verifica se o JSON contém os dados esperados


# COMMAND ----------

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)

# COMMAND ----------


