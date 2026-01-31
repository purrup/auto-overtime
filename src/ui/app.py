"""主應用程式介面模組

此模組包含 OvertimeApp 類別，負責管理整個應用程式的 UI 佈局和事件處理。
"""

import flet as ft

from ..config import Config
from .file_upload import FileUploadComponent
from .theme import ColorScheme


class OvertimeApp:
    """智慧型加班單辨識系統主應用程式介面

    負責：
    - 設定頁面屬性（標題、主題、視窗大小）
    - 建立主介面佈局
    - 整合檔案上傳元件
    - 處理按鈕事件和狀態更新
    """

    def __init__(self, page: ft.Page):
        """初始化應用程式

        Args:
            page: Flet 頁面物件
        """
        self.page = page
        self.config = Config

        # 初始化步驟
        self._setup_page()
        self._init_components()
        self._build_ui()

    def _setup_page(self) -> None:
        """設定頁面屬性"""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 20
        self.page.window.width = Config.WINDOW_WIDTH
        self.page.window.height = Config.WINDOW_HEIGHT
        self.page.window.resizable = True

    def _init_components(self) -> None:
        """初始化 UI 元件"""
        # 檔案上傳元件
        self.file_upload = FileUploadComponent(
            page=self.page,
            allowed_extensions=Config.ALLOWED_EXTENSIONS,
            on_files_selected=self._on_files_updated,
        )

        # 操作按鈕
        self.start_button = ft.ElevatedButton(
            text="開始辨識",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_start_recognition,
            disabled=True,
            bgcolor=ColorScheme.PRIMARY,
            color=ft.Colors.WHITE,
            height=45,
        )

        self.export_button = ft.ElevatedButton(
            text="匯出 CSV",
            icon=ft.Icons.FILE_DOWNLOAD,
            on_click=self._on_export_csv,
            disabled=True,
            bgcolor=ColorScheme.ACCENT,
            color=ft.Colors.WHITE,
            height=45,
        )

        # 狀態訊息
        self.status_text = ft.Text(
            value="請選擇要辨識的加班單檔案...",
            size=14,
            color=ColorScheme.TEXT_SECONDARY,
        )

    def _build_ui(self) -> None:
        """建立主介面佈局"""
        main_layout = ft.Column(
            controls=[
                self._build_header(),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self._build_upload_section(),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self._build_action_section(),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self._build_status_bar(),
            ],
            spacing=0,
            expand=True,
        )

        self.page.add(main_layout)

    def _build_header(self) -> ft.Container:
        """建立標題區

        Returns:
            包含標題和副標題的容器
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="智慧型加班單辨識系統",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ColorScheme.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        value="使用 AI 視覺模型將手寫加班單自動轉換為結構化數位報表",
                        size=14,
                        color=ColorScheme.TEXT_SECONDARY,
                    ),
                ],
                spacing=5,
            ),
            padding=ft.padding.only(bottom=10),
        )

    def _build_upload_section(self) -> ft.Container:
        """建立檔案上傳區

        Returns:
            包含檔案上傳元件的容器
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="步驟 1：上傳檔案",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ColorScheme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=10),
                    self.file_upload.build(),
                ],
                spacing=0,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ColorScheme.NEUTRAL_BORDER),
            border_radius=12,
        )

    def _build_action_section(self) -> ft.Container:
        """建立操作區

        Returns:
            包含操作按鈕的容器
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="步驟 2：辨識與匯出",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ColorScheme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        controls=[
                            self.start_button,
                            self.export_button,
                        ],
                        spacing=15,
                    ),
                ],
                spacing=0,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ColorScheme.NEUTRAL_BORDER),
            border_radius=12,
        )

    def _build_status_bar(self) -> ft.Container:
        """建立狀態列

        Returns:
            包含狀態圖示和訊息的容器
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=ft.Icons.INFO_OUTLINED,
                        color=ColorScheme.NEUTRAL_600,
                        size=20,
                    ),
                    self.status_text,
                ],
                spacing=10,
            ),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
        )

    def _on_files_updated(self, files: list) -> None:
        """檔案更新回調函數

        當使用者選擇或移除檔案時觸發，更新按鈕狀態和狀態訊息。

        Args:
            files: 檔案列表
        """
        if files and len(files) > 0:
            # 有檔案：啟用開始辨識按鈕
            self.start_button.disabled = False
            self.status_text.value = f"已選擇 {len(files)} 個檔案，可以開始辨識"
            self.status_text.color = ColorScheme.SUCCESS
        else:
            # 無檔案：禁用開始辨識按鈕
            self.start_button.disabled = True
            self.status_text.value = "請選擇要辨識的加班單檔案..."
            self.status_text.color = ColorScheme.TEXT_SECONDARY

        self.page.update()

    def _on_start_recognition(self, e) -> None:
        """開始辨識按鈕點擊事件（第一階段佔位符）

        Args:
            e: 事件物件
        """
        self.status_text.value = "辨識功能將在第二階段實作"
        self.status_text.color = ColorScheme.INFO
        self.page.update()

    def _on_export_csv(self, e) -> None:
        """匯出 CSV 按鈕點擊事件（第一階段佔位符）

        Args:
            e: 事件物件
        """
        self.status_text.value = "匯出功能將在第三階段實作"
        self.status_text.color = ColorScheme.INFO
        self.page.update()
