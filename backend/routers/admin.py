"""
Admin Router - 管理端 API 路由

提供 Excel 上傳功能，使用 Secret Token 進行身份驗證。
此 API 專供 Google Apps Script 呼叫，不提供網頁登入介面。
"""
import os
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from sqlmodel import Session, delete

from backend.database import get_session
from backend.models import MakeupExam
from backend.services.parser import parse_excel_file

from backend.utils import verify_admin_token

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/upload", name="admin_upload")
async def admin_upload_excel(
    file: Annotated[UploadFile, File()],
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[None, Depends(verify_admin_token)],
) -> dict:
    """
    上傳 Excel 檔案並更新補考資料

    執行全量覆蓋策略：
    1. 驗證 Secret Token（透過 Dependency）
    2. DELETE 所有現有資料
    3. 解析 Excel 並 INSERT 新資料

    Headers:
        X-Admin-Token: 管理員 Secret Token

    Returns:
        dict: 上傳結果，包含成功筆數
    """
    # 驗證檔案類型
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請上傳 Excel 檔案 (.xlsx 或 .xls)",
        )

    try:
        # 讀取檔案內容
        file_content = await file.read()

        # 解析 Excel（使用 async_manager 非同步執行）
        exams = await parse_excel_file(file_content)

        if not exams:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel 檔案中沒有有效資料",
            )

        # 全量覆蓋：先刪除所有資料
        session.exec(delete(MakeupExam))

        # 寫入新資料
        for exam in exams:
            session.add(exam)

        session.commit()

        return {
            "success": True,
            "message": f"成功上傳 {len(exams)} 筆補考資料",
            "count": len(exams),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"解析失敗: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上傳失敗: {str(e)}",
        )
