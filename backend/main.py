"""
Main Application - FastAPI 主應用程式

初始化 FastAPI 應用，註冊路由與中間件。
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_db_and_tables
from backend.routers import admin, api
from backend.utils import WebPage, register_error_handlers, set_admin_secret_token

# 初始化 WebPage 用於錯誤頁面渲染
TEMPLATE_DIR = Path(__file__).parent / "templates"
webpage = WebPage(TEMPLATE_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Events
    
    啟動時建立資料庫表格。
    """
    set_admin_secret_token()
    create_db_and_tables()
    yield


# 建立 FastAPI 應用
app = FastAPI(
    title="學分補考查詢系統",
    description="臺北市立復興高級中學 學分補考查詢系統 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 設定 CORS（允許前端跨域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應限制為特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(admin.router)
app.include_router(api.router)

# 註冊全域錯誤處理器（使用 fastapi_webpage）
# 當瀏覽器訪問發生錯誤時，會渲染 error.jinja2 模板
# 當 API 請求（Accept: application/json）發生錯誤時，回傳 JSON
register_error_handlers(app, webpage, "error.jinja2")


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """健康檢查端點"""
    return {"status": "healthy"}
