from typing import Any, Dict, Optional, Union, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.services.base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    User CRUD operations.
    """
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Get a user by email.
        """
        result = await db.execute(
            select(self.model).filter(self.model.email == email)
        )
        return result.scalars().first()
    
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """
        Get a user by username.
        """
        result = await db.execute(
            select(self.model).filter(self.model.username == username)
        )
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            is_active=obj_in.is_active if hasattr(obj_in, 'is_active') else True,
            is_verified=obj_in.is_verified if hasattr(obj_in, 'is_verified') else False,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user, handling password hashing if password is being updated.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """
        Check if a user is active.
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        Check if a user is a superuser.
        """
        return any(role.name == "admin" for role in user.roles)
    
    async def add_role(self, db: AsyncSession, *, user_id: int, role_name: str) -> User:
        """
        Add a role to a user.
        """
        user = await self.get(db, id=user_id)
        if not user:
            return None
        
        # Check if role exists
        result = await db.execute(select(Role).filter(Role.name == role_name))
        role = result.scalars().first()
        
        if not role:
            # Create the role if it doesn't exist
            role = Role(name=role_name)
            db.add(role)
            await db.commit()
            await db.refresh(role)
        
        # Add role to user if not already assigned
        if role not in user.roles:
            user.roles.append(role)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    async def remove_role(self, db: AsyncSession, *, user_id: int, role_name: str) -> User:
        """
        Remove a role from a user.
        """
        user = await self.get(db, id=user_id)
        if not user:
            return None
        
        # Find the role
        result = await db.execute(select(Role).filter(Role.name == role_name))
        role = result.scalars().first()
        
        if role and role in user.roles:
            user.roles.remove(role)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    async def get_user_with_roles(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Get a user with their roles loaded.
        """
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles))
            .filter(User.id == user_id)
        )
        return result.scalars().first()

# Create an instance of the user service
user = CRUDUser(User)
