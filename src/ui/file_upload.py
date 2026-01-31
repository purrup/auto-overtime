"""檔案上傳元件

提供檔案選擇、列表顯示、刪除等功能。
"""

import flet as ft
from pathlib import Path
from typing import List, Callable, Optional
from .theme import ColorScheme


class FileUploadComponent:
    """檔案上傳元件類別

    提供使用 FilePicker 選擇多個檔案、顯示檔案列表、刪除檔案等功能。
    """

    def __init__(
        self,
        page: ft.Page,
        allowed_extensions: tuple,
        on_files_selected: Optional[Callable] = None
    ):
        """初始化檔案上傳元件

        Args:
            page: Flet 頁面物件
            allowed_extensions: 允許的副檔名 tuple，例如 ("png", "jpg", "jpeg")
            on_files_selected: 檔案選擇後的回調函數，接收 selected_files 列表作為參數
        """
        self.page = page
        self.allowed_extensions = allowed_extensions
        self.on_files_selected = on_files_selected
        self.selected_files: List[dict] = []

        # 初始化 UI 元件
        self._init_components()

    def _init_components(self) -> None:
        """建立所有 UI 元件"""
        # FilePicker 檔案選擇器
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self._on_file_picker_result
        self.page.overlay.append(self.file_picker)
        self.page.update()

        # 檔案列表視圖
        self.file_list_view = ft.ListView(
            height=300,
            spacing=10,
            padding=10,
        )

        # 檔案數量標籤
        self.file_count_label = ft.Text(
            value="已選擇 0 個檔案",
            size=14,
            color=ColorScheme.TEXT_SECONDARY,
        )

        # 選擇檔案按鈕
        self.upload_button = ft.ElevatedButton(
            text="選擇檔案",
            icon=ft.icons.FILE_UPLOAD,
            on_click=self._open_file_picker,
        )

        # 清除所有按鈕
        self.clear_button = ft.TextButton(
            text="清除所有",
            icon=ft.icons.CLEAR_ALL,
            on_click=self._on_clear_clicked,
            disabled=True,
        )

    def _open_file_picker(self, e) -> None:
        """開啟檔案選擇對話框

        Args:
            e: 按鈕點擊事件
        """
        self.file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=list(self.allowed_extensions),
            dialog_title="選擇加班單圖片檔案",
        )

    def _on_file_picker_result(self, e) -> None:
        """處理檔案選擇結果

        Args:
            e: FilePicker 結果事件
        """
        # 處理選擇的檔案
        if self.file_picker.result and self.file_picker.result.files:
            self._process_selected_files(self.file_picker.result.files)

    def _process_selected_files(self, files: list) -> None:
        """處理選擇的檔案

        Args:
            files: 選擇的檔案列表
        """
        # 遍歷選擇的檔案
        for file in files:
            # 檢查是否已存在（避免重複）
            if not any(f["path"] == file.path for f in self.selected_files):
                # 建立檔案資訊 dict
                file_info = {
                    "name": file.name,
                    "path": file.path,
                    "size_kb": round(file.size / 1024, 2),  # 轉換為 KB
                }
                # 加入到已選擇檔案列表
                self.selected_files.append(file_info)

        # 更新 UI
        self._update_ui()

        # 觸發回調函數
        if self.on_files_selected:
            self.on_files_selected(self.selected_files)

    def _update_ui(self) -> None:
        """更新檔案列表顯示"""
        # 清空檔案列表視圖
        self.file_list_view.controls.clear()

        # 為每個檔案建立卡片
        for index, file_info in enumerate(self.selected_files):
            # 檔案資訊行
            file_name_text = ft.Text(
                value=file_info["name"],
                size=14,
                weight=ft.FontWeight.W_500,
            )

            file_size_text = ft.Text(
                value=f"{file_info['size_kb']} KB",
                size=12,
                color=ColorScheme.NEUTRAL_600,
            )

            # 刪除按鈕
            delete_button = ft.IconButton(
                icon=ft.icons.DELETE_OUTLINE,
                icon_color=ColorScheme.ERROR,
                tooltip="移除此檔案",
                on_click=lambda e, idx=index: self._remove_file(idx),
            )

            # 檔案卡片
            file_card = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.icons.IMAGE,
                                size=32,
                                color=ColorScheme.PRIMARY,
                            ),
                            ft.Column(
                                controls=[file_name_text, file_size_text],
                                spacing=2,
                                expand=True,
                            ),
                            delete_button,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=10,
                ),
            )

            self.file_list_view.controls.append(file_card)

        # 更新檔案數量標籤
        file_count = len(self.selected_files)
        self.file_count_label.value = f"已選擇 {file_count} 個檔案"

        # 更新清除按鈕的禁用狀態
        self.clear_button.disabled = file_count == 0

        # 更新頁面
        self.page.update()

    def _remove_file(self, index: int) -> None:
        """移除指定索引的檔案

        Args:
            index: 要移除的檔案索引
        """
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self._update_ui()

            # 觸發回調函數
            if self.on_files_selected:
                self.on_files_selected(self.selected_files)

    def _on_clear_clicked(self, e) -> None:
        """清除所有檔案

        Args:
            e: 按鈕點擊事件
        """
        self.selected_files.clear()
        self._update_ui()

        # 觸發回調函數
        if self.on_files_selected:
            self.on_files_selected(self.selected_files)

    def build(self) -> ft.Column:
        """建立並返回完整的 UI 佈局

        Returns:
            ft.Column: 包含所有元件的欄位佈局
        """
        return ft.Column(
            controls=[
                # 操作按鈕列
                ft.Row(
                    controls=[
                        self.upload_button,
                        self.clear_button,
                        self.file_count_label,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                # 分隔線
                ft.Divider(),
                # 檔案列表標題
                ft.Text(
                    value="已選擇的檔案",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                # 檔案列表視圖
                self.file_list_view,
            ],
            spacing=10,
        )
