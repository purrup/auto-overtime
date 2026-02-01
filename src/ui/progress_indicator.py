"""進度指示器元件

提供顯示/隱藏進度條和更新進度訊息的功能。
"""

import flet as ft

from ui.theme import ColorScheme


class ProgressIndicator:
    """進度指示器元件

    提供顯示/隱藏進度條和更新進度訊息的功能，用於向使用者展示長時間執行的操作進度。
    """

    def __init__(self, page: ft.Page):
        """初始化進度指示器

        Args:
            page: Flet Page 實例
        """
        self.page = page

        # 建立 UI 元件
        self._init_components()

    def _init_components(self) -> None:
        """建立所有 UI 元件"""
        # 進度條（不確定進度模式）
        self.progress_bar = ft.ProgressBar(
            width=400,
            color=ColorScheme.PRIMARY,
            bgcolor=ColorScheme.PRIMARY_LIGHT,
        )

        # 進度圖示
        self.progress_icon = ft.Icon(
            name=ft.Icons.SYNC,
            size=24,
            color=ColorScheme.PRIMARY,
        )

        # 進度訊息文字
        self.progress_text = ft.Text(
            value="處理中...",
            size=14,
            color=ColorScheme.TEXT_PRIMARY,
            weight=ft.FontWeight.W_500,
        )

        # 容器（包含所有元件）
        self.container = ft.Container(
            content=ft.Column(
                controls=[
                    # 圖示和訊息行
                    ft.Row(
                        controls=[
                            self.progress_icon,
                            self.progress_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    # 進度條
                    ft.Container(
                        content=self.progress_bar,
                        alignment=ft.alignment.center,
                    ),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ColorScheme.PRIMARY_LIGHT,
            border=ft.border.all(1, ColorScheme.PRIMARY_BORDER),
            border_radius=10,
            padding=20,
            visible=False,  # 初始狀態為隱藏
        )

    def build(self) -> ft.Container:
        """建立進度指示器 UI

        Returns:
            包含進度條和訊息的 Container
        """
        return self.container

    def show(self, message: str = "處理中...") -> None:
        """顯示進度條並更新訊息

        Args:
            message: 要顯示的進度訊息，預設為「處理中...」
        """
        self.progress_text.value = message
        self.container.visible = True
        self.page.update()

    def hide(self) -> None:
        """隱藏進度條"""
        self.container.visible = False
        self.page.update()

    def update_message(self, message: str) -> None:
        """更新進度訊息（不改變可見性）

        Args:
            message: 要顯示的進度訊息
        """
        self.progress_text.value = message
        self.page.update()

    def show_with_icon(self, message: str = "處理中...", icon: str = ft.Icons.SYNC) -> None:
        """顯示進度條並更新訊息和圖示

        Args:
            message: 要顯示的進度訊息，預設為「處理中...」
            icon: 要顯示的圖示，預設為 ft.Icons.SYNC
        """
        self.progress_text.value = message
        self.progress_icon.name = icon
        self.container.visible = True
        self.page.update()
