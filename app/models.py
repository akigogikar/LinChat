from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTable

from .database import Base


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    members = relationship("User", back_populates="team")
    documents = relationship("Document", back_populates="team")


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)

    team = relationship("Team", back_populates="members")
    documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)

    owner = relationship("User", back_populates="documents")
    team = relationship("Team", back_populates="documents")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
