"""Модели для лайков, дизлайков, просмотров и блокировок."""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Integer, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import BotUser
    from database.models.profile import VKProfile


class UserInteraction(Base):
    """Модель действия пользователя над анкетой ВКонтакте.

    Действия включают: просмотр, лайк, дизлайк, блокировку.

    Атрибуты:
        user_id: ID пользователя, выполнившего действие.
        profile_id: ID целевой анкеты.
        action: Тип действия (view, like, dislike, block).

    Связи:
        user: Ссылка на BotUser, выполнившего действие.
        profile: Ссылка на VKProfile, над которым выполнено действие.
    """

    __tablename__ = "user_interactions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("bot_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("vk_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="view/like/dislike/block"
    )

    # Связи
    user: Mapped["BotUser"] = relationship("BotUser", back_populates="interactions")
    profile: Mapped["VKProfile"] = relationship("VKProfile")

    __table_args__ = (
        # Уникальность пары (user, profile) — одно действие на пару
        Index("idx_interaction_user_profile", "user_id", "profile_id", unique=True),
        Index("idx_interaction_user_action", "user_id", "action"),
        Index("idx_interaction_profile_action", "profile_id", "action"),
        CheckConstraint(
            "action IN ('view', 'like', 'dislike', 'block')",
            name="check_interaction_action"
        ),
    )

    def __repr__(self) -> str:
        return f"<UserInteraction(user_id={self.user_id}, profile_id={self.profile_id}, action={self.action})>"


class MutualLike(Base):
    """Модель взаимного лайка (мэтча) между пользователем и анкетой.

    Атрибуты:
        user_id: ID пользователя, поставившего лайк.
        profile_id: ID анкеты, получившей лайк.
        is_notified: Был ли пользователь уведомлён о мэтче.
    """

    __tablename__ = "mutual_likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("bot_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("vk_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_notified: Mapped[bool] = mapped_column(default=False, nullable=False)

    __table_args__ = (
        Index("idx_mutual_user_profile", "user_id", "profile_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<MutualLike(user_id={self.user_id}, profile_id={self.profile_id})>"
