"""OCR 辨識路由

提供加班單 OCR 辨識相關的 API 端點。
"""

import uuid
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.config import Config
from src.services.recognition_service import RecognitionError, RecognitionService

router = APIRouter()

# 模板引擎（將在 main.py 中設定）
templates: Jinja2Templates | None = None

# 服務實例
recognition_service: RecognitionService | None = None


def init_router(templates_instance: Jinja2Templates, uploads_dir: Path) -> None:
    """初始化路由

    Args:
        templates_instance: Jinja2 模板引擎實例
        uploads_dir: 上傳檔案儲存目錄
    """
    global templates, recognition_service
    templates = templates_instance
    recognition_service = RecognitionService(uploads_dir=uploads_dir)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首頁 - 顯示檔案上傳介面

    Args:
        request: FastAPI Request 物件

    Returns:
        渲染後的 HTML 頁面
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "allowed_extensions": Config.ALLOWED_EXTENSIONS,
        },
    )


@router.post("/upload")
async def upload_files(
    request: Request,
    files: Annotated[list[UploadFile], File(description="加班單圖片檔案")],
):
    """上傳檔案並執行 OCR 辨識

    處理流程：
    1. 生成 session_id
    2. 儲存上傳的檔案
    3. 執行 OCR 辨識
    4. 重導向到結果頁面

    Args:
        request: FastAPI Request 物件
        files: 上傳的檔案列表

    Returns:
        重導向到結果頁面，或錯誤回應
    """
    if not files or len(files) == 0:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "allowed_extensions": Config.ALLOWED_EXTENSIONS,
                "error": "請選擇至少一個檔案",
            },
            status_code=400,
        )

    # 驗證檔案類型
    for file in files:
        if file.filename:
            ext = file.filename.split(".")[-1].lower()
            if ext not in Config.ALLOWED_EXTENSIONS:
                return templates.TemplateResponse(
                    request=request,
                    name="index.html",
                    context={
                        "allowed_extensions": Config.ALLOWED_EXTENSIONS,
                        "error": f"不支援的檔案格式：{ext}。支援格式：{', '.join(Config.ALLOWED_EXTENSIONS).upper()}",
                    },
                    status_code=400,
                )

    # 生成 session_id
    session_id = str(uuid.uuid4())

    # 建立會話目錄
    session_dir = recognition_service.uploads_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # 儲存上傳的檔案
    saved_paths = []
    try:
        for file in files:
            if file.filename:
                file_path = session_dir / file.filename

                # 使用 aiofiles 異步寫入檔案
                async with aiofiles.open(file_path, "wb") as f:
                    content = await file.read()
                    await f.write(content)

                saved_paths.append(str(file_path))

    except Exception as e:
        # 清理已儲存的檔案
        for path in saved_paths:
            Path(path).unlink(missing_ok=True)
        session_dir.rmdir()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "allowed_extensions": Config.ALLOWED_EXTENSIONS,
                "error": f"檔案儲存失敗：{str(e)}",
            },
            status_code=500,
        )

    # 執行 OCR 辨識
    try:
        await recognition_service.process_images(
            image_paths=saved_paths,
            session_id=session_id,
        )

        # 重導向到結果頁面
        return RedirectResponse(
            url=f"/result/{session_id}",
            status_code=303,  # See Other
        )

    except RecognitionError as e:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "allowed_extensions": Config.ALLOWED_EXTENSIONS,
                "error": str(e),
            },
            status_code=500,
        )


@router.get("/result/{session_id}", response_class=HTMLResponse)
async def show_result(request: Request, session_id: str):
    """顯示辨識結果頁面

    Args:
        request: FastAPI Request 物件
        session_id: 會話 ID

    Returns:
        渲染後的結果頁面
    """
    # 取得辨識結果
    result = recognition_service.get_result(session_id)

    if result is None:
        raise HTTPException(status_code=404, detail="找不到辨識結果")

    # 計算統計資訊
    entries = result.get("recognition_results", [])
    total_hours = sum(entry.get("hours", 0) for entry in entries)
    image_count = result.get("metadata", {}).get("image_count", 0)
    image_paths = result.get("metadata", {}).get("image_paths", [])

    # 從完整路徑中提取檔名
    image_filenames = [Path(p).name for p in image_paths]

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "session_id": session_id,
            "entries": entries,
            "total_entries": len(entries),
            "total_hours": total_hours,
            "image_count": image_count,
            "image_filenames": image_filenames,
            "token_usage": result.get("token_usage", {}),
            "cost_usd": result.get("cost_usd", 0),
        },
    )


@router.post("/api/update/{session_id}")
async def update_entries(session_id: str, request: Request):
    """更新辨識記錄（JSON API）

    接收前端編輯後的資料並更新儲存的 JSON 檔案。

    Args:
        session_id: 會話 ID
        request: FastAPI Request 物件（包含 JSON body）

    Returns:
        JSON 回應表示更新成功或失敗
    """
    try:
        # 解析 JSON body
        data = await request.json()
        entries = data.get("entries", [])

        if not isinstance(entries, list):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "無效的資料格式"},
            )

        # 更新記錄
        recognition_service.update_entries(session_id, entries)

        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "更新成功"},
        )

    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "找不到辨識結果"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@router.get("/image/{session_id}/{filename}")
async def get_image(session_id: str, filename: str):
    """提供上傳圖片供前端預覽

    Args:
        session_id: 會話 ID
        filename: 圖片檔名

    Returns:
        圖片檔案回應
    """
    image_path = recognition_service.get_image_path(session_id, filename)

    if image_path is None:
        raise HTTPException(status_code=404, detail="找不到圖片檔案")

    # 根據副檔名決定 MIME type
    ext = filename.split(".")[-1].lower()
    media_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=image_path,
        media_type=media_type,
        filename=filename,
    )
