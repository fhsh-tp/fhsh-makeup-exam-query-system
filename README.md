# 臺北市立復興高級中學 學分補考查詢系統

一個用於學生查詢補考科目、時間與地點的 Web 應用程式。

## 🚀 快速開始

### 使用 Docker Compose (推薦)

```bash
# 1. 複製環境變數檔案
cp .env.example .env

# 2. 編輯 .env 設定 Secret Token
# 產生 token: python -c "import secrets; print(secrets.token_hex(32))"
vim .env

# 3. 啟動服務
docker compose up -d --build

# 4. 查看服務狀態
docker compose ps

# 5. 查看 Secret Token（若未手動設定）
docker compose logs backend | grep "ADMIN_SECRET_TOKEN"
```

服務將在以下位置啟動：
- 前端 (學生查詢): http://localhost
- 後端 API: http://localhost:8000

### 停止服務

```bash
docker compose down
```

## 📋 功能說明

### 學生端
- 輸入學號查詢補考科目
- 顯示科目、日期、時間、地點
- 響應式設計，支援手機瀏覽

### 管理端 (API)
- 使用 Secret Token 進行身份驗證
- 透過 Google Apps Script 上傳 Excel 補考名單
- 全量覆蓋更新 (每次上傳會清除舊資料)

## 🔐 安全機制

本系統移除傳統的網頁登入介面，改用 Secret Token 機制：

1. **無登入頁面**: 消除暴力破解攻擊面
2. **Secret Token**: 使用 256 位元 (32 bytes) 隨機金鑰
3. **Header 傳輸**: Token 透過 `X-Admin-Token` HTTP Header 傳送
4. **Timing Attack 防護**: 使用 `secrets.compare_digest` 進行比對

### Google Apps Script 呼叫範例

```javascript
function uploadExcel() {
  const url = 'https://your-domain.com/admin/upload';
  const token = 'your_secret_token_here';

  // 取得 Google Drive 中的 Excel 檔案
  const file = DriveApp.getFileById('your_file_id');
  const blob = file.getBlob();

  const options = {
    method: 'post',
    headers: {
      'X-Admin-Token': token
    },
    payload: {
      file: blob
    }
  };

  const response = UrlFetchApp.fetch(url, options);
  Logger.log(response.getContentText());
}
```

## 📁 專案結構

```
├── backend/           # FastAPI 後端
│   ├── main.py       # 主應用程式
│   ├── models.py     # SQLModel 資料模型
│   ├── database.py   # 資料庫設定
│   ├── routers/      # API 路由
│   ├── services/     # 服務層 (Excel 解析)
│   ├── utils/        # 工具函式 (async, webpage)
│   └── Dockerfile
├── frontend/          # React 前端
│   ├── src/
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

## 🔧 開發環境

### 後端開發

```bash
# 從專案根目錄執行
pip install fastapi uvicorn sqlmodel psycopg2-binary pandas openpyxl python-multipart jinja2 anyio
uvicorn backend.main:app --reload
```

### 前端開發

```bash
cd frontend
npm install
npm run dev
```

## 📝 Excel 檔案格式

系統讀取工作表「**應到考名單 (班級座號序)**」，欄位需求如下：

**必要欄位：**
- 學號
- 補考科目
- 補考日期
- 補考時間
- 補考教室

**選填欄位：**
- 姓名1（或 姓名）
- 班級

## 🎨 配色方案

- 主色調: #00A99D (活潑藍綠)
- 強調色: #FF6F61 (珊瑚橘紅)
- 支援深色模式自動切換
