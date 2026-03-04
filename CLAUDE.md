# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

加班單辨識自動化系統 - 使用 AI 視覺模型將手寫加班單掃描檔自動轉換為結構化數位報表。

## 技術架構

### 核心技術棧
- **後端框架**: FastAPI (Python async web framework)
  - 部署目標: Render
  - 支援非同步處理，適合 AI API 調用
- **前端**: Jinja2 模板 + 原生 JavaScript
  - 伺服器端渲染 (SSR)
  - 拖放上傳、可編輯表格、圖片預覽
- **AI 引擎**: 多 Provider 支援（預設 Gemini）
  - **Google Gemini** (預設): `gemini-3-flash-preview`
  - **OpenAI GPT**: `gpt-4o-mini`
  - 透過 `AI_PROVIDER` 環境變數切換
  - Structured Outputs 確保回應格式正確
  - 特別優化繁體中文手寫字跡辨識

### 專案結構

```
src/
├── main.py                    # FastAPI 應用入口
├── config.py                  # 環境變數管理
├── models/
│   └── overtime.py            # Pydantic 資料模型
├── services/
│   └── recognition_service.py # 業務邏輯層
├── routers/
│   └── ocr.py                 # API 路由
├── ai_extraction/
│   ├── base_provider.py       # Vision Provider 抽象介面
│   ├── openai_provider.py     # OpenAI Vision API 實作
│   ├── gemini_provider.py     # Google Gemini Vision API 實作
│   ├── provider_factory.py    # Provider 工廠
│   └── prompt_templates.py    # AI Prompt 範本
├── image_processing/
│   └── encoder.py             # 圖片 Base64 編碼
├── data_handling/
│   └── json_handler.py        # JSON 檔案處理
├── templates/                 # Jinja2 模板
│   ├── base.html
│   ├── index.html             # 首頁（上傳）
│   └── result.html            # 結果頁（編輯）
└── static/
    ├── css/style.css
    └── js/app.js
```

### API 端點

| 方法 | 路徑 | 功能 |
|------|------|------|
| GET | `/` | 首頁（上傳表單） |
| POST | `/upload` | 上傳檔案並執行 OCR |
| GET | `/result/{session_id}` | 顯示辨識結果 |
| POST | `/api/update/{session_id}` | 更新編輯後的資料 |
| GET | `/image/{session_id}/{filename}` | 提供圖片預覽 |

## 開發環境

### 虛擬環境 (CRITICAL)

**⚠️ 絕對要求: 永遠使用專案的虛擬環境來運行 Python**

```bash
# 安裝依賴
.venv/bin/pip install -r requirements.txt

# 啟動開發伺服器
.venv/bin/uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# 或使用 python -m
.venv/bin/python -m uvicorn src.main:app --reload
```

訪問 http://127.0.0.1:8000

### 環境變數

建立 `.env` 檔案：
```bash
# AI Provider 設定（gemini 或 openai）
AI_PROVIDER=gemini

# Gemini 設定（預設 Provider）
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3-flash-preview

# OpenAI 設定（備用）
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

## 開發注意事項

- **多 Provider 架構**: 使用 Provider 抽象層和工廠模式，支援 Gemini 和 OpenAI
- **非同步設計**: Vision Provider 使用 async/await，路由和服務層都是 async
- **AI Prompt 設計是核心**: 需要針對特定的表格格式與繁體中文手寫字調校
- **Session 管理**: 使用 UUID 作為 session_id 追蹤每次辨識會話
- **自動儲存**: 前端使用 debounce 防抖，編輯後 500ms 自動儲存
