from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, UserInDB, UserResponse
from app.services import user as user_service
from app.services import auth as auth_service

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await auth_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Get user roles
    role_names = [role.name for role in user.roles] if user.roles else []
    
    return {
        "access_token": security.create_access_token(
            user.id,
            expires_delta=access_token_expires,
            user_data={"email": user.email, "roles": role_names}
        ),
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=UserResponse)
async def test_token(
    current_user: UserInDB = Depends(security.get_current_user)
) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new user
    """
    # Check if user with this email already exists
    user = await user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists"
        )
    
    # Create new user
    user = await user_service.create(db, obj_in=user_in)
    return user

@router.post("/password-recovery/{email}", response_model=Dict[str, str])
async def recover_password(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Password Recovery
    """
    # TODO: Implement password recovery logic
    return {"msg": "Password recovery email sent"}

@router.post("/reset-password/", response_model=Dict[str, str])
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Reset password
    """
    # TODO: Implement password reset logic
    return {"msg": "Password updated successfully"}
