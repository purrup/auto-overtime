# 辨識自動化系統

使用 AI 視覺模型將手寫加班單掃描檔自動轉換為結構化數位報表。

## 功能特色

- 支援批次處理加班單掃描檔 (PDF/PNG/JPG)
- GPT Vision API 智慧辨識手寫內容
- 互動式校對介面 (並排對照原始單據與辨識結果)
- 一鍵匯出 Excel/CSV 格式

## 安裝

### 建立虛擬環境

**⚠️ 重要:本專案必須使用虛擬環境運行,以確保依賴版本一致性**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
pip install -e ".[dev]"  # 包含開發工具
```

### 驗證虛擬環境

確認您正在使用專案的虛擬環境:

```bash
which python  # 應顯示 .../auto-overtime/.venv/bin/python
```

## 使用

### 啟動應用程式

**⚠️ 永遠使用專案虛擬環境中的 Python 運行**

```bash
./run.sh
```

或手動啟動:

```bash
# 方式 1: 啟用虛擬環境後運行
source .venv/bin/activate && python -m src.main

# 方式 2: 直接使用虛擬環境 Python (推薦)
.venv/bin/python -m src.main
```

## 技術架構

- **前端**: Flet (跨平台 Python UI 框架)
- **AI 引擎**: OpenAI GPT Vision API
- **資料處理**: Pandas, Pydantic
