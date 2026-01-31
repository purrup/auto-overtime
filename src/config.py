"""
配置管理模組

負責載入環境變數並驗證配置完整性。
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置錯誤異常類別"""
    pass


class Config:
    """
    應用程式配置類別

    包含所有系統配置常數，並提供配置驗證功能。
    """

    # 載入環境變數
    load_dotenv()

    # API 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")

    # 檔案配置
    ALLOWED_EXTENSIONS: tuple = ("png", "jpg", "jpeg")
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output"))

    # 應用程式 UI 配置
    APP_TITLE: str = "智慧型加班單辨識系統"
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800

    @classmethod
    def validate(cls) -> None:
        """
        驗證配置完整性

        檢查必要的配置項目是否存在且有效，並建立必要的目錄。

        Raises:
            ConfigError: 當配置無效時拋出異常
        """
        # 檢查 API Key 是否存在
        if not cls.OPENAI_API_KEY:
            raise ConfigError(
                "找不到 OPENAI_API_KEY 環境變數\n"
                "請建立 .env 檔案並設定 OPENAI_API_KEY=your-api-key"
            )

        # 檢查是否為範例值
        if cls.OPENAI_API_KEY == "sk-your-api-key-here":
            raise ConfigError(
                "請設定有效的 OPENAI_API_KEY（目前為範例值）"
            )

        # 建立輸出目錄
        try:
            cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            print(f"✓ 輸出目錄已準備: {cls.OUTPUT_DIR.absolute()}")
        except Exception as e:
            raise ConfigError(f"無法建立輸出目錄 {cls.OUTPUT_DIR}: {e}")

        # 驗證成功訊息
        print(f"✓ OpenAI API Key 已載入")
        print(f"✓ 使用模型: {cls.OPENAI_MODEL}")
        print(f"✓ 支援格式: {', '.join(cls.ALLOWED_EXTENSIONS).upper()}")
        print("✓ 配置驗證完成\n")
