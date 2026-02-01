"""圖片編碼模組

負責將圖片檔案編碼為 Base64 字串，並提供檔案大小驗證功能。
"""

import base64
from pathlib import Path


class ImageEncodingError(Exception):
    """圖片編碼錯誤異常"""

    pass


class ImageEncoder:
    """圖片編碼器，將圖片轉換為 Base64 字串"""

    # 常數：最大圖片大小限制（MB）
    MAX_IMAGE_SIZE_MB = 20

    @staticmethod
    def encode_image(image_path: Path) -> str:
        """將圖片編碼為 Base64 字串

        此方法會先驗證圖片大小，然後將圖片檔案讀取並編碼為 Base64 字串。
        編碼後的字串可用於傳送至 OpenAI Vision API 等服務。

        Args:
            image_path: 圖片檔案路徑

        Returns:
            Base64 編碼的字串

        Raises:
            FileNotFoundError: 檔案不存在
            ValueError: 圖片過大（超過 20MB）
            ImageEncodingError: 編碼失敗
        """
        # 檢查檔案是否存在
        if not image_path.exists():
            raise FileNotFoundError(f"找不到圖片檔案：{image_path}")

        # 驗證圖片大小
        try:
            ImageEncoder.validate_image_size(image_path)
        except ValueError as e:
            raise e

        # 編碼圖片為 Base64
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                return encoded_string
        except OSError as e:
            raise ImageEncodingError(f"讀取圖片檔案失敗：{e}") from e
        except Exception as e:
            raise ImageEncodingError(f"圖片編碼失敗：{e}") from e

    @staticmethod
    def validate_image_size(image_path: Path) -> None:
        """驗證圖片大小（最大 20MB）

        檢查圖片檔案大小是否在允許範圍內。OpenAI Vision API 對圖片大小有限制，
        此方法確保圖片不超過設定的上限。

        Args:
            image_path: 圖片檔案路徑

        Raises:
            ValueError: 圖片過大（超過 20MB）
        """
        size_mb = ImageEncoder.get_image_size_kb(image_path) / 1024
        max_size_mb = ImageEncoder.MAX_IMAGE_SIZE_MB

        if size_mb > max_size_mb:
            raise ValueError(f"圖片大小超過限制：{size_mb:.2f} MB（最大允許：{max_size_mb} MB）")

    @staticmethod
    def get_image_size_kb(image_path: Path) -> float:
        """取得圖片大小（KB）

        計算指定圖片檔案的大小，以 KB 為單位。

        Args:
            image_path: 圖片檔案路徑

        Returns:
            圖片大小（KB），四捨五入至小數點後兩位
        """
        size_bytes = image_path.stat().st_size
        return round(size_bytes / 1024, 2)
