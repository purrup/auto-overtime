"""集中式日誌配置模組

提供專案級別的 logger 配置，統一日誌格式和輸出。
"""

import logging
import os
import sys


def get_logger(name: str) -> logging.Logger:
    """取得指定名稱的 logger

    Args:
        name: logger 名稱，通常使用模組名稱（如 gemini_provider）

    Returns:
        設定好格式的 logger 實例
    """
    logger = logging.getLogger(name)

    # 避免重複添加 handler
    if logger.handlers:
        return logger

    # 從環境變數讀取日誌級別，預設為 INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler（輸出到 stderr）
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    # 統一格式：時間 級別 [模組名] 訊息
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
