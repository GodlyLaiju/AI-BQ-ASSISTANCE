## BQQueryAssistant

A lightweight Gradio-powered chat interface that translates natural language into BigQuery SQL, executes queries against your Google Cloud project, and returns results interactively.

---

### Features

* **Natural Language → SQL**: Converts user prompts into BigQuery SQL using Gemini API.
* **Schema Introspection**: Automatically discovers and qualifies table names.
* **Error Handling & Logging**: Catches query errors, provides feedback, and logs all interactions.
* **Interactive UI**: Simple Gradio interface for chatting and viewing results.

---

### Project Structure

```text
BQQueryAssistant/
├── src/                   # Application source
│   ├── bq_query_assistant # Core logic & utilities
│   │   ├── __init__.py
│   │   ├── schema.py      # Introspection & helpers
│   │   ├── translator.py  # Text-to-SQL logic
│   │   └── executor.py    # BigQuery client wrapper
│   └── main.py            # Gradio app entrypoint
├── tests/                 # Unit and integration tests
│   └── test_translator.py
└── docs/                  # Design docs & examples
    └── architecture.md
```

---

## Setup & Installation

1. **Clone the repo**

   ```bash
   git clone
   cd  your-folder
   ```
2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. **Google Cloud Credentials**

   * Create or download a Service Account JSON key in your GCP project with BigQuery permissions.
   * Place the JSON file (e.g. `bq-creds.json`) in your project root or secure directory.

2. **Environment Variables**

   * Create a `.env` file at the project root with the following entries:

     ```dotenv
     BQ_CREDENTIALS=./bq-creds.json
     PROJECT_ID=your_gcp_project_id
     DATASET_ID=your_bigquery_dataset
     GEMINI_API_KEY=your_gemini_api_key_here
     GEMINI_Model=gemini-model-name
     ```

3. **System Prompt Enhancement**

   * To speed up the AI's SQL generation, explicitly include fully-qualified table names in the system prompt. Example insertion in `main.py` or your prompt template:

     ```python
     SYSTEM_PROMPT = f"""
     You are a SQL assistant. The available BigQuery tables are:
       - {DATASET_ID}.customers`
       - {DATASET_ID}.orders`
       - {DATASET_ID}.products`
     Use these names when generating queries. Respond only with valid SQL.
     """
     ```

---

## Running the App

With your virtual environment active and `.env` configured, launch the Gradio interface:

```bash
python src/main.py
```

This will start a local web server (default `http://127.0.0.1:7860`) where you can interact with the assistant.

---

## Testing

Run unit tests with:

```bash
pytest --maxfail=1 --disable-warnings -q
```

---


*Happy querying!*
