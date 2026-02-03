"""
Excel Parser Service - 解析補考名單 Excel 檔案

專門解析「應到考名單 (班級座號序)」工作表，將資料轉換為 MakeupExam 物件。
使用 @to_async 將同步的 pandas 操作轉為非同步執行。
"""
from io import BytesIO
from typing import BinaryIO

import pandas as pd

from backend.models import MakeupExam
from backend.utils import to_async


# 目標工作表名稱
TARGET_SHEET_NAME = "應到考名單 (班級座號序)"


@to_async
def parse_excel_file(file_content: bytes | BinaryIO) -> list[MakeupExam]:
    """
    解析 Excel 檔案並轉換為 MakeupExam 物件列表

    使用 @to_async 裝飾器將同步的 pandas 操作轉為非同步執行，
    避免阻塞事件迴圈。

    Args:
        file_content: Excel 檔案內容 (bytes 或 file-like object)

    Returns:
        list[MakeupExam]: 解析後的補考資料列表

    Raises:
        ValueError: 當找不到目標工作表或必要欄位時
    """
    # 讀取 Excel 檔案
    if isinstance(file_content, bytes):
        file_content = BytesIO(file_content)
    
    try:
        df = pd.read_excel(
            file_content, 
            sheet_name=TARGET_SHEET_NAME,
            dtype=str  # 所有欄位都以字串讀取，避免型別轉換問題
        )
    except ValueError as e:
        raise ValueError(f"無法找到工作表「{TARGET_SHEET_NAME}」: {e}")
    
    # 清理欄位名稱 (移除空白)
    df.columns = df.columns.str.strip()
    
    # 驗證必要欄位
    required_columns = {"學號", "補考科目", "補考日期", "補考時間", "補考教室"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"缺少必要欄位: {missing_columns}")
    
    # 選擇姓名欄位 (優先使用 姓名1)
    name_column = "姓名1" if "姓名1" in df.columns else "姓名"
    
    # 轉換為 MakeupExam 物件
    exams: list[MakeupExam] = []
    for _, row in df.iterrows():
        # 跳過學號為空的行
        if pd.isna(row.get("學號")) or str(row.get("學號")).strip() == "":
            continue
            
        exam = MakeupExam(
            student_id=str(row["學號"]).strip(),
            student_name=str(row.get(name_column, "")).strip() if pd.notna(row.get(name_column)) else None,
            class_name=str(row.get("班級", "")).strip() if pd.notna(row.get("班級")) else None,
            subject=str(row["補考科目"]).strip(),
            exam_date=str(row["補考日期"]).strip(),
            exam_time=str(row["補考時間"]).strip(),
            location=str(row["補考教室"]).strip(),
        )
        exams.append(exam)
    
    return exams
