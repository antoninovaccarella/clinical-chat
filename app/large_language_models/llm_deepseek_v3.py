import os

from langchain_core.rate_limiters import InMemoryRateLimiter

from app import Config
from langchain_deepseek import ChatDeepSeek

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = Config.DEEPSEEK_API_KEY

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.3,
    check_every_n_seconds=2,  # Wake up every 200 ms to check whether allowed to make a request,
    max_bucket_size=2,  # Controls the maximum burst size.
)

class ChatModel:
    def __init__(self, api_key: str = ""):
        resolved_api_key = api_key or Config.DEEPSEEK_API_KEY
        if resolved_api_key:
            os.environ["DEEPSEEK_API_KEY"] = resolved_api_key
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=8192,
            timeout=30,
            max_retries=3,
            rate_limiter=rate_limiter,
        )
