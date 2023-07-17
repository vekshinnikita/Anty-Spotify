from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from .schemas import UserSchema, UserDB, UserCreate, UserUpdate
from .oauth2.oauth2 import YandexOAuth2
from .user_manager import get_user_manager, bearer_transport, get_jwt_strategy, SECRET


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


    

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    UserSchema,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_user = fastapi_users.current_user(active=True)