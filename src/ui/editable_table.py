"""可編輯表格元件

提供卡片式的可編輯辨識記錄介面。
"""

import threading
from collections.abc import Callable

import flet as ft

from ui.theme import ColorScheme


class EditableTableComponent:
    """可編輯表格元件類別

    功能：
    - 卡片式顯示每筆記錄
    - 所有欄位可編輯（TextField）
    - 防抖自動儲存（500ms）
    """

    def __init__(
        self,
        page: ft.Page,
        entries: list[dict],
        on_data_changed: Callable[[list[dict]], None],
    ):
        """初始化可編輯表格元件

        Args:
            page: Flet 頁面物件
            entries: 辨識記錄列表
            on_data_changed: 資料變更回調函數
        """
        self.page = page
        self.entries = entries
        self.on_data_changed = on_data_changed
        self._save_timer = None

    def build(self) -> ft.Column:
        """建立表格 UI

        Returns:
            包含所有記錄卡片的 Column
        """
        cards = []

        for index, entry in enumerate(self.entries):
            card = self._create_entry_card(entry, index)
            cards.append(card)

        return ft.Column(
            controls=cards,
            spacing=15,
        )

    def _create_entry_card(self, entry: dict, index: int) -> ft.Card:
        """建立單筆記錄的卡片

        Args:
            entry: 辨識記錄字典
            index: 記錄索引

        Returns:
            記錄卡片
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"記錄 {index + 1}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ColorScheme.TEXT_PRIMARY,
                        ),
                        ft.Divider(),
                        # 第一行：員工姓名
                        self._create_field(
                            "員工姓名",
                            "employee_name",
                            entry,
                            index,
                        ),
                        # 第二行：日期
                        self._create_field(
                            "日期 (YYYY-MM-DD)",
                            "date",
                            entry,
                            index,
                        ),
                        # 第三行：開始時間和結束時間
                        ft.Row(
                            controls=[
                                self._create_field(
                                    "開始時間 (HH:MM)",
                                    "overtime_start_time",
                                    entry,
                                    index,
                                    expand=True,
                                ),
                                self._create_field(
                                    "結束時間 (HH:MM)",
                                    "overtime_end_time",
                                    entry,
                                    index,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                        ),
                        # 第四行：加班事由
                        self._create_field(
                            "加班事由",
                            "overtime_reason",
                            entry,
                            index,
                            multiline=True,
                            min_lines=2,
                            max_lines=4,
                        ),
                        # 第五行：加班類型和時數
                        ft.Row(
                            controls=[
                                self._create_field(
                                    "加班類型",
                                    "overtime_type",
                                    entry,
                                    index,
                                    expand=True,
                                ),
                                self._create_field(
                                    "時數",
                                    "hours",
                                    entry,
                                    index,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=10,
                ),
                padding=15,
            ),
        )

    def _create_field(
        self,
        label: str,
        field_key: str,
        entry: dict,
        index: int,
        expand: bool = False,
        multiline: bool = False,
        min_lines: int = 1,
        max_lines: int = 1,
    ) -> ft.Column | ft.TextField:
        """建立單個可編輯欄位

        Args:
            label: 欄位標籤
            field_key: 欄位鍵名
            entry: 辨識記錄字典
            index: 記錄索引
            expand: 是否展開填滿
            multiline: 是否多行
            min_lines: 最小行數
            max_lines: 最大行數

        Returns:
            TextField 或包含 TextField 的 Column
        """
        text_field = ft.TextField(
            label=label,
            value=str(entry.get(field_key, "")),
            on_change=lambda e, idx=index, key=field_key: self._on_field_changed(
                idx, key, e.control.value
            ),
            border_color=ColorScheme.NEUTRAL_BORDER,
            focused_border_color=ColorScheme.PRIMARY,
            multiline=multiline,
            min_lines=min_lines,
            max_lines=max_lines,
            expand=expand,
        )

        if expand:
            return text_field
        else:
            return ft.Column(
                controls=[text_field],
                spacing=0,
            )

    def _on_field_changed(self, index: int, field_key: str, new_value: str) -> None:
        """欄位變更事件處理

        Args:
            index: 記錄索引
            field_key: 欄位鍵名
            new_value: 新值
        """
        # 更新資料
        self.entries[index][field_key] = new_value

        # 取消舊的計時器
        if self._save_timer:
            self._save_timer.cancel()

        # 啟動新的計時器（500ms 後儲存）
        def delayed_save():
            # 使用 page.run_thread() 確保執行緒安全
            self.page.run_thread(lambda: self.on_data_changed(self.entries))

        self._save_timer = threading.Timer(0.5, delayed_save)
        self._save_timer.start()
