"""
Доменная модель контекста бронирования.

Содержит основные сущности, агрегаты и доменные сервисы
для управления бронированием номеров в отеле.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field
from shared_kernel import (
    BookingStatus,
    BusinessRuleValidationException,
    DateRange,
    DomainEvent,
    EntityId,
    Money,
    RoomType,
    generate_id,
)

from .interfaces import (
    IBookingRepository,
)


class Guest(BaseModel):
    """Гость отеля."""

    id: EntityId = Field(default_factory=generate_id)
    first_name: str
    last_name: str
    email: str
    phone: str
    document_number: str  # Номер документа, удостоверяющего личность


class Room(BaseModel):
    """Номер в отеле."""

    id: EntityId = Field(default_factory=generate_id)
    number: str  # Номер комнаты (например, "101", "202A")
    type: RoomType
    capacity: int = Field(..., gt=0)
    amenities: List[str] = Field(default_factory=list)  # Удобства в номере
    base_price_per_night: Money
    is_available: bool = True


class BookingCreated(DomainEvent):
    """Событие создания бронирования."""

    booking_id: EntityId
    room_id: EntityId
    guest_id: EntityId
    period: DateRange


class BookingCancelled(DomainEvent):
    """Событие отмены бронирования."""

    booking_id: EntityId
    reason: Optional[str] = None


class BookingConfirmed(DomainEvent):
    """Событие подтверждения бронирования."""

    booking_id: EntityId
    confirmed_at: datetime


class Booking(BaseModel):
    """Бронирование номера в отеле."""

    id: EntityId = Field(default_factory=generate_id)
    room_id: EntityId
    guest_id: EntityId
    period: DateRange
    status: BookingStatus = BookingStatus.PENDING
    adults: int = Field(..., gt=0)
    children: int = Field(0, ge=0)
    special_requests: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 0
    _domain_events: List[DomainEvent] = []

    class Config:
        underscore_attrs_are_private = True

    @property
    def domain_events(self) -> List[DomainEvent]:
        """Возвращает список доменных событий."""
        return self._domain_events

    def clear_events(self) -> None:
        """Очищает список доменных событий."""
        self._domain_events = []

    def confirm(self) -> None:
        """Подтверждает бронирование."""
        if self.status != BookingStatus.PENDING:
            raise BusinessRuleValidationException(
                f"Невозможно подтвердить бронирование в статусе {self.status}"
            )

        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
        self._domain_events.append(
            BookingConfirmed(booking_id=self.id, confirmed_at=datetime.utcnow())
        )

    def cancel(self, reason: Optional[str] = None) -> None:
        """Отменяет бронирование."""
        if self.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
            raise BusinessRuleValidationException(
                f"Невозможно отменить бронирование в статусе {self.status}"
            )

        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self._domain_events.append(BookingCancelled(booking_id=self.id, reason=reason))

    def is_active(self) -> bool:
        """Проверяет, активно ли бронирование."""
        today = date.today()
        return (
            self.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED)
            and self.period.check_out >= today
        )

    @classmethod
    def create(
        cls,
        room: "Room",
        guest_id: EntityId,
        period: DateRange,
        adults: int,
        children: int = 0,
        special_requests: Optional[str] = None,
    ) -> "Booking":
        """Создает новое бронирование."""
        if not room.is_available:
            raise BusinessRuleValidationException("Номер недоступен для бронирования")

        if adults + children > room.capacity:
            raise BusinessRuleValidationException(
                f"Превышена вместимость номера (макс. {room.capacity} человек)"
            )

        booking = cls(
            room_id=room.id,
            guest_id=guest_id,
            period=period,
            adults=adults,
            children=children,
            special_requests=special_requests,
        )

        booking._domain_events.append(
            BookingCreated(
                booking_id=booking.id, room_id=room.id, guest_id=guest_id, period=period
            )
        )

        return booking


class BookingPolicy:
    """Политики и бизнес-правила для бронирований."""

    MAX_BOOKING_DAYS = 30
    MIN_ADVANCE_BOOKING_DAYS = 1

    @classmethod
    def validate_booking_period(cls, period: DateRange) -> None:
        """Проверяет, что период бронирования соответствует политикам."""
        today = date.today()

        # Минимальный срок бронирования - 1 день
        if period.nights < 1:
            raise BusinessRuleValidationException(
                "Минимальный срок бронирования - 1 ночь"
            )

        # Максимальный срок бронирования - 30 дней
        if period.nights > cls.MAX_BOOKING_DAYS:
            raise BusinessRuleValidationException(
                f"Максимальный срок бронирования - {cls.MAX_BOOKING_DAYS} дней"
            )

        # Бронирование должно быть не раньше чем за N дней
        min_check_in = today + timedelta(days=cls.MIN_ADVANCE_BOOKING_DAYS)
        if period.check_in < min_check_in:
            raise BusinessRuleValidationException(
                f"Бронирование должно быть не раньше чем за "
                f"{cls.MIN_ADVANCE_BOOKING_DAYS} дней"
            )

        # Дата заезда должна быть не раньше завтрашнего дня
        if period.check_in <= today:
            raise BusinessRuleValidationException("Дата заезда должна быть в будущем")


class BookingService:
    """Доменный сервис для работы с бронированиями."""

    def __init__(self, booking_repository: "IBookingRepository"):
        self.booking_repository = booking_repository

    def create_booking(
        self,
        room: Room,
        guest_id: EntityId,
        period: DateRange,
        adults: int,
        children: int = 0,
        special_requests: Optional[str] = None,
    ) -> Booking:
        """Создает новое бронирование."""
        # Проверяем доступность номера на выбранные даты
        if not self.is_room_available(room.id, period):
            raise BusinessRuleValidationException(
                f"Номер {room.number} уже забронирован на выбранные даты"
            )

        # Создаем бронирование
        booking = Booking.create(
            room=room,
            guest_id=guest_id,
            period=period,
            adults=adults,
            children=children,
            special_requests=special_requests,
        )

        # Сохраняем бронирование
        self.booking_repository.add(booking)
        return booking

    def is_room_available(
        self,
        room_id: EntityId,
        period: DateRange,
        exclude_booking_id: Optional[EntityId] = None,
    ) -> bool:
        """Проверяет, доступен ли номер на указанные даты."""
        # Получаем все пересекающиеся бронирования для этого номера
        overlapping_bookings = self.booking_repository.find_overlapping_bookings(
            room_id=room_id,
            check_in=period.check_in,
            check_out=period.check_out,
            exclude_booking_id=exclude_booking_id,
        )

        # Если есть активные бронирования, номер недоступен
        return not any(
            booking.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED)
            for booking in overlapping_bookings
        )

    def confirm_booking(self, booking_id: EntityId) -> Booking:
        """Подтверждает бронирование."""
        booking = self.booking_repository.get_by_id(booking_id)
        booking.confirm()
        self.booking_repository.update(booking)
        return booking

    def cancel_booking(
        self, booking_id: EntityId, reason: Optional[str] = None
    ) -> Booking:
        """Отменяет бронирование."""
        booking = self.booking_repository.get_by_id(booking_id)
        booking.cancel(reason)
        self.booking_repository.update(booking)
        return booking
