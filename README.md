<<<<<<< HEAD
# WebSphere & IBM MQ Fixpack 檢查工具

這是一個自動化工具，用於檢查 WebSphere Application Server 和 IBM MQ 的最新 Fixpack 版本。

## 功能特色

- 自動檢查 WebSphere Application Server V9.0 和 V8.5 的最新 Fixpack
- 自動檢查 IBM MQ V9.4 和 V9.3 的最新 Fixpack
- 驗證釋出日期，排除未來日期（預定發行版本）
- 生成美觀的 HTML 報告（fp-check.html）
- 顯示查詢時間和日期

## 安裝需求

### Python 版本
- Python 3.6 或更高版本

### 安裝相依套件

```bash
pip install -r requirements.txt
```

或手動安裝：

```bash
pip install requests beautifulsoup4 lxml
```

## 使用方法

### 執行程式

```bash
python check_fixpack.py
```

或使其可執行：

```bash
chmod +x check_fixpack.py
./check_fixpack.py
```

### 輸出結果

程式會：
1. 在終端機顯示檢查進度和結果
2. 生成 `fp-check.html` 報告檔案

### 查看報告

在瀏覽器中開啟 `fp-check.html` 檔案即可查看完整報告。

## 檢查的網址

### WebSphere Application Server
- https://www.ibm.com/support/pages/recommended-updates-websphere-application-server

### IBM MQ
- MQ 9.4: https://www.ibm.com/support/pages/node/7166037
- MQ 9.3: https://www.ibm.com/support/pages/node/6695813

## 程式特點

1. **日期驗證**：自動過濾未來日期，只顯示已發行的版本
2. **多格式支援**：支援多種日期格式解析
3. **錯誤處理**：完善的錯誤處理機制
4. **美觀報告**：生成專業的 HTML 報告

## 注意事項

- 需要網路連線才能存取 IBM 網站
- 如果 IBM 網站結構變更，可能需要更新程式
- 建議定期執行以獲取最新資訊

## 故障排除

### 無法連線到 IBM 網站
- 檢查網路連線
- 確認防火牆設定
- 檢查是否需要代理伺服器

### 無法解析版本資訊
- IBM 網站可能已更新結構
- 請檢查網站內容是否有變更

## 授權

此工具僅供練習使用。
=======
# WAS-MQ-FP-Check
check was and mq latest fixpack and release date
>>>>>>> b24ad136d5a35a415fbcab333cce1877f0281e1c
