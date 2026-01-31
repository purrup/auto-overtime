#!/usr/bin/env python3
"""
POC 測試腳本：OpenAI Vision API 繁體中文手寫加班單辨識
驗證使用 OpenAI Vision API 辨識手寫加班單的可行性
"""

import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# ============================================================
# 1. Pydantic 資料模型定義
# ============================================================

class OvertimeEntry(BaseModel):
    """單筆加班記錄"""

    employee_name: str = Field(
        description="員工姓名，從「簽到（退）簽」欄位中的手寫簽名辨識。若無法辨識填入「無法辨識」"
    )

    date: str = Field(
        description="加班日期，格式為 YYYY-MM-DD。若為民國年則需轉換為西元年（民國年+1911=西元年）。若無法辨識填入「無法辨識」"
    )

    overtime_start_time: str = Field(
        description="加班時間（起），格式為 HH:MM（24小時制）。例如：08:00。若無法辨識填入「無法辨識」"
    )

    overtime_end_time: str = Field(
        description="加班時間（迄），格式為 HH:MM（24小時制）。例如：09:00。若無法辨識填入「無法辨識」"
    )

    overtime_reason: str = Field(
        description="加班事由，完整的手寫文字內容。若無法辨識填入「無法辨識」"
    )

    overtime_type: str = Field(
        description="加班類型，例如「加班費」、「補休」等。若無法辨識填入「無法辨識」"
    )

    hours: float = Field(
        description="加班時數，數值型態，單位為小時。例如：1.0 表示 1 小時。若無法辨識填入 0.0"
    )


class OvertimeDocument(BaseModel):
    """整張加班單文件（可包含多筆記錄）"""

    entries: List[OvertimeEntry] = Field(
        description="加班記錄列表，每一列代表一筆加班記錄。如果圖片中只有一筆記錄，列表就只有一個元素。"
    )


# ============================================================
# 2. 工具函數
# ============================================================

def encode_image_to_base64(image_path: Path) -> str:
    """將圖片編碼為 Base64 字串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_size_kb(image_path: Path) -> float:
    """取得圖片大小（KB）"""
    size_bytes = image_path.stat().st_size
    return round(size_bytes / 1024, 2)


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """
    計算 API 呼叫成本（gpt-5-mini-2025-08-07 定價）
    Input: $0.250 / 1M tokens
    Output: $2 / 1M tokens
    """
    input_cost = prompt_tokens * 0.25 / 1_000_000
    output_cost = completion_tokens * 2 / 1_000_000
    return round(input_cost + output_cost, 6)


def create_prompt() -> str:
    """建立 Vision API 的 Prompt"""
    return """你是一個專業的繁體中文文字辨識專家，擅長辨識手寫及印刷體的繁體中文。

請仔細觀察這張加班單掃描圖片，**辨識表格中所有的加班記錄列**。

**重要**：
- 一張圖片可能包含多筆加班記錄（多列）
- 請逐列辨識，每一列都是一筆獨立的加班記錄
- 主要辨識手寫內容，但「加班事由」欄位通常是印刷體，也需要讀取

對於每一筆加班記錄，請提取以下資訊：

1. **員工姓名**：從「簽到（退）簽」欄位中的手寫簽名辨識

2. **日期**：找到日期欄位的手寫內容
   - 如果是民國年（例如 114），請轉換為西元年（民國年 + 1911 = 西元年）
   - 輸出格式：YYYY-MM-DD（例如：2025-11-22）

3. **加班時間（起）**：找到「加班時間」表格中「起」欄位的手寫內容
   - 輸出格式：HH:MM（24小時制，例如：08:00）

4. **加班時間（迄）**：找到「加班時間」表格中「迄」欄位的手寫內容
   - 輸出格式：HH:MM（24小時制，例如：09:00）

5. **加班事由**：找到「加 班 事 由」欄位的內容
   - **注意**：此欄位通常是印刷體/打字內容，不是手寫
   - **請讀取該欄位格子內的完整內容，包括括號內的補充說明**
   - **絕對不要讀取加 班 事 由」欄位右邊的「無法線上申請事由」欄位下方的印刷體/打字內容**
   - **只讀取表格主體內「加班事由」欄位中對應該列的完整文字**
   - 如果該欄位有多行文字，請完整讀取所有內容

6. **申請類別**：找到「加班」或「補休」欄位中的印刷體內容
   - 此欄位的值需要配合 「時數」 欄位來判斷, 「時數」 欄位不為 0 小時的選項才是申請類別的值
        -e.g. |加班費 | 0 小時 |
              |補休   | 2 小時 |
              申請類別的值應為: 補休
   - 可能的值：「加班費」、「補休」

7. **加班時數**：找到「時數」欄位的內容
   - 輸出為數值（例如：1.0）

**重要提醒**：
- 請辨識圖片中所有的加班記錄列，不要遺漏任何一筆
- 每一列都是一個獨立的 OvertimeEntry
- 如果某個欄位無法辨識，請填入「無法辨識」
- 時數如果無法辨識，請填入 0.0
"""


def save_result_to_json(
    result: OvertimeDocument,
    metadata: dict,
    token_usage: dict,
    prompt: str,
    output_dir: Path
) -> Path:
    """將結果儲存為 JSON 檔案"""

    # 建立輸出目錄
    output_dir.mkdir(parents=True, exist_ok=True)

    # 產生檔名（含時間戳記）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_result_{timestamp}.json"
    output_path = output_dir / filename

    # 組合輸出資料
    output_data = {
        "test_metadata": metadata,
        "recognition_results": [entry.model_dump() for entry in result.entries],
        "total_entries": len(result.entries),
        "token_usage": token_usage,
        "prompt_used": prompt
    }

    # 寫入 JSON 檔案（使用繁體中文友善的編碼）
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    return output_path


def print_divider(char: str = "=", length: int = 40):
    """印出分隔線"""
    print(char * length)


def print_result(
    image_path: Path,
    model: str,
    result: OvertimeDocument,
    token_usage: dict,
    output_path: Path
):
    """以美化格式印出辨識結果"""

    print_divider()
    print("POC 測試：OpenAI Vision API 手寫辨識")
    print_divider()
    print()

    print(f"測試圖片：{image_path}")
    print(f"模型：{model}")
    print(f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"辨識到 {len(result.entries)} 筆加班記錄")
    print()

    for idx, entry in enumerate(result.entries, 1):
        print_divider()
        print(f"辨識結果 #{idx}")
        print_divider()
        print(f"員工姓名：{entry.employee_name}")
        print(f"日期：{entry.date}")
        print(f"加班時間（起）：{entry.overtime_start_time}")
        print(f"加班時間（迄）：{entry.overtime_end_time}")
        print(f"加班事由：{entry.overtime_reason}")
        print(f"加班類型：{entry.overtime_type}")
        print(f"加班時數：{entry.hours}")
        print()

    print_divider()
    print("Token 使用統計")
    print_divider()
    print(f"Prompt Tokens：{token_usage['prompt_tokens']}")
    print(f"Completion Tokens：{token_usage['completion_tokens']}")
    print(f"Total Tokens：{token_usage['total_tokens']}")
    print()
    print(f"估算成本：${token_usage['estimated_cost_usd']} USD")
    print()

    print_divider()
    print(f"結果已儲存至：{output_path}")
    print_divider()


# ============================================================
# 3. 主程式
# ============================================================

def main():
    """主程式進入點"""

    # 載入環境變數
    load_dotenv()

    # 檢查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("錯誤：找不到 OPENAI_API_KEY 環境變數", file=sys.stderr)
        print("請建立 .env 檔案並設定 OPENAI_API_KEY=your-api-key", file=sys.stderr)
        sys.exit(1)

    if api_key == "sk-your-api-key-here":
        print("錯誤：請設定有效的 OPENAI_API_KEY（目前為範例值）", file=sys.stderr)
        sys.exit(1)

    # 取得模型名稱
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # 設定檔案路徑
    project_root = Path(__file__).parent
    # image_path = project_root / "image" / "SKM_C550i26012311580.jpg"
    image_path = project_root / "image" / "1769137764441.jpg"
    output_dir = project_root / "poc_results"

    # 檢查圖片檔案是否存在
    if not image_path.exists():
        print(f"錯誤：找不到測試圖片 {image_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # 初始化 OpenAI Client
        client = OpenAI(api_key=api_key)

        # 編碼圖片為 Base64
        base64_image = encode_image_to_base64(image_path)

        # 建立 Prompt
        prompt = create_prompt()

        # 呼叫 OpenAI Vision API（使用 Structured Outputs）
        print("正在呼叫 OpenAI Vision API...")
        print(f"使用模型：{model}")
        print()

        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            response_format=OvertimeDocument
            # temperature=0.1  # gpt-5-mini 不支援自定義 temperature，只能使用預設值
        )

        # 取得辨識結果
        result = completion.choices[0].message.parsed

        # 取得 Token 使用統計
        usage = completion.usage
        token_usage = {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "estimated_cost_usd": calculate_cost(usage.prompt_tokens, usage.completion_tokens)
        }

        # 準備 Metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "image_path": str(image_path),
            "image_size_kb": get_image_size_kb(image_path)
        }

        # 儲存結果到 JSON
        output_path = save_result_to_json(
            result=result,
            metadata=metadata,
            token_usage=token_usage,
            prompt=prompt,
            output_dir=output_dir
        )

        # 印出結果
        print_result(
            image_path=image_path,
            model=model,
            result=result,
            token_usage=token_usage,
            output_path=output_path
        )

    except Exception as e:
        print(f"錯誤：API 呼叫失敗", file=sys.stderr)
        print(f"詳細訊息：{str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
