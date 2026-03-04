"""
Google Gemini Vision Provider

使用 Google Gemini API 進行加班單圖片辨識。
"""

import base64
import time

from google import genai
from google.genai import errors, types

from src.ai_extraction.base_provider import RecognitionResult, VisionProvider
from src.ai_extraction.prompt_templates import PromptTemplates
from src.config import Config
from src.models.overtime import OvertimeDocument
from src.utils.logger import get_logger

logger = get_logger("gemini_provider")


class GeminiAPIError(Exception):
    """Gemini API 錯誤異常"""

    pass


class GeminiVisionProvider(VisionProvider):
    """Google Gemini Vision API Provider"""

    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = Config.GEMINI_MODEL

    async def recognize_batch(self, base64_images: list[str]) -> RecognitionResult:
        """批次辨識多張圖片"""
        try:
            start_time = time.time()
            logger.info(f"開始 API 呼叫: model={self.model}, images={len(base64_images)}")

            # 建立 contents：prompt + 圖片
            prompt = PromptTemplates.get_overtime_recognition_prompt()
            contents = [prompt]

            for img_base64 in base64_images:
                # 將 base64 解碼為 bytes
                img_bytes = base64.b64decode(img_base64)
                contents.append(
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                )

            # 呼叫 Gemini API（非同步 + 結構化輸出）
            # Gemini 需要 JSON Schema dict，不是 Pydantic class
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OvertimeDocument.model_json_schema(),
                ),
            )

            # 解析結果
            result = OvertimeDocument.model_validate_json(response.text)

            # 取得 token 使用量
            usage = response.usage_metadata
            token_usage = {
                "prompt_tokens": usage.prompt_token_count,
                "completion_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count,
            }

            # 計算處理時間
            processing_time = round(time.time() - start_time, 2)
            logger.info(f"API 呼叫成功: tokens={token_usage['total_tokens']}, time={processing_time}s")

            return {
                "result": result,
                "token_usage": token_usage,
                "processing_time_seconds": processing_time,
            }
        except errors.APIError as e:
            error_msg = f"API 錯誤 {e.code}: {e.message}"
            logger.error(error_msg)

            if e.code == 429:
                raise GeminiAPIError("API 使用量已達上限，請稍後再試") from e
            elif e.code == 403:
                raise GeminiAPIError("API Key 權限不足，請檢查設定") from e
            elif e.code in [500, 503]:
                raise GeminiAPIError("Gemini 服務暫時不可用，請稍後再試") from e
            elif e.code == 504:
                raise GeminiAPIError("請求超時，請減少圖片數量或稍後再試") from e
            else:
                raise GeminiAPIError(f"Gemini API 呼叫失敗：{e.message}") from e
        except Exception as e:
            logger.exception("未預期的錯誤")
            raise GeminiAPIError(f"Gemini API 呼叫失敗：{str(e)}") from e
