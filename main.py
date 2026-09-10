import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from notes.api import notes_router
from auth.api import auth_router
from installations.api import installations_router
from subscriptions.api import subscriptions_router
from entitlements.api import entitlements_router
from payments.api import payments_router
from application.api import app_router
from utils.exceptions import AppException
from middleware.request_logging import RequestLoggingMiddleware
from middleware.security import SecurityHeadersMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="FastAPI Template",
    description="Layered FastAPI backend template built around one CRUD module (Notes) — the pattern to copy for any new resource.",
    version="1.0.0",
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error_response(status_code: int, message: str, error_code: str):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "error_code": error_code},
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return _error_response(exc.status_code, exc.message, exc.error_code or "APP_ERROR")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(notes_router)
app.include_router(auth_router)
app.include_router(installations_router)
app.include_router(subscriptions_router)
app.include_router(entitlements_router)
app.include_router(payments_router)
app.include_router(app_router)
