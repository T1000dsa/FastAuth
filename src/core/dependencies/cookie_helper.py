from fastapi.responses import RedirectResponse
from datetime import timedelta

from src.core.config.auth_config import (
    ACCESS_TYPE,
    REFRESH_TYPE
    )
from src.core.config.config import settings


class CookieManager:
    @staticmethod
    def set_auth_cookies(response: RedirectResponse, tokens: dict):
        response.set_cookie(
            key=ACCESS_TYPE,
            value=tokens["access_token"],
            httponly=True,
            secure=settings.is_prod,
            samesite="lax",
            max_age=timedelta(minutes=settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES).seconds
        )
        # Similar for refresh token

    @staticmethod
    def clear_auth_cookies(response: RedirectResponse):
        response.delete_cookie(ACCESS_TYPE)
        response.delete_cookie(REFRESH_TYPE)