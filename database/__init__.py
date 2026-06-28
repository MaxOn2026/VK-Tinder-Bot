# database/__init__.py
from database.base import Base
from database.db_manager import db_manager
from database.models.user import BotUser
from database.models.profile import VKProfile
from database.models.interest import Interest
from database.models.interaction import UserInteraction, MutualLike
from database.models.match import Match, Message
from database.models.location import Location

__all__ = [
    "Base",
    "db_manager",
    "BotUser",
    "VKProfile",
    "Interest",
    "UserInteraction",
    "MutualLike",
    "Match",
    "Message",
    "Location",
]
