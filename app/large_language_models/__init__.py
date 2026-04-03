from app.large_language_models.llm_deepseek_r1 import ChatModel as DeepSeekR1Model
from app.large_language_models.llm_deepseek_v3 import ChatModel as DeepSeekV3Model
from app.large_language_models.llm_gemini import ChatModel as GeminiModel


AVAILABLE_MODELS = {
    "gemini": GeminiModel,
    "deepseek-v3": DeepSeekV3Model,
    "deepseek-r1": DeepSeekR1Model,
}


def get_chat_model(model_name: str = "", api_key: str = ""):
    normalized_name = (model_name or "gemini").strip().lower()
    model_class = AVAILABLE_MODELS.get(normalized_name, GeminiModel)
    return model_class(api_key=api_key).llm
