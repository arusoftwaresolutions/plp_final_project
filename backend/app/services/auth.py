from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.db.models import User
from backend.app.schemas.token import TokenPayload
from backend.app.services.user import user as user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class AuthService:
    """
    Authentication service for handling user authentication and token management.
    """
    
    @classmethod
    async def authenticate(
        cls, 
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User's email
            password: Plain text password
            
        Returns:
            User object if authentication is successful, None otherwise
        """
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from backend.app.core.security import verify_password
        
        # Get user by email with roles eagerly loaded
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles))
            .filter(User.email == email)
        )
        user = result.scalars().first()
        
        if not user:
            return None
            
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
            
        # Check if user is active
        if not user.is_active:
            return None
            
        return user
    
    @classmethod
    def create_access_token(
        cls, 
        subject: Union[str, Any], 
        expires_delta: Optional[timedelta] = None,
        user_data: Optional[dict] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            subject: The subject of the token (usually user ID)
            expires_delta: Optional timedelta for token expiration
            user_data: Additional user data to include in the token
            
        Returns:
            str: Encoded JWT token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "iat": datetime.utcnow(),
        }
        
        if user_data:
            to_encode.update(user_data)
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @classmethod
    async def get_current_user(
        cls, 
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """
        Get the current authenticated user from the JWT token.
        
        Args:
            db: Database session
            token: JWT token from the Authorization header
            
        Returns:
            User: The authenticated user
            
        Raises:
            HTTPException: If the token is invalid or the user doesn't exist
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            
            token_data = TokenPayload(**payload)
        except (JWTError, ValueError):
            raise credentials_exception
        
        user = await user_service.get(db, id=int(user_id))
        if user is None:
            raise credentials_exception
        
        return user
    
    @classmethod
    async def get_current_active_user(
        cls, 
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Get the current active user.
        
        Args:
            current_user: The current authenticated user
            
        Returns:
            User: The active user
            
        Raises:
            HTTPException: If the user is inactive
        """
        if not user_service.is_active(current_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    
    @classmethod
    async def get_current_active_superuser(
        cls, 
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Get the current active superuser.
        
        Args:
            current_user: The current authenticated user
            
        Returns:
            User: The active superuser
            
        Raises:
            HTTPException: If the user is not a superuser
        """
        if not user_service.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        return current_user
    
    @classmethod
    async def authenticate_user(
        cls, 
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User's email
            password: Plain text password
            
        Returns:
            Optional[User]: The authenticated user if successful, None otherwise
        """
        return await user_service.authenticate(db, email=email, password=password)
    
    @classmethod
    async def create_first_superuser(cls, db: AsyncSession) -> User:
        """
        Create the first superuser if no users exist.
        
        Args:
            db: Database session
            
        Returns:
            User: The created or existing superuser
        """
        # Check if any users exist
        result = await db.execute(select(User).limit(1))
        existing_user = result.scalars().first()
        
        if existing_user:
            return existing_user
        
        # Create first superuser
        user_data = {
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "is_active": True,
            "is_verified": True,
        }
        
        # Create the user
        user = await user_service.create(db, obj_in=user_data)
        
        # Add admin role
        await user_service.add_role(db, user_id=user.id, role_name="admin")
        
        await db.commit()
        await db.refresh(user)
        
        return user

# Create an instance of the auth service
auth = AuthService()
