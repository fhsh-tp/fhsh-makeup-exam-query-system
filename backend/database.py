"""
Database Configuration - 資料庫連線與 Session 管理

使用 SQLModel 進行 ORM 操作。
"""
import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# 從環境變數取得資料庫連線字串
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/makeup_exam"
)

# 建立 SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """建立資料庫表格"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI Dependency: 取得資料庫 Session
    
    Yields:
        Session: SQLModel Session 物件
    """
    with Session(engine) as session:
        yield session
