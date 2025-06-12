import pytest
from unittest.mock import patch
from src.bq_query_assistant import tools
from src.bq_query_assistant.assistant import BQQueryAssistant
import json


@patch("src.bq_query_assistant.tools.bq_client")
def test_get_table_schema(mock_bq_client):
    # Mock the BigQuery client and its methods
    mock_table = mock_bq_client.get_table.return_value
    mock_table.schema = [
        {"name": "column1", "field_type": "STRING"},
        {"name": "column2", "field_type": "INTEGER"},
    ]

    # Call the function
    schema = tools.get_table_schema("test_table")

    # Assert the result
    assert "column1 (STRING)" in schema
    assert "column2 (INTEGER)" in schema


@patch("src.bq_query_assistant.tools.bq_client")
def test_run_sql_query_success(mock_bq_client):
    # Mock the BigQuery client and its methods
    mock_result = mock_bq_client.query.return_value
    mock_result.result.return_value.to_dataframe.return_value.to_dict.return_value = [
        {"col1": "val1", "col2": 123},
        {"col1": "val2", "col2": 456},
    ]

    # Call the function
    result = tools.run_sql_query("SELECT * FROM test_table")

    # Assert the result
    assert result == [{"col1": "val1", "col2": 123}, {"col1": "val2", "col2": 456}]


@patch("src.bq_query_assistant.tools.bq_client")
def test_run_sql_query_failure(mock_bq_client):
    # Mock the BigQuery client to raise an exception
    mock_bq_client.query.side_effect = Exception("Query failed")

    # Call the function
    result = tools.run_sql_query("SELECT * FROM test_table")

    # Assert the result
    assert "error" in result


def test_record_unknown_question(caplog):
    # Call the function
    question = "What is the meaning of life?"
    result = tools.record_unknown_question(question)

    # Assert the result and check the log
    assert result == {"recorded": True}
    assert question in caplog.text


# Mocking OpenAI and other dependencies for BQQueryAssistant tests
@pytest.fixture
def mock_openai(monkeypatch):
    class MockChatCompletion:
        def __init__(self, content, finish_reason="stop", tool_calls=None):
            self.choices = [
                type(
                    "obj",
                    (object,),
                    {
                        "message": type(
                            "obj",
                            (object,),
                            {"content": content, "tool_calls": tool_calls},
                        ),
                        "finish_reason": finish_reason,
                    },
                )()
            ]

    class MockOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        @property
        def chat(self):
            return self

        @property
        def completions(self):
            return self

        def create(self, *args, **kwargs):
            messages = kwargs.get("messages", [])
            if any(
                "get_table_schema" in m["content"] for m in messages if "content" in m
            ):
                return MockChatCompletion(
                    content="Table schema: col1 STRING, col2 INTEGER"
                )
            elif any("nl_to_sql" in m["content"] for m in messages if "content" in m):
                return MockChatCompletion(content="SELECT * FROM table")
            elif any(
                "run_sql_query" in m["content"] for m in messages if "content" in m
            ):
                return MockChatCompletion(content=json.dumps([{"result": "success"}]))
            else:
                # Simulate a final answer from the assistant
                return MockChatCompletion(content="The answer is 42.")

    monkeypatch.setattr("src.bq_query_assistant.assistant.OpenAI", MockOpenAI)


def test_bq_query_assistant_chat(mock_openai):
    assistant = BQQueryAssistant()
    response = assistant.chat("What is the meaning of life?", [])
    assert response == "The answer is 42."


def test_bq_query_assistant_tool_calls(mock_openai):
    assistant = BQQueryAssistant()
    # Mock tool call
    tool_calls = [
        type(
            "obj",
            (object,),
            {
                "id": "tool_call_1",
                "function": type(
                    "obj",
                    (object,),
                    {
                        "name": "get_table_schema",
                        "arguments": json.dumps({"table_name": "test"}),
                    },
                ),
            },
        )
    ]
    results = assistant.handle_tool_call(tool_calls)
    assert len(results) == 1
    assert results[0]["role"] == "tool"


def test_bq_query_assistant_handle_tool_call_no_module(mock_openai):
    assistant = BQQueryAssistant()
    # Mock tool call with a non-existent tool
    tool_calls = [
        type(
            "obj",
            (object,),
            {
                "id": "tool_call_1",
                "function": type(
                    "obj", (object,), {"name": "non_existent_tool", "arguments": "{}"}
                ),
            },
        )
    ]
    with pytest.raises(RuntimeError):
        assistant.handle_tool_call(tool_calls)
