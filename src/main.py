#!/usr/bin/env python3
"""
加班單辨識自動化系統
FastAPI Web 應用程式進入點
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.config import Config
from src.routers import ocr

# 取得專案路徑
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

# 定義目錄路徑
STATIC_DIR = SRC_DIR / "static"
TEMPLATES_DIR = SRC_DIR / "templates"
UPLOADS_DIR = PROJECT_ROOT / "uploads"

# 建立 FastAPI 應用程式
app = FastAPI(
    title="加班單辨識系統",
    description="使用 AI 視覺模型將手寫加班單自動轉換為結構化數位報表",
    version="1.0.0",
)

# 建立必要目錄
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 設定 Jinja2 模板引擎
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 初始化路由並包含
ocr.init_router(templates_instance=templates, uploads_dir=UPLOADS_DIR)
app.include_router(ocr.router)


@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件

    驗證配置並顯示啟動資訊。
    """
    print("=" * 50)
    print("加班單辨識系統 - Web 版")
    print("=" * 50)

    # 驗證配置（不會拋出異常，只顯示警告）
    try:
        Config.validate()
    except Exception as e:
        print(f"! 配置警告：{e}")
        print("  請確保 .env 檔案中設定了正確的 OPENAI_API_KEY")

    print(f"靜態檔案目錄：{STATIC_DIR}")
    print(f"模板目錄：{TEMPLATES_DIR}")
    print(f"上傳目錄：{UPLOADS_DIR}")
    print(f"輸出目錄：{Config.OUTPUT_DIR}")
    print("=" * 50)


# 開發模式執行
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(SRC_DIR)],
    )
