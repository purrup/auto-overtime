/**
 * 加班單辨識系統 - 前端 JavaScript
 */

(function() {
    'use strict';

    // ===== 工具函式 =====

    /**
     * 防抖函式
     * @param {Function} func - 要執行的函式
     * @param {number} wait - 等待時間（毫秒）
     * @returns {Function}
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 檢查檔案類型是否為圖片
     * @param {File} file - 檔案物件
     * @returns {boolean}
     */
    function isValidFileType(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        return validTypes.includes(file.type);
    }

    /**
     * 格式化檔案大小
     * @param {number} bytes - 檔案大小（位元組）
     * @returns {string}
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // ===== 檔案上傳功能 =====

    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const fileListItems = document.getElementById('file-list-items');
    const fileCount = document.getElementById('file-count');
    const submitBtn = document.getElementById('submit-btn');
    const uploadForm = document.getElementById('upload-form');

    // 儲存已選檔案
    let selectedFiles = [];

    if (dropzone && fileInput) {
        // 點擊 dropzone 開啟檔案選擇器
        dropzone.addEventListener('click', () => {
            fileInput.click();
        });

        // 檔案選擇變更
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        // 拖放事件
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
    }

    /**
     * 處理選擇的檔案
     * @param {FileList} files - 檔案列表
     */
    function handleFiles(files) {
        const validFiles = Array.from(files).filter(file => {
            if (!isValidFileType(file)) {
                console.warn(`不支援的檔案類型: ${file.name}`);
                return false;
            }
            // 檢查是否已存在相同檔案
            const exists = selectedFiles.some(f => f.name === file.name && f.size === file.size);
            if (exists) {
                console.warn(`檔案已存在: ${file.name}`);
                return false;
            }
            return true;
        });

        selectedFiles = selectedFiles.concat(validFiles);
        updateFileList();
    }

    /**
     * 更新檔案列表 UI
     */
    function updateFileList() {
        if (!fileListItems || !fileList || !fileCount || !submitBtn) return;

        fileListItems.innerHTML = '';

        if (selectedFiles.length === 0) {
            fileList.classList.remove('has-files');
            submitBtn.disabled = true;
            return;
        }

        fileList.classList.add('has-files');
        fileCount.textContent = selectedFiles.length;
        submitBtn.disabled = false;

        selectedFiles.forEach((file, index) => {
            const li = document.createElement('li');
            li.className = 'file-item';
            li.innerHTML = `
                <span class="file-item-name">
                    <svg class="file-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    ${file.name}
                    <span style="color: var(--color-text-muted); margin-left: 0.5rem;">(${formatFileSize(file.size)})</span>
                </span>
                <button type="button" class="file-item-remove" data-index="${index}" title="移除檔案">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            `;
            fileListItems.appendChild(li);
        });

        // 綁定移除按鈕事件
        fileListItems.querySelectorAll('.file-item-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.index, 10);
                removeFile(index);
            });
        });

        // 更新 file input（用於表單提交）
        updateFileInput();
    }

    /**
     * 移除檔案
     * @param {number} index - 檔案索引
     */
    function removeFile(index) {
        selectedFiles.splice(index, 1);
        updateFileList();
    }

    /**
     * 更新 file input（建立新的 DataTransfer）
     */
    function updateFileInput() {
        if (!fileInput) return;

        const dt = new DataTransfer();
        selectedFiles.forEach(file => {
            dt.items.add(file);
        });
        fileInput.files = dt.files;
    }

    // 表單提交處理
    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            if (selectedFiles.length === 0) {
                e.preventDefault();
                alert('請先選擇檔案');
                return;
            }

            // 顯示載入狀態
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoading = submitBtn.querySelector('.btn-loading');
            if (btnText && btnLoading) {
                btnText.hidden = true;
                btnLoading.hidden = false;
            }
            submitBtn.disabled = true;
        });
    }

    // ===== 結果頁面功能 =====

    const entryCards = document.getElementById('entry-cards');
    const statusSaved = document.getElementById('status-saved');
    const statusSaving = document.getElementById('status-saving');

    if (entryCards) {
        const sessionId = entryCards.dataset.sessionId;

        // 收集所有輸入欄位
        const inputs = entryCards.querySelectorAll('.form-input');

        /**
         * 顯示儲存狀態
         * @param {boolean} saving - 是否正在儲存
         */
        function showSaveStatus(saving) {
            if (statusSaved && statusSaving) {
                statusSaved.hidden = saving;
                statusSaving.hidden = !saving;
            }
        }

        /**
         * 儲存資料到後端
         */
        const saveData = debounce(async () => {
            showSaveStatus(true);

            // 收集所有卡片資料
            const entries = [];
            entryCards.querySelectorAll('.entry-card').forEach(card => {
                const entry = {};
                card.querySelectorAll('.form-input').forEach(input => {
                    const field = input.dataset.field;
                    let value = input.value;

                    // 處理數字欄位
                    if (input.type === 'number') {
                        value = parseFloat(value) || 0;
                    }

                    entry[field] = value;
                });
                entries.push(entry);
            });

            try {
                const response = await fetch(`/api/update/${sessionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ entries }),
                });

                if (!response.ok) {
                    throw new Error('儲存失敗');
                }

                showSaveStatus(false);
            } catch (error) {
                console.error('儲存錯誤:', error);
                showSaveStatus(false);
                // 可以在這裡顯示錯誤提示
            }
        }, 500);

        // 監聽所有輸入欄位變更
        inputs.forEach(input => {
            input.addEventListener('input', saveData);
            input.addEventListener('change', saveData);
        });
    }

    // ===== 圖片燈箱功能 =====

    const lightbox = document.getElementById('lightbox');
    const lightboxImage = document.getElementById('lightbox-image');
    const lightboxClose = document.getElementById('lightbox-close');
    const lightboxBackdrop = lightbox ? lightbox.querySelector('.lightbox-backdrop') : null;

    /**
     * 開啟燈箱
     * @param {string} imageSrc - 圖片網址
     */
    function openLightbox(imageSrc) {
        if (lightbox && lightboxImage) {
            lightboxImage.src = imageSrc;
            lightbox.hidden = false;
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * 關閉燈箱
     */
    function closeLightbox() {
        if (lightbox) {
            lightbox.hidden = true;
            document.body.style.overflow = '';
        }
    }

    // 縮圖點擊事件
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
            const imageSrc = thumb.dataset.image;
            if (imageSrc) {
                openLightbox(imageSrc);
            }
        });
    });

    // 關閉燈箱事件
    if (lightboxClose) {
        lightboxClose.addEventListener('click', closeLightbox);
    }

    if (lightboxBackdrop) {
        lightboxBackdrop.addEventListener('click', closeLightbox);
    }

    // ESC 鍵關閉燈箱
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightbox && !lightbox.hidden) {
            closeLightbox();
        }
    });

})();
