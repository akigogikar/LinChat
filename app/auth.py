import os
from typing import Optional

from fastapi import Request, Response, Depends
from fastapi_users import FastAPIUsers, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager

from .database import async_session_maker
from .models import User

SECRET = os.getenv("SECRET_KEY", "SECRET")

cookie_transport = CookieTransport(cookie_name="linchat", cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_db():
    async with async_session_maker() as session:
        yield SQLAlchemyUserDatabase(session, User)


class UserRead(schemas.BaseUser[int]):
    team_id: Optional[int]


class UserCreate(schemas.BaseUserCreate):
    team_id: Optional[int] = None


class UserUpdate(schemas.BaseUserUpdate):
    team_id: Optional[int] = None


class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        from .db import add_audit_log

        add_audit_log(user.id, "register")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        from .db import add_audit_log

        add_audit_log(user.id, "login")


async def get_user_manager(
    user_db=Depends(get_user_db),
) -> UserManager:
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
