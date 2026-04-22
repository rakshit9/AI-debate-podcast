from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.auth.jwt import InvalidTokenError, create_access_token, create_refresh_token, decode_token
from podforge_api.auth.password import generate_api_key, hash_password, verify_password
from podforge_api.config import Settings, get_settings
from podforge_api.database import get_db
from podforge_api.models.user import User
from podforge_api.schemas.auth import APIKeyResponse, RefreshRequest, Token, UserRegister
from podforge_api.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserRegister,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Token:
    svc = UserService(db)
    existing = await svc.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await svc.create(email=body.email, hashed_password=hash_password(body.password))
    return Token(
        access_token=create_access_token(str(user.id), settings),
        refresh_token=create_refresh_token(str(user.id), settings),
    )


@router.post("/token", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Token:
    svc = UserService(db)
    user = await svc.get_by_email(form.username)
    if not user or not user.hashed_password or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return Token(
        access_token=create_access_token(str(user.id), settings),
        refresh_token=create_refresh_token(str(user.id), settings),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Token:
    try:
        payload = decode_token(body.refresh_token, settings)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if payload.type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    svc = UserService(db)
    user = await svc.get_by_id(payload.sub)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return Token(
        access_token=create_access_token(str(user.id), settings),
        refresh_token=create_refresh_token(str(user.id), settings),
    )


@router.post("/api-key", response_model=APIKeyResponse)
async def create_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyResponse:
    raw_key, hashed = generate_api_key()
    svc = UserService(db)
    await svc.set_api_key(current_user.id, hashed)
    return APIKeyResponse(raw_key=raw_key)


@router.delete("/api-key", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    svc = UserService(db)
    await svc.set_api_key(current_user.id, None)
