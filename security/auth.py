"""JWT authentication primitives for the Squad-4 demo API.

Configure AUTH_SECRET with a long random value before exposing this API.
Demo credentials are configurable through environment variables.
"""
from datetime import datetime, timedelta, timezone
import hmac
import os
from typing import Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ConfigDict, Field

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("AUTH_SECRET", "DEV_ONLY_CHANGE_THIS_SECRET_BEFORE_DEPLOYMENT")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "squad4-user")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "ChangeMe123!")
DEMO_ADMIN_USERNAME = os.getenv("DEMO_ADMIN_USERNAME", "squad4-admin")
DEMO_ADMIN_PASSWORD = os.getenv("DEMO_ADMIN_PASSWORD", "ChangeAdmin123!")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class Principal(BaseModel):
    model_config = ConfigDict(frozen=True)
    user_id: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=100)
    roles: list[str] = Field(default_factory=lambda: ["user"])


def authenticate_user(username: str, password: str) -> Principal | None:
    """Demo credential validation; replace with your enterprise identity provider."""
    if hmac.compare_digest(username, DEMO_USERNAME) and hmac.compare_digest(password, DEMO_PASSWORD):
        return Principal(user_id="demo-user-001", username=username, roles=["user"])
    if hmac.compare_digest(username, DEMO_ADMIN_USERNAME) and hmac.compare_digest(password, DEMO_ADMIN_PASSWORD):
        return Principal(user_id="demo-admin-001", username=username, roles=["user", "admin"])
    return None


def create_access_token(principal: Principal) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": principal.user_id,
        "username": principal.username,
        "roles": principal.roles,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> Principal:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        roles = payload.get("roles", [])
        if not user_id or not username or not isinstance(roles, list):
            raise credentials_error
        return Principal(user_id=user_id, username=username, roles=roles)
    except (jwt.PyJWTError, ValueError, TypeError):
        raise credentials_error


def require_roles(*required_roles: str):
    """Dependency factory for role-based access control (RBAC)."""
    def role_checker(principal: Principal = Depends(get_current_user)) -> Principal:
        if not set(required_roles).intersection(principal.roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return principal
    return role_checker
