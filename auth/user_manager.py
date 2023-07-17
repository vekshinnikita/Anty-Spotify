from fastapi import Depends, Request, HTTPException
from ormar import NoMatch
from typing import Optional, Tuple
from fastapi_users import BaseUserManager, models
from fastapi_users.manager import UserNotExists
from fastapi_users.authentication import BearerTransport, JWTStrategy
from fastapi_users.authentication import CookieTransport


from .models import get_user_db, OAuthAccount, User
from .schemas import UserDB, UserCreate
from .oauth2.oauth2 import YandexOAuth2

SECRET = "Sdasdad3w#RmF34ef43%E5&*6DV%$5DSvBF*fY9V(y*&VNFdfBU(t8DnfDS"

yandex_oauth_client = YandexOAuth2(
    "6f78edd11b8e4c59ae13a821b4668cc7",
    "21262f2229e247aabbe0eaca37be0d36",
    "https://oauth.yandex.ru/authorize",
    "https://oauth.yandex.ru/token",
    name='yandex'
)

bearer_transport =  CookieTransport(cookie_max_age=3600)

jwt_strategy = JWTStrategy(secret=SECRET, lifetime_seconds=3600)


def get_jwt_strategy() -> JWTStrategy:
    return jwt_strategy

class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def oauth_callback(
        self, oauth_account: models.BaseOAuthAccount, request: Optional[Request] = None
    ) -> models.UD:
        """
        Handle the callback after a successful OAuth authentication.

        If the user already exists with this OAuth account, the token is updated.

        If a user with the same e-mail already exists,
        the OAuth account is linked to it.

        If the user does not exist, it is created and the on_after_register handler
        is triggered.

        :param oauth_account: The new OAuth account to create.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None
        :return: A user.
        """
        username = await yandex_oauth_client.get_id_login(oauth_account.access_token)
        oauth_account = OAuthAccount(username=username, **oauth_account.dict())

        token = request.cookies.get('fastapiusersauth', None)

        if token:
            # Link account      
            user = await jwt_strategy.read_token(token, self)
            try:
                await OAuthAccount.objects.get(oauth_name=oauth_account.oauth_name, account_id=oauth_account.account_id)
                raise HTTPException(status_code=400, detail="This Yandex user already in use")
            except NoMatch:
                if user is not None:
                    oauth_account.user = user.dict()
                    await oauth_account.save()
                else: 
                    raise HTTPException(status_code=401, detail="Unauthorized")
        else: 

            try:
                user_oauth_account = await OAuthAccount.objects.select_related('user').get(oauth_name=oauth_account.oauth_name, account_id=oauth_account.account_id)
                user = user_oauth_account.user
            except NoMatch:
                try:
                    # Link account
                    user = await User.objects.select_related('oauth_accounts').get(email=oauth_account.account_email) # type: ignore
                    oauth_account.user = user.dict()
                    await oauth_account.save()
                except NoMatch:
                    # Create account
                    password = self.password_helper.generate()
                    user = self.user_db_model(
                        username=username,
                        email=oauth_account.account_email,
                        hashed_password=self.password_helper.hash(password),
                    )
                    await self.user_db.create(user)
                    oauth_account.user = user.dict()
                    await oauth_account.save()
                    await self.on_after_register(user, request)
            else:
                # Update oauth
                updated_oauth_accounts = []
                for existing_oauth_account in user.oauth_accounts:  # type: ignore
                    if existing_oauth_account.account_id == oauth_account.account_id:
                        updated_oauth_accounts.append(oauth_account)
                    else:
                        updated_oauth_accounts.append(existing_oauth_account)
                user.oauth_accounts = updated_oauth_accounts  # type: ignore
                await user.update()

        return user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)