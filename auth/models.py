import ormar
import datetime
from db import MainMeta
from typing import Optional, Union, Dict, List
from fastapi_users.db import OrmarBaseUserModel, OrmarUserDatabase, OrmarBaseOAuthAccountModel

from .schemas import UserDB


class User(OrmarBaseUserModel):
    class Meta(MainMeta):
        pass

    username: Optional[str] = ormar.String(max_length=1000, unique=True)

class OAuthAccount(OrmarBaseOAuthAccountModel):
    class Meta(MainMeta):
        pass

    username: str = ormar.String(max_length=150)
    user: Optional[Union[Dict, User]] = ormar.ForeignKey(User, related_name="oauth_accounts")



async def get_user_db():
    yield OrmarUserDatabase(UserDB, User, OAuthAccount)