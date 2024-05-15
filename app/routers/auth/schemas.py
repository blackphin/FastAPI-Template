from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr


# REQUEST


class TokenData(BaseModel):
    token: str
    emp_no: str
    scopes: List[str] = []
    exp: datetime


class CreateUser(BaseModel):
    emp_no: str
    name: str
    dept: str


# RESPONSE


class Token(BaseModel):
    access_token: str
    token_type: str
    scopes: List[str] = []

    class Config:
        orm_mode = True
