"""
Прикладной слой контекста бронирования.

Содержит сервисы приложения, которые координируют
взаимодействие между внешними интерфейсами и доменной моделью.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from shared_kernel import BookingStatus, DateRange, EntityId, generate_id

from . import interfaces as ports
from .domain import Booking, BookingPolicy, BookingService, Guest, Room

# DTO (Data Transfer Objects) для входящих данных


class CreateBookingRequest(BaseModel):
    """Запрос на создание бронирования."""

    room_id: EntityId
    guest_id: EntityId
    check_in: date
    check_out: date
    adults: int = Field(..., gt=0)
    children: int = Field(0, ge=0)
    special_requests: Optional[str] = None

    @validator("check_out")
    def check_out_after_check_in(cls, v, values):
        if "check_in" in values and v <= values["check_in"]:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return v


class UpdateBookingRequest(BaseModel):
    """Запрос на обновление бронирования."""

    booking_id: EntityId
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    special_requests: Optional[str] = None

    @validator("check_out")
    def check_out_after_check_in(cls, v, values):
        if (
            v is not None
            and "check_in" in values
            and values["check_in"] is not None
            and v <= values["check_in"]
        ):
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return v


class CancelBookingRequest(BaseModel):
    """Запрос на отмену бронирования."""

    booking_id: EntityId
    reason: Optional[str] = None


class RegisterGuestRequest(BaseModel):
    """Запрос на регистрацию нового гостя."""

    first_name: str
    last_name: str
    email: str
    phone: str
    document_number: str


# DTO для исходящих данных


class BookingDTO(BaseModel):
    """DTO для представления бронирования."""

    id: EntityId
    room_id: EntityId
    guest_id: EntityId
    check_in: date
    check_out: date
    status: BookingStatus
    adults: int
    children: int
    special_requests: Optional[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, booking: Booking) -> "BookingDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=booking.id,
            room_id=booking.room_id,
            guest_id=booking.guest_id,
            check_in=booking.period.check_in,
            check_out=booking.period.check_out,
            status=booking.status,
            adults=booking.adults,
            children=booking.children,
            special_requests=booking.special_requests,
            created_at=booking.created_at.isoformat(),
            updated_at=booking.updated_at.isoformat(),
        )


class RoomDTO(BaseModel):
    """DTO для представления номера."""

    id: EntityId
    number: str
    type: str
    capacity: int
    amenities: List[str]
    base_price_per_night: Dict[str, Any]
    is_available: bool

    @classmethod
    def from_domain(cls, room: Room) -> "RoomDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=room.id,
            number=room.number,
            type=room.type.value,
            capacity=room.capacity,
            amenities=room.amenities,
            base_price_per_night={
                "amount": room.base_price_per_night.amount,
                "currency": room.base_price_per_night.currency,
            },
            is_available=room.is_available,
        )


class GuestDTO(BaseModel):
    """DTO для представления гостя."""

    id: EntityId
    first_name: str
    last_name: str
    email: str
    phone: str
    document_number: str

    @classmethod
    def from_domain(cls, guest: Guest) -> "GuestDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=guest.id,
            first_name=guest.first_name,
            last_name=guest.last_name,
            email=guest.email,
            phone=guest.phone,
            document_number=guest.document_number,
        )


# Сервисы приложения


class BookingApplicationService:
    """Сервис приложения для работы с бронированиями."""

    def __init__(self, uow: ports.IBookingUnitOfWork):
        """Инициализирует сервис."""
        self._uow = uow
        self._booking_service = BookingService(self._uow.bookings)

    async def create_booking(self, request: CreateBookingRequest) -> BookingDTO:
        """Создает новое бронирование."""
        async with self._uow:
            # Проверяем период бронирования
            period = DateRange(check_in=request.check_in, check_out=request.check_out)
            BookingPolicy.validate_booking_period(period)

            # Получаем номер и гостя
            room = await self._uow.rooms.get_by_id(request.room_id)
            if not room:
                raise ValueError(f"Room with id {request.room_id} not found")

            guest = await self._uow.guests.get_by_id(request.guest_id)
            if not guest:
                raise ValueError(f"Guest with id {request.guest_id} not found")

            # Создаем бронирование через доменный сервис
            booking = await self._booking_service.create_booking(
                room=room,
                guest_id=guest.id,
                period=period,
                adults=request.adults,
                children=request.children,
                special_requests=request.special_requests,
            )

            # UoW commit'нет изменения автоматически при выходе из `async with`
            return BookingDTO.from_domain(booking)

    async def get_booking(self, booking_id: EntityId) -> Optional[BookingDTO]:
        """Возвращает информацию о бронировании."""
        booking = await self._uow.bookings.get_by_id(booking_id)
        if not booking:
            return None
        return BookingDTO.from_domain(booking)

    async def update_booking(self, request: UpdateBookingRequest) -> BookingDTO:
        """Обновляет информацию о бронировании."""
        async with self._uow:
            # Получаем бронирование
            booking = await self._uow.bookings.get_by_id(request.booking_id)
            if not booking:
                raise ValueError(f"Booking with id {request.booking_id} not found")

            # Обновляем информацию, если передана
            if request.check_in is not None or request.check_out is not None:
                check_in = (
                    request.check_in
                    if request.check_in is not None
                    else booking.period.check_in
                )
                check_out = (
                    request.check_out
                    if request.check_out is not None
                    else booking.period.check_out
                )

                # Проверяем новый период
                new_period = DateRange(check_in=check_in, check_out=check_out)
                BookingPolicy.validate_booking_period(new_period)

                # Проверяем доступность номера на новый период
                if not await self._booking_service.is_room_available(
                    room_id=booking.room_id,
                    period=new_period,
                    exclude_booking_id=booking.id,
                ):
                    raise ValueError("Номер недоступен на выбранные даты")

                # Обновляем период
                booking.period = new_period

            if request.special_requests is not None:
                booking.special_requests = request.special_requests

            # Обновляем метаданные
            booking.updated_at = datetime.now()

            # Сохраняем изменения
            await self._uow.bookings.update(booking)
            # UoW commit'нет изменения автоматически при выходе из `async with`

            return BookingDTO.from_domain(booking)

    async def cancel_booking(self, request: CancelBookingRequest) -> BookingDTO:
        """Отменяет бронирование."""
        async with self._uow:
            # Отменяем бронирование через доменный сервис
            booking = await self._booking_service.cancel_booking(
                booking_id=request.booking_id, reason=request.reason
            )
            # UoW commit'нет изменения автоматически при выходе из `async with`
            return BookingDTO.from_domain(booking)

    async def list_bookings(
        self,
        guest_id: Optional[EntityId] = None,
        status: Optional[BookingStatus] = None,
    ) -> List[BookingDTO]:
        """Возвращает список бронирований с фильтрацией."""
        if guest_id is not None:
            bookings = await self._uow.bookings.find_by_guest(guest_id)
        elif status is not None:
            bookings = await self._uow.bookings.find_by_status(status.value)
        else:
            # В реальном приложении здесь была бы пагинация
            bookings = []

        return [BookingDTO.from_domain(booking) for booking in bookings]


class RoomApplicationService:
    """Сервис приложения для работы с номерами."""

    def __init__(self, uow: ports.IBookingUnitOfWork):
        """Инициализирует сервис."""
        self._uow = uow

    async def list_available_rooms(
        self,
        check_in: date,
        check_out: date,
        room_type: Optional[str] = None,
        capacity: Optional[int] = None,
    ) -> List[RoomDTO]:
        """Возвращает список доступных номеров."""
        # Проверяем период
        period = DateRange(check_in=check_in, check_out=check_out)
        BookingPolicy.validate_booking_period(period)

        # Получаем все доступные номера
        rooms = await self._uow.rooms.find_available_rooms(
            check_in=check_in,
            check_out=check_out,
            room_type=room_type,
            min_capacity=capacity or 1,
        )

        # Фильтруем номера, которые уже забронированы на выбранные даты
        available_rooms = []
        booking_service = BookingService(self._uow.bookings)

        for room in rooms:
            if await booking_service.is_room_available(room.id, period):
                available_rooms.append(room)

        return [RoomDTO.from_domain(room) for room in available_rooms]

    async def get_room(self, room_id: EntityId) -> Optional[RoomDTO]:
        """Возвращает информацию о номере."""
        room = await self._uow.rooms.get_by_id(room_id)
        if not room:
            return None
        return RoomDTO.from_domain(room)


class GuestApplicationService:
    """Сервис приложения для работы с гостями."""

    def __init__(self, uow: ports.IBookingUnitOfWork):
        """Инициализирует сервис."""
        self._uow = uow

    async def register_guest(
        self,
        request: RegisterGuestRequest,
    ) -> GuestDTO:
        """Регистрирует нового гостя."""
        async with self._uow:
            # Проверяем, что гость с таким email еще не зарегистрирован
            existing_guest = await self._uow.guests.find_by_email(request.email)
            if existing_guest is not None:
                raise ValueError(f"Гость с email {request.email} уже зарегистрирован")

            guest = Guest(
                id=generate_id(),
                first_name=request.first_name,
                last_name=request.last_name,
                email=request.email,
                phone=request.phone,
                document_number=request.document_number,
            )
            await self._uow.guests.add(guest)
            # UoW commit'нет изменения автоматически при выходе из `async with`
            return GuestDTO.from_domain(guest)

    async def get_guest(self, guest_id: EntityId) -> Optional[GuestDTO]:
        """Возвращает информацию о госте."""
        guest = await self._uow.guests.get_by_id(guest_id)
        if not guest:
            return None
        return GuestDTO.from_domain(guest)

    async def find_guest_by_email(self, email: str) -> Optional[GuestDTO]:
        """Находит гостя по email."""
        guest = await self._uow.guests.find_by_email(email)
        if not guest:
            return None
        return GuestDTO.from_domain(guest)
