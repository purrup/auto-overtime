# 加班單辨識自動化系統

使用 AI 視覺模型將手寫加班單掃描檔自動轉換為結構化數位報表。

## 功能特色

- 支援批次處理加班單掃描檔 (PNG/JPG)
- GPT Vision API 智慧辨識手寫內容
- 互動式校對介面（可編輯表格、圖片預覽）
- 自動儲存編輯結果

## 安裝

### 建立虛擬環境

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 環境變數

建立 `.env` 檔案：

```
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

## 使用

### 啟動伺服器

```bash
# 方式 1: VS Code 快捷鍵
Cmd+Shift+B

# 方式 2: 命令列
.venv/bin/uvicorn src.main:app --reload --port 8000
```

訪問 http://127.0.0.1:8000

### 操作流程

1. 上傳加班單圖片（支援拖放）
2. 點擊「開始辨識」
3. 在結果頁面檢視並編輯辨識結果
4. 編輯後自動儲存

## 技術架構

- **後端**: FastAPI (Python async web framework)
- **前端**: Jinja2 模板 + 原生 JavaScript
- **AI 引擎**: OpenAI GPT Vision API (AsyncOpenAI)
- **資料驗證**: Pydantic

## API 端點

| 方法 | 路徑 | 功能 |
|------|------|------|
| GET | `/` | 首頁（上傳表單） |
| POST | `/upload` | 上傳檔案並執行 OCR |
| GET | `/result/{session_id}` | 顯示辨識結果 |
| POST | `/api/update/{session_id}` | 更新編輯後的資料 |
| GET | `/image/{session_id}/{filename}` | 提供圖片預覽 |
