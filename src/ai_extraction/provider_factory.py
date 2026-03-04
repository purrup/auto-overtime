"""
Vision Provider 工廠模組

根據配置選擇並建立對應的 Vision Provider 實例。
"""

from src.ai_extraction.base_provider import VisionProvider
from src.config import Config


def get_vision_provider() -> VisionProvider:
    """根據配置取得對應的 Vision Provider

    Returns:
        VisionProvider 實例

    Raises:
        ValueError: 不支援的 Provider 類型
    """
    provider = Config.AI_PROVIDER.lower()

    if provider == "openai":
        from src.ai_extraction.openai_provider import OpenAIVisionProvider

        return OpenAIVisionProvider()
    elif provider == "gemini":
        from src.ai_extraction.gemini_provider import GeminiVisionProvider

        return GeminiVisionProvider()
    else:
        raise ValueError(f"不支援的 AI Provider: {provider}")
