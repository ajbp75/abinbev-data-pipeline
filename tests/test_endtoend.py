# Databricks notebook source
def test_pipeline_end_to_end():
    # 1. Run the Bronze layer notebook
    print("Running Bronze layer notebook...")
    dbutils.notebook.run("/Users/re046620@qintess.com/bronze", 300)
    print("Bronze layer completed successfully!")

    # 2. Run the Silver layer notebook
    print("Running Silver layer notebook...")
    dbutils.notebook.run("/Users/re046620@qintess.com/silver", 300)
    print("Silver layer completed successfully!")

    # 3. Run the Gold layer notebook
    print("Running Gold layer notebook...")
    dbutils.notebook.run("/Users/re046620@qintess.com/gold", 300)
    print("Gold layer completed successfully!")

    # 4. Validate results in the Gold layer
    print("Validating results in the Gold layer...")
    gold_data = spark.read.parquet("dbfs:/mnt/gold/test_gold_table_output.parquet")
    assert gold_data.count() == 2  # Verify the number of aggregations by state
    assert "brewery_type" in gold_data.columns  # Check if 'brewery_type' column exists
    assert gold_data.filter(gold_data.state == "CO").count() == 2  # Validate data for state 'CO'

if __name__ == "__main__":
    print("Starting End-to-End Pipeline Test...")
    test_pipeline_end_to_end()


# COMMAND ----------


