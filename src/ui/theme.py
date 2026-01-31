"""主題配色系統

提供統一的顏色定義,確保 UI 一致性。
"""

import flet as ft


class ColorScheme:
    """配色方案類別

    定義應用程式的所有顏色常數,採用柔和簡約的設計風格。
    """

    # 主色調 (Primary) - 用於主要操作按鈕和強調元素
    PRIMARY = ft.Colors.INDIGO_400  # 柔和靛藍色
    PRIMARY_LIGHT = ft.Colors.INDIGO_50  # 極淡靛藍背景
    PRIMARY_BORDER = ft.Colors.INDIGO_100  # 淡靛藍邊框

    # 次要色調 (Accent) - 用於次要操作和成功狀態
    ACCENT = ft.Colors.TEAL_400  # 柔和青綠色
    ACCENT_LIGHT = ft.Colors.TEAL_50  # 極淡青綠背景
    ACCENT_BORDER = ft.Colors.TEAL_100  # 淡青綠邊框

    # 中性色階 (Neutral) - 用於文字、背景、邊框
    TEXT_PRIMARY = ft.Colors.GREY_800  # 主要文字色
    TEXT_SECONDARY = ft.Colors.GREY_600  # 次要文字色
    NEUTRAL_600 = ft.Colors.GREY_500  # 中性灰色
    NEUTRAL_BORDER = ft.Colors.GREY_200  # 統一邊框色
    SURFACE = ft.Colors.GREY_50  # 淺灰背景

    # 語意色彩 (Semantic) - 用於狀態提示
    SUCCESS = ft.Colors.TEAL_500  # 成功狀態
    INFO = ft.Colors.INDIGO_400  # 資訊提示
    WARNING = ft.Colors.AMBER_500  # 警告狀態
    ERROR = ft.Colors.RED_400  # 錯誤狀態

    # 功能色彩 (Functional)
    BACKGROUND = ft.Colors.WHITE  # 主背景色
