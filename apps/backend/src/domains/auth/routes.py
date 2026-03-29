"""Auth routes – login, signup, refresh, logout via Supabase."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.supabase import get_supabase_client
from ..profiles.service import ProfileService

router = APIRouter(prefix="/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


@router.post("/signup", response_model=TokenResponse)
async def signup(body: SignUpRequest, db: AsyncSession = Depends(get_db)):
    client = get_supabase_client()
    try:
        response = client.auth.sign_up({"email": body.email, "password": body.password})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not response.user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signup failed")

    profile_svc = ProfileService(db)
    await profile_svc.get_or_create_profile(auth_uid=response.user.id, email=body.email, full_name=body.full_name)

    return TokenResponse(
        access_token=response.session.access_token if response.session else "",
        refresh_token=response.session.refresh_token if response.session else "",
        user={"id": response.user.id, "email": response.user.email},
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    client = get_supabase_client()
    try:
        response = client.auth.sign_in_with_password({"email": body.email, "password": body.password})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return TokenResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        user={"id": response.user.id, "email": response.user.email},
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    client = get_supabase_client()
    try:
        response = client.auth.refresh_session(refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return TokenResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        user={"id": response.user.id, "email": response.user.email},
    )


@router.post("/logout")
async def logout():
    return {"message": "Logged out. Clear tokens on client side."}
