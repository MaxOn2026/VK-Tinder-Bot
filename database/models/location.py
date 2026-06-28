"""Модель для работы с географическими данными."""

from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base


class Location(Base):
    """Модель географической локации (города с координатами).

    Атрибуты:
        city_name: Название города (уникальное).
        country: Название страны (по умолчанию: "Россия").
        latitude: Координата широты (-90 до 90).
        longitude: Координата долготы (-180 до 180).
        timezone: Идентификатор часового пояса.
        population: Количество жителей.
    """

    __tablename__ = "locations"

    city_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Название города (уникально)",
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Россия")
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(9, 6), nullable=True, comment="Широта (от -90 до 90)"
    )
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(9, 6), nullable=True, comment="Долгота (от -180 до 180)"
    )
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    population: Mapped[Optional[int]] = mapped_column(Numeric(10), nullable=True)

    __table_args__ = (
        Index("idx_location_coords", "latitude", "longitude"),
        Index("idx_location_country", "country"),
    )

    @property
    def coordinates(self) -> Optional[tuple]:
        """Возвращает координаты в виде кортежа.

        Возвращает:
            Optional[tuple]: (широта, долгота) или None, если координаты отсутствуют.
        """
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None

    def __repr__(self) -> str:
        return f"<Location(city={self.city_name}, country={self.country})>"
