from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr


# REQUEST


class TokenData(BaseModel):
    token: str
    user_id: str
    scopes: List[str] = []
    exp: datetime


class CreateUser(BaseModel):
    user_id: str
    name: str
    dept: str


# RESPONSE


class Token(BaseModel):
    access_token: str
    token_type: str
    scopes: List[str] = []

    class Config:
        orm_mode = True
