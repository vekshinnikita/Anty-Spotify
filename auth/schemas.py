from fastapi_users import models
from fastapi_users.db import OrmarBaseOAuthAccountModel
from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional


class UserSchema(models.BaseUser,):
    username: Optional[str]


class UserCreate(models.BaseUserCreate):
    username: Optional[str]


class UserUpdate(models.BaseUserUpdate):
    pass


class UserDB(UserSchema, models.BaseUserDB):
    pass

class User(BaseModel):
    id: UUID4   
    username: Optional[str]

