"""
Vision API 客戶端模組

負責與 OpenAI Vision API 通訊，處理批次圖片辨識和錯誤處理。
"""

import openai
from openai import OpenAI

from ..config import Config
from ..models.overtime import OvertimeDocument
from .prompt_templates import PromptTemplates


class VisionAPIError(Exception):
    """Vision API 錯誤異常"""

    pass


class VisionClient:
    """OpenAI Vision API 客戶端

    負責與 OpenAI Vision API 通訊，處理批次圖片辨識。
    """

    def __init__(self):
        """初始化 Vision API 客戶端

        使用 Config.OPENAI_API_KEY 和 Config.OPENAI_MODEL
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def recognize_batch(self, base64_images: list[str]) -> dict:
        """批次辨識多張圖片

        單次 API 請求處理所有圖片，使用 Structured Outputs 確保格式正確。

        Args:
            base64_images: Base64 編碼的圖片列表

        Returns:
            {
                "result": OvertimeDocument,  # Pydantic 模型
                "token_usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "cost_usd": float
            }

        Raises:
            VisionAPIError: API 呼叫失敗
        """
        try:
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
            completion = self.client.beta.chat.completions.parse(
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

            # 計算成本
            cost_usd = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)

            return {"result": result, "token_usage": token_usage, "cost_usd": cost_usd}

        except openai.AuthenticationError as e:
            raise VisionAPIError("API Key 無效，請檢查 .env 檔案中的 OPENAI_API_KEY 設定") from e
        except openai.APIConnectionError as e:
            raise VisionAPIError("網路連線失敗，請檢查網路連線後再試") from e
        except openai.RateLimitError as e:
            raise VisionAPIError("API 使用量已達上限，請稍後再試或升級方案") from e
        except Exception as e:
            raise VisionAPIError(f"API 呼叫失敗：{str(e)}") from e

    @staticmethod
    def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        """計算 API 呼叫成本

        使用 gpt-5-mini-2025-08-07 定價：
        - Input: $0.250 / 1M tokens
        - Output: $2 / 1M tokens

        Args:
            prompt_tokens: Prompt tokens 數量
            completion_tokens: Completion tokens 數量

        Returns:
            成本（美元）
        """
        input_cost = prompt_tokens * 0.25 / 1_000_000
        output_cost = completion_tokens * 2 / 1_000_000
        return round(input_cost + output_cost, 6)
