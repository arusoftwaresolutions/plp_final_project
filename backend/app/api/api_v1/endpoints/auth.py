import uuid
from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
    
    # Add request ID for better tracing
    request_id = str(uuid.uuid4())[:8]
    
    try:
        logger.info(f"[{request_id}] Login attempt for user: {form_data.username}")

        # Check if user exists with roles loaded
        try:
            logger.info(f"[{request_id}] Querying database for user: {form_data.username}")
            result = await db.execute(
                select(User)
                .where(User.email == form_data.username)
                .options(selectinload(User.roles))
            )
            user = result.scalars().first()
            logger.info(f"[{request_id}] Database query completed")
        except Exception as e:
            logger.error(f"[{request_id}] Database error when fetching user: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

        if not user:
            logger.warning(f"[{request_id}] User not found: {form_data.username}")
            # Add a small delay to prevent timing attacks
            import time
            time.sleep(0.5)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

        logger.info(f"[{request_id}] User found: {user.email}, ID: {user.id}, Active: {user.is_active}, Verified: {getattr(user, 'is_verified', False)}")

        # Check if user is active
        if not user.is_active:
            logger.warning(f"[{request_id}] Inactive user attempted login: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive. Please contact support."
            )

        # Verify password directly
        try:
            logger.info(f"[{request_id}] Verifying password for user: {user.email}")
            password_matches = pwd_context.verify(form_data.password, user.hashed_password)
            if not password_matches:
                logger.warning(f"[{request_id}] Invalid password for user: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect email or password"
                )
            logger.info(f"[{request_id}] Password verification successful for user: {user.email}")
        except Exception as e:
            logger.error(f"[{request_id}] Error verifying password: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying password: {str(e)}"
            )

        # If we get here, authentication was successful
        logger.info(f"[{request_id}] Authentication successful for user: {user.email}")

        # Create access token with user data
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Get user roles
        try:
            role_names = [role.name for role in user.roles] if hasattr(user, 'roles') and user.roles else []
            logger.info(f"[{request_id}] User {user.email} has roles: {role_names}")

            # Create token data
            token_data = {
                "access_token": security.create_access_token(
                    user.id,
                    expires_delta=access_token_expires,
                    user_data={"email": user.email, "roles": role_names}
                ),
                "token_type": "bearer",
            }

            logger.info(f"[{request_id}] Token generated successfully for user: {user.email}")
            return token_data
            
        except Exception as e:
            logger.error(f"[{request_id}] Error generating token: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating access token: {str(e)}"
            )
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions with more context
        logger.warning(f"[{request_id}] Login failed - {http_exc.detail}")
        raise http_exc
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in login endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login. Please try again later."
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
