#!/bin/bash
# 智慧型加班單辨識系統 - 啟動腳本

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 使用正確的 Python 版本運行應用程式
~/.pyenv/versions/3.13.11/bin/python -m src.main
