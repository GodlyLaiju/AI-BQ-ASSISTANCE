import logging
from google.cloud import bigquery
from .config import BQ_CREDENTIALS, BQ_PROJECT_ID, BQ_DATASET_ID

# Initialize client
bq_client = bigquery.Client.from_service_account_json(BQ_CREDENTIALS)


def get_table_schema(table_name: str):
    table = bq_client.get_table(f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{table_name}")
    return "\n".join(f"{f.name} ({f.field_type})" for f in table.schema)


def run_sql_query(sql: str):
    try:
        df = bq_client.query(sql).result().to_dataframe()
        return df.to_dict(orient="records")
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return {"error": str(e)}


def record_unknown_question(question: str):
    logging.info(f"Unknown question recorded: {question}")
    return {"recorded": True}
