# 智慧型加班單辨識自動化系統

使用 AI 視覺模型將手寫加班單掃描檔自動轉換為結構化數位報表。

## 功能特色

- 支援批次處理加班單掃描檔 (PDF/PNG/JPG)
- GPT Vision API 智慧辨識手寫內容
- 互動式校對介面 (並排對照原始單據與辨識結果)
- 一鍵匯出 Excel/CSV 格式

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
pip install -e ".[dev]"  # 包含開發工具
```

## 使用

```bash
./run.sh
```
or
```bash
source .venv/bin/activate && python -m src.main 2>&1 | head -50 &
```

## 技術架構

- **前端**: Flet (跨平台 Python UI 框架)
- **AI 引擎**: OpenAI GPT Vision API
- **資料處理**: Pandas, Pydantic
