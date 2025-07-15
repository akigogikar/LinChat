import os
from typing import Optional

from fastapi import Request
from fastapi_users import FastAPIUsers, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

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


fastapi_users = FastAPIUsers[User, int](
    get_user_db,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)


async def on_after_register(user: User, request: Optional[Request] = None):
    from .db import add_audit_log

    add_audit_log(user.id, "register")


async def on_after_login(user: User, request: Optional[Request] = None):
    from .db import add_audit_log

    add_audit_log(user.id, "login")


fastapi_users.on_after_register(on_after_register)
fastapi_users.on_after_login(on_after_login)
