"""Модели для мэтчей и переписки."""
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import BotUser


class Match(Base):
    """Модель мэтча между двумя пользователями бота (оба лайкнули друг друга).

    Атрибуты:
        user1_id: ID первого пользователя (всегда меньший ID).
        user2_id: ID второго пользователя (всегда больший ID).
        matched_at: Время создания мэтча.
        is_active: Активен ли мэтч.

    Связи:
        user1: Ссылка на BotUser (user1_id).
        user2: Ссылка на BotUser (user2_id).
        messages: Один-ко-многим с Message.
    """

    __tablename__ = "matches"

    user1_id: Mapped[int] = mapped_column(
        ForeignKey("bot_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user2_id: Mapped[int] = mapped_column(
        ForeignKey("bot_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    matched_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.now,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)

    # Связи
    user1: Mapped["BotUser"] = relationship("BotUser", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2: Mapped["BotUser"] = relationship("BotUser", foreign_keys=[user2_id], back_populates="matches_as_user2")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_match_users", "user1_id", "user2_id", unique=True),
        CheckConstraint("user1_id < user2_id", name="check_match_users_order"),
        Index("idx_match_active_ordered", "is_active", "matched_at"),
    )

    def __repr__(self) -> str:
        return f"<Match(user1_id={self.user1_id}, user2_id={self.user2_id})>"


class Message(Base):
    """Модель сообщения в чате мэтча.

    Атрибуты:
        match_id: ID связанного мэтча.
        sender_id: ID пользователя, отправившего сообщение.
        text: Текст сообщения.
        sent_at: Время отправки сообщения.
        is_read: Прочитано ли сообщение.

    Связи:
        match: Ссылка на Match.
        sender: Ссылка на BotUser, отправившего сообщение.
    """

    __tablename__ = "messages"

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("bot_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.now,
        index=True
    )
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Связи
    match: Mapped["Match"] = relationship("Match", back_populates="messages")
    sender: Mapped["BotUser"] = relationship("BotUser")

    __table_args__ = (
        Index("idx_message_match_sent", "match_id", "sent_at"),
        Index("idx_message_unread", "match_id", "is_read"),
    )

    def __repr__(self) -> str:
        return f"<Message(match_id={self.match_id}, sender_id={self.sender_id}, text_len={len(self.text)})>"
