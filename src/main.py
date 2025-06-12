import gradio as gr
from bq_query_assistant.assistant import BQQueryAssistant

if __name__ == "__main__":
    iface = gr.ChatInterface(BQQueryAssistant().chat, type="messages")
    iface.launch()
