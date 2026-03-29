"""Auth utilities: JWT verification via Supabase, role checking, dependencies."""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from .supabase import get_supabase_client


async def get_current_user(request: Request) -> dict:
    """Extract and verify the Supabase JWT from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = auth_header.removeprefix("Bearer ").strip()
    supabase = get_supabase_client()
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return {"id": user.id, "email": user.email, "role": user.user_metadata.get("role", "user")}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {exc}",
        ) from exc


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Return None for unauthenticated requests instead of raising."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


def require_role(*roles: str):
    """Dependency factory that ensures the user has one of the given roles."""
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "user")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(roles)}",
            )
        return user
    return _check
