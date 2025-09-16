from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    """
    Token response schema.
    """
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """
    Token payload schema.
    """
    sub: Optional[int] = None
    exp: Optional[int] = None
    email: Optional[EmailStr] = None
    roles: Optional[list[str]] = None

class Msg(BaseModel):
    """
    Generic message response schema.
    """
    msg: str
