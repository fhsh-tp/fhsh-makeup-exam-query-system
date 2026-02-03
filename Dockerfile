# Railway Deployment - Backend Only
FROM python:3.13-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製後端程式碼
COPY backend /app/backend

# 安裝 Python 依賴
RUN pip install --no-cache-dir \
    fastapi>=0.109.0 \
    "uvicorn[standard]>=0.27.0" \
    sqlmodel>=0.0.14 \
    psycopg2-binary>=2.9.9 \
    pandas>=2.1.0 \
    openpyxl>=3.1.0 \
    python-multipart>=0.0.6 \
    jinja2>=3.1.0 \
    anyio>=4.0.0

ENV PYTHONPATH=/app

# Railway 會自動設定 PORT 環境變數
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
