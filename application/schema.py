from pydantic import BaseModel


class VersionCheckResponse(BaseModel):
    latest_version: str
    minimum_supported_version: str
    update_required: bool
    release_url: str | None


class AppConfigResponse(BaseModel):
    app_env: str
