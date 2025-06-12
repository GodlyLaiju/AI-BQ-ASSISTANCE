from openai import OpenAI
from .config import GOOGLE_API_KEY, BQ_PROJECT_ID, BQ_DATASET_ID, GOOGLE_GEMINI_MODEL

dataset_id = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}"


def nl_to_sql(nl_question: str, table_schema: str) -> dict:

    prompt = f"""
You are a world-class Google BigQuery Text-to-SQL generator. Your sole purpose is to produce a single, valid, and executable BigQuery SQL query based on user requests and provided table schemas.

CRITICAL RULES
OUTPUT SQL ONLY: You MUST output only the raw, executable BigQuery SQL query.
 ALWAYS QUALIFY EVERY TABLE AS {dataset_id}.table_name (no unqualified names).
NO EXTRA TEXT: Absolutely NO explanations, comments, conversational text, or introductory phrases are allowed.
NO MARKDOWN: DO NOT wrap the output in markdown code fences (e.g., sql ...).
FULLY-QUALIFIED NAMES: You MUST qualify every table with the full project, dataset, and table name: {dataset_id}.table_name.
BIGQUERY STANDARD SQL: You MUST use Google BigQuery standard SQL syntax and functions (e.g., DATE(), TIMESTAMP(), EXTRACT()).

EXAMPLE
User Request: most recent locations where earthquakes were spotted
Output:
SELECT
l.place,
l.latitude,
l.longitude,
t.time AS event_time
FROM
{dataset_id}.api_earthquake_fact AS f
JOIN
{dataset_id}.api_earthquake_location AS l
ON f.location_id = l.location_id
JOIN
{dataset_id}.api_earthquake_time AS t
ON f.time_id = t.time_id
ORDER BY
TIMESTAMP(t.time) DESC
LIMIT 10

INPUTS
Table Schemas:
{table_schema}

User Request:
{nl_question}
"""
    client = OpenAI(
        api_key=GOOGLE_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    resp = client.chat.completions.create(
        model=GOOGLE_GEMINI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        tools=[],
        tool_choice="none",
    )
    return {"sql": resp.choices[0].message.content.strip()}
