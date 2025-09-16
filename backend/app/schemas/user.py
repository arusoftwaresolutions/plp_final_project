from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """
    Base user schema.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(UserBase):
    """
    Schema for updating a user.
    """
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @validator('password', pre=True)
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserInDBBase(UserBase):
    """
    Base schema for user stored in DB.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserResponse(UserInDBBase):
    """
    User response schema.
    """
    pass

class UserInDB(UserInDBBase):
    """
    User schema for internal use (includes hashed password).
    """
    hashed_password: str

class UserWithRoles(UserResponse):
    """
    User schema including role information.
    """
    roles: List[str] = []

class UserRegister(UserCreate):
    """
    Schema for user registration.
    """
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
