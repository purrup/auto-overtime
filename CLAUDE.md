# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

加班單辨識自動化系統 - 使用 AI 視覺模型將手寫加班單掃描檔自動轉換為結構化數位報表(Excel/CSV)。

## 技術架構

### 核心技術棧
- **前端框架**: Flet (Python-based UI framework)
  - 跨平台支援:macOS (Apple Silicon/Intel) 與 Windows 10/11
  - 本地端運行,無需後端伺服器
- **AI 引擎**: GPT 多模態模型(Vision API)
  - 用於 OCR 與表格結構識別
  - 特別優化繁體中文手寫字跡辨識
- **輸出格式**: Excel/CSV

### 系統模組設計

專案採用模組化架構,分為四大核心模組:

1. **UI Module (視覺介面模組)**
   - 檔案上傳區(支援拖放)
   - 進度指示器
   - 並排對照視圖(原始單據 vs 辨識結果)
   - 互動式資料編輯表格

2. **Image Pre-processing Module (影像前處理模組)**
   - 影像壓縮與格式轉換(PDF/PNG/JPG)
   - 影像品質優化
   - 符合 AI 模型輸入規範的預處理

3. **Intelligence Extraction Module (智慧提取模組)**
   - 與 GPT Vision API 的整合層
   - Prompt 策略設計與優化
   - 關鍵區域辨識:日期、時間、事由、時數
   - 過濾印刷體雜訊,鎖定手寫筆跡

4. **Data Handler Module (資料處理與輸出模組)**
   - 資料格式轉換與標準化
   - 時間格式處理(例:"14時16分" → 標準時間格式)
   - Excel/CSV 檔案生成

## 工作流程設計

系統遵循「人機協作」(Human-in-the-loop)原則:

1. **數位化輸入** → 使用者上傳掃描檔(批次支援)
2. **智慧辨識** → AI 提取手寫內容與關鍵資訊
3. **互動校對** → 並排對照視圖,使用者可修正 AI 誤判
4. **結構化輸出** → 一鍵匯出 Excel/CSV

## 重要配置

- **API Key 管理**: 將 OpenAI/GPT API Key 存放於環境變數或外部配置檔,不可提交至 Git
- **敏感資訊**: `.gitignore` 已設定忽略 `image/` 目錄(包含測試用的真實單據掃描檔)

## 開發環境要求

### 虛擬環境 (CRITICAL)

**⚠️ 絕對要求:永遠使用專案的虛擬環境來運行 Python**

- 本專案依賴 Flet 0.28.3 及其特定的 API 設計 (例:`ft.Icons` 而非 `ft.icons`)
- 虛擬環境確保依賴版本一致性,避免系統層級套件衝突
- 所有 Python 命令都必須使用 `.venv/bin/python`,而非系統 Python

**正確的運行方式:**
```bash
# 推薦:直接使用虛擬環境 Python
.venv/bin/python -m src.main

# 或先啟用虛擬環境
source .venv/bin/activate
python -m src.main
```

**錯誤的運行方式 (會導致模組錯誤):**
```bash
# ❌ 使用系統 Python
python -m src.main

# ❌ 使用錯誤的 Python 版本
python3 -m src.main
```

## 開發注意事項

- 這是一個注重 **UX 流暢度** 的桌面應用程式,操作步驟要極簡化
- AI Prompt 設計是核心:需要針對特定的表格格式與繁體中文手寫字調校
- 跨平台測試很重要:macOS 與 Windows 的 UI 表現需一致
- 影像檔案可能很大,需要考慮記憶體管理與批次處理效能
- **Flet API 注意事項**:Flet 0.28.3 使用 `ft.Icons` (大寫) 而非 `ft.icons`,這是常見錯誤來源
