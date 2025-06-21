"""
Интерфейсы (порты) для контекста бронирования.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Awaitable, Callable, List, Optional, Protocol, Type, TypeVar

from ..shared_kernel import DomainEvent, EntityId
from .domain import Booking, Guest, Room

T_Event = TypeVar("T_Event", bound=DomainEvent)


class ILogger(Protocol):
    """Интерфейс для логгера."""

    def info(self, message: str, **kwargs: Any) -> None: ...
    def error(self, message: str, **kwargs: Any) -> None: ...
    def warning(self, message: str, **kwargs: Any) -> None: ...
    def debug(self, message: str, **kwargs: Any) -> None: ...


class IEventBus(Protocol):
    """Интерфейс для шины событий."""

    async def publish(self, event: DomainEvent) -> None: ...
    def subscribe(
        self, event_type: Type[T_Event], handler: Callable[[T_Event], Awaitable[None]]
    ) -> None: ...


class IBookingRepository(Protocol):
    """Интерфейс репозитория для бронирований."""

    async def add(self, booking: Booking) -> None: ...
    async def get_by_id(self, booking_id: EntityId) -> Booking | None: ...
    async def update(self, booking: Booking) -> None: ...
    async def find_by_guest(self, guest_id: EntityId) -> List[Booking]: ...
    async def find_by_status(self, status: str) -> List[Booking]: ...
    async def find_overlapping_bookings(
        self,
        room_id: EntityId,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[EntityId] = None,
    ) -> List[Booking]: ...


class IRoomRepository(Protocol):
    """Интерфейс репозитория для комнат."""

    async def get_by_id(self, room_id: EntityId) -> Room | None: ...
    async def find_available_rooms(
        self,
        check_in: date,
        check_out: date,
        min_capacity: int,
        room_type: Optional[str] = None,
    ) -> List[Room]: ...


class IGuestRepository(Protocol):
    """Интерфейс репозитория для гостей."""

    async def add(self, guest: Guest) -> None: ...
    async def get_by_id(self, guest_id: EntityId) -> Guest | None: ...
    async def find_by_email(self, email: str) -> Guest | None: ...


class IBookingUnitOfWork(Protocol):
    """Интерфейс Unit of Work для контекста Booking."""

    @property
    def bookings(self) -> IBookingRepository: ...
    @property
    def rooms(self) -> IRoomRepository: ...
    @property
    def guests(self) -> IGuestRepository: ...
    @property
    def event_bus(self) -> IEventBus: ...

    async def __aenter__(self) -> IBookingUnitOfWork: ...
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
