"""
AI Vision Provider 抽象介面

定義所有 AI Vision Provider 必須實作的介面。
"""

from abc import ABC, abstractmethod
from typing import TypedDict

from src.models.overtime import OvertimeDocument


class RecognitionResult(TypedDict):
    """辨識結果的型別定義"""

    result: OvertimeDocument
    token_usage: dict
    processing_time_seconds: float


class VisionProvider(ABC):
    """Vision Provider 抽象基底類別"""

    @abstractmethod
    async def recognize_batch(self, base64_images: list[str]) -> RecognitionResult:
        """
        辨識多張圖片並回傳結構化結果

        Args:
            base64_images: Base64 編碼的圖片列表

        Returns:
            RecognitionResult: 包含辨識結果、token 使用量和處理時間的字典
        """
        pass
