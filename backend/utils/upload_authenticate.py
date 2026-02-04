import os
import secrets
from typing import Annotated
from fastapi import Header, HTTPException, status

# 從環境變數取得 Secret Token（至少 32 bytes / 256 bits）
# 若未設定，啟動時會產生隨機 token 並輸出到 log

ADMIN_SECRET_TOKEN = None

def set_admin_secret_token() -> None:
    global ADMIN_SECRET_TOKEN

    if ADMIN_SECRET_TOKEN is None:
        ADMIN_SECRET_TOKEN = os.getenv("ADMIN_SECRET_TOKEN")

    if not ADMIN_SECRET_TOKEN:
        ADMIN_SECRET_TOKEN = secrets.token_hex(32)  # 產生 64 字元的 hex string (256 bits)
        print(f"[WARNING] ADMIN_SECRET_TOKEN 未設定，已自動產生: {ADMIN_SECRET_TOKEN}")
        print("[WARNING] 請將此 token 設定到環境變數中以確保一致性")


def verify_admin_token(x_admin_token: Annotated[str | None, Header()] = None) -> None:
    """
    驗證 Admin Secret Token

    透過 HTTP Header 'X-Admin-Token' 傳入 token 進行驗證。
    使用 secrets.compare_digest 防止 timing attack。

    Raises:
        HTTPException: 若 token 無效或未提供
    """

    if not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供驗證 token",
            headers={"WWW-Authenticate": "X-Admin-Token"},
        )

    if not secrets.compare_digest(x_admin_token, ADMIN_SECRET_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="驗證 token 無效",
            headers={"WWW-Authenticate": "X-Admin-Token"},
        )