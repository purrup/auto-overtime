"""JSON 資料處理工具

提供 JSON 檔案的讀取、更新功能。
"""

import json
from pathlib import Path


class JSONDataHandler:
    """JSON 檔案處理工具類別"""

    @staticmethod
    def load_result(file_path: Path) -> dict:
        """載入 JSON 檔案

        Args:
            file_path: JSON 檔案路徑

        Returns:
            解析後的字典

        Raises:
            FileNotFoundError: 檔案不存在
            json.JSONDecodeError: JSON 格式錯誤
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到檔案：{file_path}") from None
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON 格式錯誤：{e.msg}", e.doc, e.pos) from e

    @staticmethod
    def update_entries(file_path: Path, entries: list[dict]) -> None:
        """更新 JSON 檔案中的 recognition_results 欄位

        Args:
            file_path: JSON 檔案路徑
            entries: 辨識記錄列表

        Raises:
            FileNotFoundError: 檔案不存在
            json.JSONDecodeError: JSON 格式錯誤
        """
        # 讀取現有 JSON
        data = JSONDataHandler.load_result(file_path)

        # 更新欄位
        data["recognition_results"] = entries
        data["total_entries"] = len(entries)

        # 寫回檔案
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
