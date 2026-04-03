import os

from langchain_openai import ChatOpenAI

from app import Config

class ChatModel:
    def __init__(self, api_key: str = ""):
        resolved_api_key = api_key or Config.DEEPBRICKS_API_KEY
        client_kwargs = {
            "model_name": "gpt-4o-mini",
            "openai_api_key": resolved_api_key,
        }

        custom_api_base = os.getenv("OPENAI_API_BASE", "").strip()
        if custom_api_base:
            client_kwargs["openai_api_base"] = custom_api_base
        elif not api_key and Config.DEEPBRICKS_API_KEY:
            client_kwargs["openai_api_base"] = "https://api.deepbricks.ai/v1/"

        self.llm = ChatOpenAI(**client_kwargs)
