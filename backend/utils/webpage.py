"""
WebPage Utils - FastAPI 網頁渲染與錯誤處理

提供：
- WebPage: Jinja2 模板渲染類別
- register_error_handlers: 全域錯誤處理器註冊
"""
import time
from os import PathLike
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from starlette.exceptions import HTTPException as StarletteHTTPException


@pass_context
def urlx_for(context: dict, name: str, **path_params: Any) -> str:
    """
    擴充 FastAPI 的 url_for 函式，支援 Reverse Proxy。

    當 Request Header 包含 x-forwarded-proto 時，自動替換 URL scheme。
    """
    request: Request = context["request"]
    http_url = request.url_for(name, **path_params)
    if scheme := request.headers.get("x-forwarded-proto"):
        return http_url.replace(scheme=scheme)
    return http_url


class WebPage:
    """
    管理網頁渲染的類別。

    初始化 Jinja2 環境，提供 Template 渲染功能。
    """

    def __init__(
        self,
        template_directory: Path | PathLike | str,
        **global_context: Any,
    ):
        """
        初始化 WebPage 實例。

        Args:
            template_directory: Template 檔案的目錄路徑
            **global_context: 全域的 Context 變數
        """
        self._template = Jinja2Templates(template_directory)
        self._template.env.globals["url_for"] = urlx_for
        self._webpage_context = dict(global_context)
        self._pre_context: dict = {}

    def __call__(
        self,
        template_file: PathLike | str,
        request: Request,
        context: dict[str, Any] | None = None,
        **kwargs,
    ):
        """
        渲染指定的 Template 並回傳 Response。

        Args:
            template_file: Template 檔案名稱
            request: FastAPI 的 Request 物件
            context: 額外的 Context 變數
            **kwargs: 其他參數 (status_code, headers)

        Returns:
            TemplateResponse
        """
        if context is None:
            context = {}

        context.update({
            "request": request,
            "webpage": self._webpage_context,
            "css_timestamp": str(int(time.time())),
        })
        context.update(self._pre_context)

        response = self._template.TemplateResponse(
            name=template_file,
            context=context,
        )

        if isinstance(kwargs.get("status_code"), int):
            response.status_code = kwargs["status_code"]

        if isinstance(kwargs.get("headers"), dict):
            response.headers.update(kwargs["headers"])

        return response


def register_error_handlers(
    app: FastAPI,
    webpage: WebPage,
    error_template: str = "error.jinja2",
):
    """
    註冊全域錯誤處理器。

    根據 Request 的 Accept Header 決定回傳 JSON 或 HTML：
    - Accept: application/json → 回傳 JSON
    - 其他 → 渲染 HTML 錯誤頁面

    Args:
        app: FastAPI App 實例
        webpage: WebPage 實例
        error_template: 錯誤頁面 Template 檔名
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        accept = request.headers.get("accept", "")
        if "application/json" in accept:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        return webpage(
            template_file=error_template,
            request=request,
            context={"status_code": exc.status_code, "detail": exc.detail},
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        accept = request.headers.get("accept", "")
        if "application/json" in accept:
            from fastapi.encoders import jsonable_encoder
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": jsonable_encoder(exc.errors())},
            )
        return webpage(
            template_file=error_template,
            request=request,
            context={
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detail": str(exc),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        accept = request.headers.get("accept", "")
        if "application/json" in accept:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal Server Error"},
            )
        return webpage(
            template_file=error_template,
            request=request,
            context={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "Internal Server Error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
