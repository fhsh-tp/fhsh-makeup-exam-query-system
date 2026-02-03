"""
API Router - 學生查詢 API

提供學生查詢補考資訊的 RESTful API。
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import MakeupExam

router = APIRouter(prefix="/api", tags=["api"])


def mask_name(name: str | None) -> str | None:
    """
    遮蔽姓名中間字元

    規則：
    - 2 字：X○（王○）
    - 3 字：X○X（王○明）
    - 4 字以上：X○○...X（歐陽○○發）

    Args:
        name: 原始姓名

    Returns:
        遮蔽後的姓名，若為 None 或空字串則回傳 None
    """
    if not name or not name.strip():
        return None

    name = name.strip()
    length = len(name)

    if length == 1:
        return name
    elif length == 2:
        return f"{name[0]}○"
    else:
        # 3 字以上：保留頭尾，中間用○替換
        middle = "○" * (length - 2)
        return f"{name[0]}{middle}{name[-1]}"


@router.get("/exams/{student_id}", name="get_student_exams")
async def get_student_exams(
    student_id: str,
    session: Annotated[Session, Depends(get_session)],
) -> list[dict]:
    """
    查詢指定學號的補考資訊

    Args:
        student_id: 學號

    Returns:
        list[dict]: 該學生的補考清單，包含科目、日期、時間、地點、遮蔽姓名
    """
    # 查詢該學號的所有補考資料
    statement = select(MakeupExam).where(MakeupExam.student_id == student_id)
    exams = session.exec(statement).all()

    # 轉換為前端需要的格式（姓名遮蔽、移除班級）
    return [
        {
            "subject": exam.subject,
            "exam_date": exam.exam_date,
            "exam_time": exam.exam_time,
            "location": exam.location,
            "student_name": mask_name(exam.student_name),
        }
        for exam in exams
    ]
