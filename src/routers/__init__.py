"""路由層模組

提供 FastAPI 路由定義。
"""

from src.routers.ocr import router as ocr_router

__all__ = ["ocr_router"]
