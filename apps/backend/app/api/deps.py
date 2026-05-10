from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.security import AuthUser, jwt_verifier
from app.db.session import get_db_session

bearer_scheme = HTTPBearer(auto_error=False)
settings = get_settings()


def get_admin_token(x_admin_token: str = Header(default="")) -> None:
    if x_admin_token != settings.admin_ingestion_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> AuthUser:
    if settings.allow_dev_auth_bypass and not credentials:
        return AuthUser(user_id=settings.dev_auth_user_id, email=settings.dev_auth_email)
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return jwt_verifier.verify(credentials.credentials)


__all__ = ["get_db_session", "get_current_user", "get_admin_token"]
