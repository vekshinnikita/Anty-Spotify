
from starlette.requests import Request

from .schemas import UserDB

def send_sms_code(user: UserDB, request: Request) -> None:
    print(f"User {user.id} has registered. {123456}")