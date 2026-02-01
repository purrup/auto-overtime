"""主應用程式介面模組

此模組包含 OvertimeApp 類別，負責管理整個應用程式的 UI 佈局和事件處理。
"""

import json
from datetime import datetime
from pathlib import Path

import flet as ft

from ai_extraction.vision_client import VisionAPIError, VisionClient
from config import Config
from data_handling.json_handler import JSONDataHandler
from image_processing.encoder import ImageEncoder, ImageEncodingError
from ui.editable_table import EditableTableComponent
from ui.file_upload import FileUploadComponent
from ui.image_gallery import ImageGalleryComponent
from ui.progress_indicator import ProgressIndicator
from ui.theme import ColorScheme


class OvertimeApp:
    """ㄋ加班單辨識系統主應用程式介面

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

        # 進度指示器（新增）
        self.progress_indicator = ProgressIndicator(page=self.page)

        # 結果顯示文字（新增）
        self.result_text = ft.Text(
            value="",
            size=14,
            selectable=True,
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
                self.progress_indicator.build(),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self._build_action_section(),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self._build_result_section(),
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
                        value="加班單辨識系統",
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
        """開始辨識按鈕點擊事件

        啟動背景執行緒處理 AI 辨識，避免 UI 凍結。

        Args:
            e: 事件物件
        """
        # 驗證檔案列表
        if not self.file_upload.selected_files:
            self._show_snackbar("請先選擇檔案", is_error=True)
            return

        # 更新 UI 狀態
        self.start_button.disabled = True
        self.export_button.disabled = True
        self.file_upload.upload_button.disabled = True
        self.file_upload.clear_button.disabled = True
        self.result_container.visible = False
        self.progress_indicator.show("正在處理圖片...")
        self.page.update()

        # 啟動背景執行緒
        self.page.run_thread(self._recognition_task)

    def _on_export_csv(self, e) -> None:
        """匯出 CSV 按鈕點擊事件（第一階段佔位符）

        Args:
            e: 事件物件
        """
        self.status_text.value = "匯出功能將在第三階段實作"
        self.status_text.color = ColorScheme.INFO
        self.page.update()

    def _build_result_section(self) -> ft.Container:
        """建立結果顯示區

        Returns:
            包含結果資訊的容器
        """
        self.result_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="辨識結果",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ColorScheme.TEXT_PRIMARY,
                    ),
                    ft.Container(height=10),
                    self.result_text,
                ],
                spacing=0,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ColorScheme.NEUTRAL_BORDER),
            border_radius=12,
            visible=False,  # 初始隱藏
        )
        return self.result_container

    def _recognition_task(self) -> None:
        """背景執行緒中執行的辨識任務

        完整流程：
        1. 圖片編碼
        2. 呼叫 Vision API
        3. 儲存結果
        4. 通知成功或失敗
        """
        try:
            # 步驟 1：圖片編碼
            self.progress_indicator.update_message("正在編碼圖片...")
            self.page.update()

            encoder = ImageEncoder()
            base64_images = []
            image_paths = []

            for file_info in self.file_upload.selected_files:
                image_path = Path(file_info["path"])
                image_paths.append(str(image_path))

                # 驗證大小並編碼
                encoder.validate_image_size(image_path)
                base64_image = encoder.encode_image(image_path)
                base64_images.append(base64_image)

            # 步驟 2：更新進度訊息
            self.progress_indicator.update_message("正在呼叫 AI 辨識...")
            self.page.update()

            # 步驟 3：呼叫 Vision API
            client = VisionClient()
            api_result = client.recognize_batch(base64_images)

            # 步驟 4：儲存結果
            self.progress_indicator.update_message("正在儲存結果...")
            self.page.update()

            metadata = {
                "timestamp": datetime.now().isoformat(),
                "model": self.config.OPENAI_MODEL,
                "image_count": len(base64_images),
                "image_paths": image_paths,
            }

            output_path = self._save_recognition_result(api_result, metadata)

            # 步驟 5：通知成功
            result_data = {
                "result": api_result["result"],
                "token_usage": api_result["token_usage"],
                "cost_usd": api_result["cost_usd"],
                "output_path": output_path,
                "image_count": len(base64_images),
                "image_paths": image_paths,  # 新增這行
            }

            self.page.run_thread(lambda: self._on_recognition_success(result_data))

        except (ImageEncodingError, VisionAPIError) as e:
            # 已知錯誤
            error_message = str(e)
            self.page.run_thread(lambda: self._on_recognition_error(error_message))
        except Exception as e:
            # 未知錯誤
            error_message = f"發生未預期的錯誤：{str(e)}"
            self.page.run_thread(lambda: self._on_recognition_error(error_message))

    def _on_recognition_success(self, result_data: dict) -> None:
        """辨識成功回調（主執行緒）

        Args:
            result_data: 辨識結果資料
        """
        # 隱藏進度條
        self.progress_indicator.hide()

        # 儲存當前的 output_path 和 image_paths 到實例變數（供後續儲存使用）
        self.current_result_path = result_data["output_path"]
        self.current_image_paths = result_data["image_paths"]

        # 計算統計資訊
        total_hours = sum(entry.hours for entry in result_data["result"].entries)
        image_count = result_data["image_count"]
        entry_count = len(result_data["result"].entries)

        # 建立統計資訊文字（簡化版）
        summary_text = f"處理圖片：{image_count} 張 | 辨識記錄：{entry_count} 筆 | 總加班時數：{total_hours} 小時"

        # 建立圖片展示元件
        image_gallery = ImageGalleryComponent(self.page, self.current_image_paths)

        # 將 Pydantic 模型轉換為 dict 列表
        entries_dict = [entry.model_dump() for entry in result_data["result"].entries]

        # 建立可編輯表格元件
        editable_table = EditableTableComponent(
            self.page,
            entries_dict,
            on_data_changed=self._on_table_data_changed,
        )

        # 更新結果容器內容
        self.result_container.content = ft.Column(
            controls=[
                ft.Text(
                    "步驟 3：檢視與編輯",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ColorScheme.TEXT_PRIMARY,
                ),
                ft.Container(height=10),
                ft.Text(
                    summary_text,
                    size=14,
                    color=ColorScheme.TEXT_SECONDARY,
                ),
                ft.Divider(),
                ft.Text(
                    "原始圖片",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ColorScheme.TEXT_PRIMARY,
                ),
                ft.Container(height=5),
                image_gallery.build(),
                ft.Divider(),
                ft.Text(
                    "辨識結果 (可編輯)",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ColorScheme.TEXT_PRIMARY,
                ),
                ft.Container(height=5),
                editable_table.build(),
            ],
            spacing=10,
        )
        self.result_container.visible = True

        # 恢復按鈕狀態
        self.start_button.disabled = False
        self.file_upload.upload_button.disabled = False
        self.file_upload.clear_button.disabled = False

        # 更新狀態列
        self.status_text.value = f"辨識完成！共 {entry_count} 筆記錄"
        self.status_text.color = ColorScheme.SUCCESS

        # 顯示 SnackBar
        self._show_snackbar("辨識完成！")

        self.page.update()

    def _on_table_data_changed(self, entries: list[dict]) -> None:
        """表格資料變更時的回調函數

        Args:
            entries: 更新後的辨識記錄列表
        """
        try:
            # 儲存到 JSON
            JSONDataHandler.update_entries(self.current_result_path, entries)

            # 顯示儲存提示（靜默，不干擾）
            self.status_text.value = "變更已自動儲存"
            self.status_text.color = ColorScheme.SUCCESS
            self.page.update()

        except Exception as e:
            # 錯誤處理
            self._show_snackbar(f"儲存失敗：{str(e)}", is_error=True)

    def _on_recognition_error(self, error_message: str) -> None:
        """辨識失敗回調（主執行緒）

        Args:
            error_message: 錯誤訊息
        """
        # 隱藏進度條
        self.progress_indicator.hide()

        # 恢復按鈕狀態
        self.start_button.disabled = False
        self.file_upload.upload_button.disabled = False
        self.file_upload.clear_button.disabled = False

        # 更新狀態列
        self.status_text.value = "辨識失敗"
        self.status_text.color = ColorScheme.ERROR

        # 顯示錯誤對話框
        self._show_error_dialog("辨識失敗", error_message)

        self.page.update()

    def _save_recognition_result(self, api_result: dict, metadata: dict) -> Path:
        """儲存辨識結果到 output/ 資料夾

        Args:
            api_result: API 回應結果
            metadata: 中繼資料

        Returns:
            輸出檔案路徑
        """
        # 產生檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recognition_result_{timestamp}.json"
        output_path = self.config.OUTPUT_DIR / filename

        # 組合輸出資料
        output_data = {
            "metadata": metadata,
            "recognition_results": [entry.model_dump() for entry in api_result["result"].entries],
            "total_entries": len(api_result["result"].entries),
            "token_usage": api_result["token_usage"],
            "cost_usd": api_result["cost_usd"],
        }

        # 寫入 JSON 檔案
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return output_path

    def _show_error_dialog(self, title: str, message: str) -> None:
        """顯示錯誤對話框

        Args:
            title: 對話框標題
            message: 錯誤訊息
        """

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Icon(name=ft.Icons.ERROR_OUTLINED, size=48, color=ft.Colors.RED_400),
                    ft.Text(message, size=14),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            actions=[ft.TextButton(text="確定", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _show_snackbar(self, message: str, is_error: bool = False) -> None:
        """顯示 SnackBar 提示

        Args:
            message: 提示訊息
            is_error: 是否為錯誤訊息
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_400 if is_error else None,
        )
        self.page.snack_bar.open = True
        self.page.update()
