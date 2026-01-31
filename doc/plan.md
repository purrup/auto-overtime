# 智慧型加班單辨識自動化系統 - 實作計劃

## 專案概述

建立一個跨平台桌面應用程式,使用 Flet 框架和 OpenAI Vision API,將手寫加班單掃描檔自動轉換為 CSV 格式的結構化資料。

**核心工作流程**: 上傳掃描檔 → AI 辨識 → 人工校對 → 匯出 CSV

---

## 用戶需求確認

- ✅ 已有 OpenAI API Key (需提供配置介面)
- ✅ 只需要 CSV 匯出功能
- ✅ 預期批次處理 1-10 張加班單
- ✅ AI 無法辨識時標記為"無法辨識"

---

## 技術選型理由

### 為何選擇 OpenAI Vision API?

根據 context7 官方文件驗證結果:

#### 1. **技術優勢**
- **語義理解能力**: 不只做 OCR,還能理解表格結構、上下文和視覺元素
- **Prompt 工程驅動**: 用自然語言指定提取邏輯,例如"只提取手寫部分,忽略印刷框架"
- **一站式解決方案**: OCR + 結構化輸出 + 資料過濾一次完成
- **內建表格識別**: 無需額外的後處理規則即可理解表格結構

#### 2. **繁體中文支援**
- 官方限制中特別列出**日文和韓文表現欠佳,但未列出中文**
- 暗示繁體中文支援較好
- 需使用真實加班單進行 POC 測試驗證準確率

#### 3. **成本效益**
- 使用 `gpt-4.1-mini` 模型
- 1024×1024 加班單圖片 ≈ 1,659 tokens
- **單張成本: ~$0.002 USD (不到 0.1 台幣)**
- 與傳統 OCR 成本相近,但開發效率更高

#### 4. **與傳統 OCR 比較**

| 方案                | 成本/張  | 手寫辨識 | 開發複雜度   | 表格理解     |
| ------------------- | -------- | -------- | ------------ | ------------ |
| OpenAI Vision       | ~$0.002  | 優秀     | 低(Prompt)   | ✅ 原生支援   |
| Google Cloud Vision | ~$0.0015 | 良好     | 中(需後處理) | ❌ 需額外處理 |
| Tesseract           | 免費     | 差       | 高(需後處理) | ❌ 需額外處理 |

**結論**: Vision API 開發效率最高,減少大量後處理邏輯,且成本極低。

---

## 專案結構設計

```
/Users/vin/coding/auto-overtime/
├── main.py                          # 應用程式進入點
├── config.py                        # 配置管理
├── .env.example                     # 環境變數範本
├── requirements.txt                 # 依賴套件清單
├── modules/
│   ├── ui/
│   │   ├── main_view.py            # 主介面佈局
│   │   ├── file_upload.py          # 檔案上傳元件 (FilePicker + DragTarget)
│   │   ├── comparison_view.py      # 並排對照視圖 (Row 佈局)
│   │   └── editable_table.py       # 可編輯資料表格 (DataTable + TextField)
│   ├── ai_extraction/
│   │   ├── vision_client.py        # OpenAI Vision API 客戶端
│   │   ├── models.py               # Pydantic 資料模型定義
│   │   └── prompts.py              # Prompt 策略設計
│   └── data_handling/
│       ├── parser.py               # 資料解析與標準化 (日期、時間格式)
│       └── exporter.py             # CSV 匯出器
└── output/                          # CSV 輸出目錄
```

---

## 核心模組說明

### 1. UI 模組 (Flet)

**技術要點**:
- 使用 `FilePicker` 支援多檔案選擇,`DragTarget` 支援拖放
- 使用 `Row` 佈局實現並排對照視圖 (原始影像 vs AI 結果)
- 使用 `DataTable` + `TextField` 實現欄位編輯
- 支援新增/刪除列和欄位驗證

### 2. AI 辨識模組

**模型選擇**: `gpt-4.1-mini` (推薦)

**資料模型** (Pydantic):
- `OvertimeEntry`: 單筆加班記錄
  - date (日期)
  - sign_in_time (簽到時間)
  - sign_out_time (簽退時間)
  - overtime_period (加班時間)
  - reason (加班事由)
  - hours (加班時數)
- 特殊處理: AI 無法辨識時填入"無法辨識"

**Prompt 策略**:
- 強調「只辨識手寫內容,忽略印刷體表格框架」
- 使用 `detail="high"` 參數提升辨識精度
- 使用 `temperature=0.1` 提高輸出一致性
- 使用 Structured Outputs 強制 JSON 格式輸出
- 明確指定日期、時間格式要求

**API 呼叫要點**:
- 影像使用 Base64 編碼傳送
- 設定 `response_format` 使用 Pydantic 模型
- 錯誤處理與重試機制

### 3. 資料處理模組

**資料解析器**:
- 日期格式轉換 (民國年 → 西元年)
- 時間格式標準化 ("14時30分" → "14:30")
- 時數解析 ("4小時" → 4.0)

**CSV 匯出器**:
- 使用 pandas DataFrame 處理資料
- UTF-8 with BOM 編碼 (Excel 相容)
- 自動生成帶時間戳記的檔案名稱

---

## 配置管理

**環境變數** (.env):
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OUTPUT_DIR=./output
```

**config.py**: 使用 python-dotenv 載入環境變數

---

## 依賴套件清單

**requirements.txt**:
```
flet>=0.24.0              # UI 框架
openai>=1.52.0            # OpenAI API
pandas>=2.0.0             # 資料處理
pydantic>=2.0.0           # 資料驗證
python-dotenv>=1.0.0      # 環境變數管理
```

**注意**:
- 輸入只會是 PNG 圖片,不需要處理 PDF 或其他格式
- 不需要安裝 Pillow 或 pdf2image

---

## 實作步驟 (分階段)

### 第一階段: 環境設定與基礎 UI
1. 建立專案目錄結構
2. 安裝依賴套件: `pip install -r requirements.txt`
3. 建立 `.env` 檔案並設定 API Key
4. 實作 main.py 和基礎 UI 框架
5. 實作檔案上傳功能 (FilePicker + DragTarget)

**驗證**: 能夠啟動應用程式並選擇/拖放檔案

---

### 第二階段: AI 整合與測試
1. 實作 `VisionClient` (OpenAI Vision API 整合)
2. 定義 Pydantic 資料模型
3. 設計並測試 Prompt
4. 使用真實範例 (image/ 目錄) 測試辨識準確度

**驗證**: 能夠上傳圖片並看到 AI 辨識結果 (JSON 格式)

---

### 第三階段: 資料顯示與編輯
1. 實作並排對照視圖
2. 實作可編輯資料表格
3. 實作資料驗證與格式化
4. 新增/刪除列功能
5. 標記"無法辨識"欄位 (視覺提示)

**驗證**: 完整的 UI 流程,從上傳到編輯

---

### 第四階段: CSV 匯出與最佳化
1. 實作 CSV 匯出功能
2. 新增檔案儲存對話框
3. 批次處理優化 (處理 1-10 張加班單)
4. 新增進度指示器
5. 錯誤處理與使用者提示

**驗證**: 能夠匯出格式正確的 CSV 檔案

---

### 第五階段: 打包與測試
1. macOS 打包: `flet build macos`
2. Windows 打包: `flet build windows`
3. 跨平台 UI 測試
4. 效能測試 (記憶體、速度)
5. 撰寫使用說明

**驗證**: 獨立執行檔可在目標平台正常運行

---

## 關鍵檔案清單 (實作優先順序)

1. **main.py** - 應用程式進入點,整合所有模組
2. **modules/ai_extraction/prompts.py** - Prompt 策略 (直接影響準確度)
3. **modules/ai_extraction/vision_client.py** - AI 辨識核心
4. **modules/ui/main_view.py** - 主介面佈局
5. **modules/ui/editable_table.py** - 可編輯表格 (人機協作核心)
6. **modules/data_handling/exporter.py** - CSV 匯出
7. **config.py** - 配置管理

---

## 端對端驗證流程

1. 啟動應用程式: `python main.py`
2. 上傳測試圖片 (image/ 目錄中的範例)
3. 點擊"開始辨識"按鈕
4. 檢查 AI 辨識結果是否正確顯示在右側面板
5. 在資料表格中修正任何"無法辨識"的欄位
6. 點擊"匯出 CSV"按鈕
7. 檢查 output/ 目錄中的 CSV 檔案格式
8. 用 Excel 或文字編輯器開啟 CSV 驗證內容正確

---

## 技術注意事項

### 1. API Key 安全性
- 不要將 API Key 提交到 Git (.env 已在 .gitignore)
- 提供 .env.example 作為範本
- 首次啟動時可在 UI 中設定 API Key

### 2. 記憶體管理 (1-10 張批次處理)
- 逐一處理圖片,避免同時載入多張 PNG
- 使用 Base64 編碼時注意記憶體使用

### 3. 錯誤處理
- API 呼叫失敗時顯示友善錯誤訊息
- 網路連線異常時提示使用者檢查網路
- PNG 檔案無法讀取時顯示錯誤訊息

### 4. Prompt 優化策略
- 強調「只辨識手寫,忽略印刷體」
- 使用 `detail="high"` 參數提升細節辨識
- 設定 `temperature=0.1` 提高輸出一致性
- 若初期準確度不理想,可在 Prompt 中提供範例

### 5. 掃描品質要求
- 建議解析度: 300 DPI 以上
- 確保影像方向正確 (Vision API 對旋轉影像可能誤判)
- 影像清晰度影響辨識準確度

---

## 預期成果

完成實作後,使用者將獲得:
- ✅ 跨平台桌面應用程式 (macOS .app / Windows .exe)
- ✅ 直覺的拖放式檔案上傳介面
- ✅ AI 驅動的手寫字辨識 (繁體中文優化)
- ✅ 並排對照視圖 (原始單據 vs 辨識結果)
- ✅ 可編輯的資料表格 (人工校對功能)
- ✅ 一鍵匯出 CSV 功能
- ✅ 批次處理 1-10 張加班單
- ✅ 清晰標記"無法辨識"欄位

---

## POC 測試建議

在正式開發前,建議先進行 POC (Proof of Concept) 測試:

1. **建立簡單的測試腳本**,使用真實加班單圖片測試 Vision API
2. **調整 Prompt** 直到達到可接受的辨識準確度 (建議 >80%)
3. **測試繁體中文手寫字**的辨識效果
4. **驗證成本**: 確認實際 token 使用量符合預期

**POC 測試腳本範例架構**:
- 讀取 image/ 目錄中的測試圖片
- 呼叫 Vision API with 不同 Prompt 變體
- 比較辨識結果與實際內容
- 記錄 token 使用量和成本

---

