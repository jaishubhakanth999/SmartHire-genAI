"""
Authentication.

Responsibility: verify the Supabase-issued JWT sent by the frontend on every
API call (`Authorization: Bearer <access_token>`), and expose FastAPI
dependencies that route handlers use to get the current user and to gate
admin-only endpoints.

The frontend never talks to this backend for sign-in/sign-up -- that goes
directly to Supabase Auth via supabase-js. This module only verifies the
token Supabase already issued, using the project's JWT secret (Settings ->
API -> JWT Settings in the Supabase dashboard).
"""

from dataclasses import dataclass
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.database import get_profile

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: Optional[str]
    role: str  # "user" or "admin"


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}") from exc


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header.")

    payload = _decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has no subject.")

    profile = get_profile(user_id)
    role = profile.get("role", "user") if profile else "user"
    email = payload.get("email") or (profile.get("email") if profile else None)

    return CurrentUser(id=user_id, email=email, role=role)


async def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return user
