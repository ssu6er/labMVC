from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    categories: Mapped[list["Category"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    history: Mapped[list["ChoiceHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    user: Mapped[User] = relationship(back_populates="categories")
    options: Mapped[list["Option"]] = relationship(
        back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )
    history: Mapped[list["ChoiceHistory"]] = relationship(
        back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    category: Mapped[Category] = relationship(back_populates="options")


class ChoiceHistory(Base):
    __tablename__ = "choice_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    selected_option_title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    user: Mapped[User] = relationship(back_populates="history")
    category: Mapped[Category] = relationship(back_populates="history")
