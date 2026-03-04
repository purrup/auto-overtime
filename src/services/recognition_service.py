"""加班單辨識服務

封裝 OCR 辨識的核心業務邏輯，包含：
- 圖片編碼
- Vision API 調用
- 結果儲存
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from src.ai_extraction.gemini_provider import GeminiAPIError
from src.ai_extraction.openai_provider import VisionAPIError
from src.ai_extraction.provider_factory import get_vision_provider
from src.config import Config
from src.data_handling.json_handler import JSONDataHandler
from src.image_processing.encoder import ImageEncoder, ImageEncodingError
from src.models.overtime import OvertimeDocument


class RecognitionError(Exception):
    """辨識錯誤異常"""

    pass


class RecognitionService:
    """加班單辨識服務

    提供圖片 OCR 辨識功能，整合圖片編碼、AI 辨識和結果儲存。
    """

    def __init__(self, uploads_dir: Path | None = None, output_dir: Path | None = None):
        """初始化辨識服務

        Args:
            uploads_dir: 上傳檔案儲存目錄，預設為 Config.UPLOADS_DIR
            output_dir: 辨識結果儲存目錄，預設為 Config.OUTPUT_DIR
        """
        self.uploads_dir = uploads_dir or Path("uploads")
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.encoder = ImageEncoder()
        self.vision_provider = get_vision_provider()

    async def process_images(self, image_paths: list[str], session_id: str | None = None) -> dict:
        """處理多張圖片進行 OCR 辨識

        完整流程：
        1. 編碼所有圖片為 Base64
        2. 調用 Vision API 進行辨識
        3. 儲存辨識結果到 JSON 檔案

        Args:
            image_paths: 圖片檔案路徑列表
            session_id: 會話 ID，若未提供則自動生成

        Returns:
            dict: 包含以下欄位的字典：
                - session_id: 會話 ID
                - result: OvertimeDocument 辨識結果
                - token_usage: Token 使用統計
                - processing_time_seconds: 處理時間（秒）
                - output_path: 結果檔案路徑
                - image_count: 處理圖片數量
                - image_paths: 原始圖片路徑列表

        Raises:
            RecognitionError: 辨識過程中發生錯誤
        """
        if not image_paths:
            raise RecognitionError("沒有提供圖片檔案")

        # 生成或使用提供的 session_id
        if session_id is None:
            session_id = str(uuid.uuid4())

        try:
            # 步驟 1：編碼圖片
            base64_images = await self._encode_images(image_paths)

            # 步驟 2：調用 Vision API
            api_result = await self.vision_provider.recognize_batch(base64_images)

            # 步驟 3：儲存結果
            # 根據 AI Provider 取得對應的模型名稱
            if Config.AI_PROVIDER.lower() == "openai":
                model_name = Config.OPENAI_MODEL
            else:
                model_name = Config.GEMINI_MODEL

            metadata = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "provider": Config.AI_PROVIDER,
                "model": model_name,
                "image_count": len(base64_images),
                "image_paths": image_paths,
            }

            output_path = self._save_recognition_result(
                api_result=api_result,
                metadata=metadata,
                session_id=session_id,
            )

            return {
                "session_id": session_id,
                "result": api_result["result"],
                "token_usage": api_result["token_usage"],
                "processing_time_seconds": api_result["processing_time_seconds"],
                "output_path": str(output_path),
                "image_count": len(base64_images),
                "image_paths": image_paths,
            }

        except ImageEncodingError as e:
            raise RecognitionError(f"圖片編碼失敗：{str(e)}") from e
        except (VisionAPIError, GeminiAPIError) as e:
            raise RecognitionError(f"AI 辨識失敗：{str(e)}") from e
        except Exception as e:
            raise RecognitionError(f"辨識過程發生錯誤：{str(e)}") from e

    async def _encode_images(self, image_paths: list[str]) -> list[str]:
        """編碼多張圖片為 Base64

        Args:
            image_paths: 圖片檔案路徑列表

        Returns:
            Base64 編碼字串列表
        """
        base64_images = []

        for image_path in image_paths:
            path = Path(image_path)

            # 驗證檔案大小
            self.encoder.validate_image_size(path)

            # 編碼圖片
            base64_image = self.encoder.encode_image(path)
            base64_images.append(base64_image)

        return base64_images

    def _save_recognition_result(
        self,
        api_result: dict,
        metadata: dict,
        session_id: str,
    ) -> Path:
        """儲存辨識結果到 JSON 檔案

        Args:
            api_result: API 回應結果
            metadata: 中繼資料
            session_id: 會話 ID

        Returns:
            輸出檔案路徑
        """
        # 確保輸出目錄存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 使用 session_id 作為檔名
        filename = f"{session_id}.json"
        output_path = self.output_dir / filename

        # 組合輸出資料
        result: OvertimeDocument = api_result["result"]
        output_data = {
            "metadata": metadata,
            "recognition_results": [entry.model_dump() for entry in result.entries],
            "total_entries": len(result.entries),
            "token_usage": api_result["token_usage"],
            "processing_time_seconds": api_result["processing_time_seconds"],
        }

        # 寫入 JSON 檔案
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return output_path

    def get_result(self, session_id: str) -> dict | None:
        """取得指定會話的辨識結果

        Args:
            session_id: 會話 ID

        Returns:
            辨識結果字典，若不存在則返回 None
        """
        result_path = self.output_dir / f"{session_id}.json"

        if not result_path.exists():
            return None

        return JSONDataHandler.load_result(result_path)

    def update_entries(self, session_id: str, entries: list[dict]) -> None:
        """更新指定會話的辨識記錄

        Args:
            session_id: 會話 ID
            entries: 更新後的辨識記錄列表

        Raises:
            FileNotFoundError: 會話不存在
        """
        result_path = self.output_dir / f"{session_id}.json"

        if not result_path.exists():
            raise FileNotFoundError(f"找不到會話：{session_id}")

        JSONDataHandler.update_entries(result_path, entries)

    def get_image_path(self, session_id: str, filename: str) -> Path | None:
        """取得上傳圖片的實際路徑

        Args:
            session_id: 會話 ID
            filename: 圖片檔名

        Returns:
            圖片檔案路徑，若不存在則返回 None
        """
        # 圖片存放在 uploads/{session_id}/ 目錄下
        image_path = self.uploads_dir / session_id / filename

        if image_path.exists():
            return image_path

        return None
