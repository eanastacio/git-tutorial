from __future__ import annotations

from dataclasses import dataclass
import logging

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError, PyJWKClient

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AuthUser:
    user_id: str
    email: str | None = None


class JWTVerifier:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.jwks_client = PyJWKClient(self.settings.clerk_jwks_url)

    def verify(self, token: str) -> AuthUser:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.settings.clerk_audience,
                issuer=self.settings.clerk_issuer,
                options={"verify_aud": bool(self.settings.clerk_audience)},
            )
            return AuthUser(user_id=payload["sub"], email=payload.get("email"))
        except InvalidTokenError as exc:
            logger.warning("Invalid auth token: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            ) from exc


jwt_verifier = JWTVerifier()
