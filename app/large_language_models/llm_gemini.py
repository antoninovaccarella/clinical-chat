from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from app import Config


rate_limiter = InMemoryRateLimiter(
    requests_per_second=2,  # <-- Super slow! We can only make a request once every 20 seconds!!
    check_every_n_seconds=0.5,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)


class ChatModel:
    def __init__(self, api_key: str = ""):
        resolved_api_key = api_key or Config.GEMINI_API_2 or Config.GEMINI_API
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=resolved_api_key,
            model="gemini-3-flash-preview",
            temperature=0,
            top_p= 0.95,
            top_k= 40,
            max_output_tokens= 8192,
            timeout=None,
            max_retries=5,
            rate_limiter=rate_limiter,
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )


