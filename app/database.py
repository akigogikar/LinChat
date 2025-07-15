import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .db import DB_FILE

DATABASE_URL = os.getenv("LINCHAT_DATABASE_URL", f"sqlite+aiosqlite:///{DB_FILE}")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass
