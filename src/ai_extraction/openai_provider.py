"""
OpenAI Vision Provider 模組

實作 VisionProvider 介面，負責與 OpenAI Vision API 通訊，處理批次圖片辨識和錯誤處理。
"""

import time

import openai
from openai import AsyncOpenAI

from src.ai_extraction.base_provider import RecognitionResult, VisionProvider
from src.ai_extraction.prompt_templates import PromptTemplates
from src.config import Config
from src.models.overtime import OvertimeDocument


class VisionAPIError(Exception):
    """Vision API 錯誤異常"""

    pass


class OpenAIVisionProvider(VisionProvider):
    """OpenAI Vision API Provider

    實作 VisionProvider 介面，負責與 OpenAI Vision API 通訊，處理批次圖片辨識。
    """

    def __init__(self):
        """初始化 OpenAI Vision Provider

        使用 Config.OPENAI_API_KEY 和 Config.OPENAI_MODEL
        """
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    async def recognize_batch(self, base64_images: list[str]) -> RecognitionResult:
        """批次辨識多張圖片

        單次 API 請求處理所有圖片，使用 Structured Outputs 確保格式正確。

        Args:
            base64_images: Base64 編碼的圖片列表

        Returns:
            RecognitionResult: 包含辨識結果、token 使用量和處理時間的字典
                {
                    "result": OvertimeDocument,  # Pydantic 模型
                    "token_usage": {
                        "prompt_tokens": int,
                        "completion_tokens": int,
                        "total_tokens": int
                    },
                    "processing_time_seconds": float
                }

        Raises:
            VisionAPIError: API 呼叫失敗
        """
        try:
            start_time = time.time()

            # 取得 Prompt 範本
            prompt = PromptTemplates.get_overtime_recognition_prompt()

            # 建立 content 陣列
            content = [
                {"type": "text", "text": prompt},
            ]

            # 加入所有圖片
            for base64_image in base64_images:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high",  # 提升辨識精度
                        },
                    }
                )

            # 呼叫 OpenAI Vision API（使用 Structured Outputs）
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                response_format=OvertimeDocument,  # Structured Outputs
            )

            # 從 API 回應中取得結構化結果
            result = completion.choices[0].message.parsed  # OvertimeDocument 實例

            # 取得 token 使用統計
            usage = completion.usage
            token_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }

            # 計算處理時間
            processing_time = round(time.time() - start_time, 2)

            return {"result": result, "token_usage": token_usage, "processing_time_seconds": processing_time}

        except openai.AuthenticationError as e:
            raise VisionAPIError("API Key 無效，請檢查 .env 檔案中的 OPENAI_API_KEY 設定") from e
        except openai.APIConnectionError as e:
            raise VisionAPIError("網路連線失敗，請檢查網路連線後再試") from e
        except openai.RateLimitError as e:
            raise VisionAPIError("API 使用量已達上限，請稍後再試或升級方案") from e
        except Exception as e:
            raise VisionAPIError(f"API 呼叫失敗：{str(e)}") from e

