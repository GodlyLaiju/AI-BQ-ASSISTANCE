import json
import logging
import importlib

from openai import OpenAI

from bq_query_assistant.config import GOOGLE_API_KEY, GOOGLE_GEMINI_MODEL
from .system_prompt import main_system_prompt

TOOLS_MODULE = "bq_query_assistant.tools"
# Configure logging
logging.basicConfig(level=logging.INFO)

FUNCTION_MODULE_MAP = {
    "get_table_schema": TOOLS_MODULE,
    "run_sql_query": TOOLS_MODULE,
    "record_unknown_question": TOOLS_MODULE,
    "nl_to_sql": "bq_query_assistant.nl_sql_model",
}

# Tools metadata
tools_metadata = [
    {
        "type": "function",
        "function": {
            "name": "get_table_schema",
            "description": "Fetch schema.",
            "parameters": {
                "type": "object",
                "properties": {"table_name": {"type": "string"}},
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql_query",
            "description": "Execute SQL.",
            "parameters": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "Log questions.",
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nl_to_sql",
            "description": "NL→SQL converter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nl_question": {"type": "string"},
                    "table_schema": {"type": "string"},
                },
                "required": ["nl_question", "table_schema"],
            },
        },
    },
]


class BQQueryAssistant:
    def __init__(self):
        self.client = OpenAI(
            api_key=GOOGLE_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    def handle_tool_call(self, tool_calls):
        results = []
        for call in tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)

            module_name = FUNCTION_MODULE_MAP.get(name)
            if not module_name:
                raise RuntimeError(f"No module mapping for tool {name}")
            module = importlib.import_module(module_name)
            fn = getattr(module, name)
            logging.info(f"Calling function {name}")
            output = fn(**args)
            results.append(
                {
                    "role": "tool",
                    "content": json.dumps(output),
                    "tool_call_id": call.id,
                }
            )
        return results

    def chat(self, message, history):

        messages = (
            [{"role": "system", "content": main_system_prompt()}]
            + history
            + [{"role": "user", "content": message}]
        )
        done = False
        while not done:
            response = self.client.chat.completions.create(
                model=GOOGLE_GEMINI_MODEL,
                messages=messages,
                tools=tools_metadata,
                tool_choice="auto",
            )
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
