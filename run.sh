#!/bin/bash
# 加班單辨識系統 - 啟動腳本

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 檢查虛擬環境是否存在
if [ ! -d ".venv" ]; then
    echo "❌ 錯誤: 找不到虛擬環境 .venv"
    echo "請先執行: python -m venv .venv && .venv/bin/pip install -e ."
    exit 1
fi

# 直接使用虛擬環境的 Python (不依賴 activate)
echo "🚀 啟動加班單辨識系統..."
echo "📍 使用 Python: .venv/bin/python"
.venv/bin/python -m src.main
