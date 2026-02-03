"""
MakeupExam SQLModel - 學分補考資料模型

定義用於儲存補考資訊的資料庫模型。
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class MakeupExam(SQLModel, table=True):
    """
    補考資料模型
    
    Attributes:
        id: 主鍵
        student_id: 學號 (indexed for fast lookup)
        student_name: 學生姓名
        class_name: 班級
        subject: 補考科目
        exam_date: 補考日期 (e.g. "2月6日")
        exam_time: 補考時間 (e.g. "08:00-08:50")
        location: 補考教室 (e.g. "篤行樓209教室")
        created_at: 資料建立時間
    """
    __tablename__ = "makeup_exams"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(index=True, max_length=20, description="學號")
    student_name: Optional[str] = Field(default=None, max_length=50)
    class_name: Optional[str] = Field(default=None, max_length=20)
    subject: str = Field(max_length=50)
    exam_date: str = Field(max_length=20, description="原始格式 e.g. 2月6日")
    exam_time: str = Field(max_length=50)
    location: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
