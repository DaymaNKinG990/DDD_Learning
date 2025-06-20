"""
Доменная модель контекста проживания.

Содержит основные сущности, агрегаты и доменные сервисы
для управления заселением и выселением гостей.
"""

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from shared_kernel import DomainEvent, DomainException, EntityId, Money

from .interfaces import ICheckInRepository


class CheckInStatus(str, Enum):
    """Статусы заселения."""

    PENDING = "pending"  # Ожидает заселения
    IN_HOUSE = "in_house"  # Гость заселен
    CHECKED_OUT = "checked_out"  # Гость выселился
    NO_SHOW = "no_show"  # Гость не явился
    CANCELLED = "cancelled"  # Бронирование отменено


class RoomStatus(str, Enum):
    """Статусы номера."""

    AVAILABLE = "available"  # Свободен и готов к заселению
    OCCUPIED = "occupied"  # Занят
    MAINTENANCE = "maintenance"  # На обслуживании
    CLEANING = "cleaning"  # В процессе уборки
    OUT_OF_ORDER = "out_of_order"  # Неисправен


class RoomType(str, Enum):
    """Типы номеров в отеле."""

    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    FAMILY = "family"


class Room(BaseModel):
    """Номер в отеле."""

    id: EntityId = Field(default_factory=uuid4)
    number: str  # Номер комнаты (например, "101", "202A")
    type: RoomType
    status: RoomStatus = RoomStatus.AVAILABLE
    floor: int
    capacity: int = Field(..., gt=0)
    amenities: List[str] = Field(default_factory=list)  # Удобства в номере
    base_price_per_night: Money
    last_cleaned_at: Optional[datetime] = None
    next_cleaning_scheduled: Optional[datetime] = None

    def mark_as_occupied(self) -> None:
        """Помечает номер как занятый."""
        if self.status == RoomStatus.OCCUPIED:
            return

        if self.status not in (RoomStatus.AVAILABLE, RoomStatus.CLEANING):
            raise DomainException(
                f"Невозможно занять номер в статусе {self.status.value}"
            )

        self.status = RoomStatus.OCCUPIED

    def mark_as_available(self) -> None:
        """Помечает номер как доступный после уборки."""
        self.status = RoomStatus.AVAILABLE
        self.last_cleaned_at = datetime.utcnow()
        self.next_cleaning_scheduled = self._calculate_next_cleaning()

    def mark_for_cleaning(self) -> None:
        """Помечает номер как требующий уборки."""
        self.status = RoomStatus.CLEANING

    def mark_as_maintenance(self) -> None:
        """Помечает номер как неисправный."""
        self.status = RoomStatus.MAINTENANCE

    def _calculate_next_cleaning(self) -> datetime:
        """Рассчитывает следующую дату уборки (по умолчанию через 3 дня)."""
        return datetime.utcnow() + timedelta(days=3)


class Guest(BaseModel):
    """Гость отеля."""

    id: EntityId = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
    phone: str
    document_number: str  # Номер документа, удостоверяющего личность
    address: Optional[Dict[str, Any]] = None  # Адрес гостя
    preferences: Dict[str, Any] = Field(default_factory=dict)  # Предпочтения гостя


class CheckIn(DomainEvent):
    """Событие заселения гостя."""

    check_in_id: EntityId
    room_id: EntityId
    guest_id: EntityId
    booking_id: Optional[EntityId] = None
    check_in_date: date
    check_out_date: date
    room_number: str
    guest_name: str


class CheckOut(DomainEvent):
    """Событие выселения гостя."""

    check_in_id: EntityId
    room_id: EntityId
    guest_id: EntityId
    check_out_date: date
    room_number: str
    guest_name: str


class RoomMaintenanceScheduled(DomainEvent):
    """Событие планирования технического обслуживания номера."""

    room_id: EntityId
    room_number: str
    maintenance_start: datetime
    maintenance_end: datetime
    reason: str


class CheckInRecord(BaseModel):
    """Запись о заселении гостя."""

    id: EntityId = Field(default_factory=uuid4)
    booking_id: Optional[EntityId] = None
    room_id: EntityId
    guest_id: EntityId
    check_in_date: date
    check_out_date: date
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    status: CheckInStatus = CheckInStatus.PENDING
    room_number: str  # Денормализованное поле для удобства
    guest_name: str  # Денормализованное поле для удобства
    adults: int = Field(..., gt=0)
    children: int = Field(0, ge=0)
    special_requests: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
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

    def check_in(self, check_in_time: Optional[datetime] = None) -> None:
        """Выполняет заселение гостя."""
        if self.status != CheckInStatus.PENDING:
            raise DomainException(f"Невозможно заселить гостя в статусе {self.status}")

        self.status = CheckInStatus.IN_HOUSE
        self.actual_check_in = check_in_time or datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Публикуем событие заселения
        self._domain_events.append(
            CheckIn(
                check_in_id=self.id,
                room_id=self.room_id,
                guest_id=self.guest_id,
                booking_id=self.booking_id,
                check_in_date=self.check_in_date,
                check_out_date=self.check_out_date,
                room_number=self.room_number,
                guest_name=self.guest_name,
            )
        )

    def check_out(self, check_out_time: Optional[datetime] = None) -> None:
        """Выполняет выселение гостя."""
        if self.status != CheckInStatus.IN_HOUSE:
            raise DomainException(f"Невозможно выселить гостя в статусе {self.status}")

        self.status = CheckInStatus.CHECKED_OUT
        self.actual_check_out = check_out_time or datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Публикуем событие выселения
        self._domain_events.append(
            CheckOut(
                check_in_id=self.id,
                room_id=self.room_id,
                guest_id=self.guest_id,
                check_out_date=self.check_out_date,
                room_number=self.room_number,
                guest_name=self.guest_name,
            )
        )

    def mark_as_no_show(self) -> None:
        """Помечает бронирование как неявку гостя."""
        if self.status != CheckInStatus.PENDING:
            raise DomainException(
                f"Невозможно отметить как неявку в статусе {self.status}"
            )

        self.status = CheckInStatus.NO_SHOW
        self.updated_at = datetime.utcnow()

    def is_checked_in(self) -> bool:
        """Проверяет, заселен ли гость."""
        return self.status == CheckInStatus.IN_HOUSE

    def is_checked_out(self) -> bool:
        """Проверяет, выселился ли гость."""
        return self.status == CheckInStatus.CHECKED_OUT


class AccommodationService:
    """Доменный сервис для управления проживанием."""

    def __init__(self, check_in_repository: "ICheckInRepository"):
        self.check_in_repository = check_in_repository

    def check_in_guest(
        self,
        room: Room,
        guest: Guest,
        check_in_date: date,
        check_out_date: date,
        adults: int,
        children: int = 0,
        booking_id: Optional[EntityId] = None,
        special_requests: Optional[str] = None,
    ) -> CheckInRecord:
        """Регистрирует заселение гостя."""
        # Проверяем, что номер доступен
        if room.status != RoomStatus.AVAILABLE:
            raise DomainException(f"Номер {room.number} недоступен для заселения")

        # Создаем запись о заселении
        check_in = CheckInRecord(
            booking_id=booking_id,
            room_id=room.id,
            guest_id=guest.id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_number=room.number,
            guest_name=f"{guest.first_name} {guest.last_name}",
            adults=adults,
            children=children,
            special_requests=special_requests,
        )

        # Выполняем заселение
        check_in.check_in()

        # Помечаем номер как занятый
        room.mark_as_occupied()

        return check_in

    def check_out_guest(
        self, check_in_id: EntityId, check_out_time: Optional[datetime] = None
    ) -> CheckInRecord:
        """Выполняет выселение гостя."""
        # Получаем запись о заселении
        check_in = self.check_in_repository.get_by_id(check_in_id)

        # Выполняем выселение
        check_in.check_out(check_out_time)

        return check_in

    def get_current_guests(self) -> List[CheckInRecord]:
        """Возвращает список текущих гостей отеля."""
        return self.check_in_repository.find_by_status(CheckInStatus.IN_HOUSE)

    def get_expected_arrivals(self, date: date) -> List[CheckInRecord]:
        """Возвращает список ожидаемых заездов на указанную дату."""
        return self.check_in_repository.find_expected_arrivals(date)

    def get_expected_departures(self, date: date) -> List[CheckInRecord]:
        """Возвращает список ожидаемых выездов на указанную дату."""
        return self.check_in_repository.find_expected_departures(date)


class RoomMaintenanceService:
    """Сервис для управления техническим обслуживанием номеров."""

    def schedule_maintenance(
        self, room: Room, start_time: datetime, end_time: datetime, reason: str
    ) -> RoomMaintenanceScheduled:
        """Планирует техническое обслуживание номера."""
        if room.status == RoomStatus.OCCUPIED:
            raise DomainException("Невозможно запланировать ТО занятого номера")

        if start_time >= end_time:
            raise DomainException("Время окончания должно быть позже времени начала")

        # Помечаем номер как находящийся на обслуживании
        room.mark_as_maintenance()

        # Создаем событие планирования ТО
        event = RoomMaintenanceScheduled(
            room_id=room.id,
            room_number=room.number,
            maintenance_start=start_time,
            maintenance_end=end_time,
            reason=reason,
        )

        return event
