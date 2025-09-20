from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.schemas.token import Token, TokenPayload
from backend.app.schemas.user import UserCreate, UserInDB, UserResponse
from backend.app.services import user as user_service
from backend.app.services import auth as auth_service

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Check if user exists with roles loaded
        result = await db.execute(
            select(User).where(User.email == form_data.username).options(selectinload(User.roles))
        )
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )
            
        logger.info(f"User found: {user.email}, Active: {user.is_active}, Verified: {getattr(user, 'is_verified', False)}")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive. Please contact support."
            )
            
        # Verify password directly
        if not pwd_context.verify(form_data.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )
            
        # If we get here, authentication was successful
        logger.info(f"Password verified for user: {user.email}")
        
        # Create access token with user data
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Get user roles
        role_names = [role.name for role in user.roles] if hasattr(user, 'roles') and user.roles else []
        logger.info(f"User {user.email} logged in with roles: {role_names}")
        
        # Create token data
        token_data = {
            "access_token": security.create_access_token(
                user.id,
                expires_delta=access_token_expires,
                user_data={"email": user.email, "roles": role_names}
            ),
            "token_type": "bearer",
        }
            
        logger.info("Login successful")
        return token_data
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        logger.warning(f"HTTP Exception: {str(http_exc.detail)}")
        raise http_exc
        
    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

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
