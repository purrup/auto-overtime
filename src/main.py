#!/usr/bin/env python3
"""
智慧型加班單辨識自動化系統
主程式進入點
"""

import flet as ft

from .config import Config
from .ui.app import OvertimeApp


def main(page: ft.Page) -> None:
    """
    應用程式主函數

    Args:
        page: Flet Page 實例
    """
    try:
        # 驗證配置
        Config.validate()

        # 建立應用程式實例
        OvertimeApp(page)

    except Exception as e:
        # 定義關閉應用程式的回調函數
        async def close_app(e) -> None:
            """關閉應用程式"""
            await page.window.close()

        # 建立錯誤對話框
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("啟動失敗", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Icon(name=ft.Icons.ERROR_OUTLINED, size=48, color=ft.Colors.RED_400),
                    ft.Text("應用程式啟動失敗", size=16),
                    ft.Container(height=10),
                    ft.Text(str(e), size=14, color=ft.Colors.GREY_700),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            actions=[ft.TextButton(text="關閉", on_click=close_app)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # 顯示錯誤對話框
        page.overlay.append(error_dialog)
        error_dialog.open = True
        page.update()


if __name__ == "__main__":
    ft.app(target=main)
