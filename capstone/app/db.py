"""Storage. SQLite by default; set DATABASE_URL=postgresql+psycopg://... for Postgres."""
import os
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine(os.environ.get("DATABASE_URL", "sqlite:///capstone.db"))


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_enc: Mapped[str] = mapped_column(String)          # Fernet ciphertext
    phone_enc: Mapped[str] = mapped_column(String)          # Fernet ciphertext
    language: Mapped[str] = mapped_column(String(40))
    need: Mapped[dict] = mapped_column(JSON)                # validated CareNeed, no contact data
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MatchRequest(Base):
    __tablename__ = "match_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"))
    license: Mapped[str] = mapped_column(String(20))
    usual_price: Mapped[int]
    budget: Mapped[int]
    status: Mapped[str] = mapped_column(String(10), default="pending")   # pending | accepted | declined
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Outbox(Base):
    """Messages USCIC sends to parents (delivered by a separate mail/SMS worker)."""
    __tablename__ = "outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"))
    body: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


def init_db():
    Base.metadata.create_all(engine)


def session() -> Session:
    return Session(engine)
