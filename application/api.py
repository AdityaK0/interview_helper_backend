from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from .schema import AppConfigResponse, VersionCheckResponse
from .service import ApplicationService

app_router = APIRouter(prefix="/app", tags=["Application"])


@app_router.get("/version", response_model=VersionCheckResponse)
def get_version(
    platform: str = Query(...),
    current_version: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return ApplicationService(db).check_version(platform, current_version)


@app_router.get("/config", response_model=AppConfigResponse)
def get_config(db: Session = Depends(get_db)):
    return ApplicationService(db).get_config()
