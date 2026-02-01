"""
加班記錄的 Pydantic 資料模型定義

此模組定義了加班單辨識系統的核心資料結構：
- OvertimeEntry: 單筆加班記錄
- OvertimeDocument: 整張加班單文件（可包含多筆記錄）
"""

from pydantic import BaseModel, Field


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
        description="加班事由，完整的手寫或是印刷文字內容。若無法辨識填入「無法辨識」"
    )

    overtime_type: str = Field(
        description="加班類型，例如「加班費」、「補休」等。若無法辨識填入「無法辨識」"
    )

    hours: float = Field(
        description="加班時數，數值型態，單位為小時。例如：1.0 表示 1 小時。若無法辨識填入 0.0"
    )


class OvertimeDocument(BaseModel):
    """整張加班單文件（可包含多筆記錄）"""

    entries: list[OvertimeEntry] = Field(
        description="加班記錄列表，每一列代表一筆加班記錄。如果圖片中只有一筆記錄，列表就只有一個元素。"
    )
