"""圖片展示元件

提供圖片縮圖列表和放大查看功能。
"""

from pathlib import Path

import flet as ft

from .theme import ColorScheme


class ImageGalleryComponent:
    """圖片展示元件類別

    功能：
    - 顯示圖片縮圖列表
    - 點擊縮圖放大查看
    - 處理圖片不存在的情況
    """

    def __init__(self, page: ft.Page, image_paths: list[str]):
        """初始化圖片展示元件

        Args:
            page: Flet 頁面物件
            image_paths: 圖片路徑列表
        """
        self.page = page
        self.image_paths = image_paths

    def build(self) -> ft.Row:
        """建立圖片展示 UI

        Returns:
            包含所有縮圖的 Row 容器
        """
        thumbnails = []

        for index, image_path in enumerate(self.image_paths):
            thumbnail = self._create_thumbnail(image_path, index)
            thumbnails.append(thumbnail)

        return ft.Row(
            controls=thumbnails,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    def _create_thumbnail(self, image_path: str, index: int) -> ft.Container:
        """建立單個縮圖

        Args:
            image_path: 圖片路徑
            index: 圖片索引

        Returns:
            縮圖容器
        """
        # 檢查檔案是否存在
        if not Path(image_path).exists():
            # 顯示錯誤佔位符
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.BROKEN_IMAGE,
                            size=40,
                            color=ColorScheme.ERROR,
                        ),
                        ft.Text(
                            "圖片不存在",
                            size=12,
                            color=ColorScheme.ERROR,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=150,
                height=150,
                bgcolor=ColorScheme.SURFACE,
                border_radius=8,
                border=ft.border.all(2, ColorScheme.ERROR),
            )

        # 正常顯示圖片（使用 ft.ImageFit.COVER）
        return ft.Container(
            content=ft.Image(
                src=image_path,
                width=150,
                height=150,
                fit=ft.ImageFit.COVER,
                border_radius=8,
            ),
            on_click=lambda e, path=image_path: self._show_fullsize_dialog(path),
            border_radius=8,
            border=ft.border.all(1, ColorScheme.NEUTRAL_BORDER),
            tooltip="點擊放大查看",
        )

    def _show_fullsize_dialog(self, image_path: str) -> None:
        """顯示放大圖片對話框

        Args:
            image_path: 圖片路徑
        """

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("圖片預覽", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Image(
                    src=image_path,
                    fit=ft.ImageFit.CONTAIN,
                ),
                width=800,
                height=600,
            ),
            actions=[
                ft.TextButton("關閉", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # 使用官方推薦方式
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
