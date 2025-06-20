"""
Прикладной слой контекста проживания.

Содержит сервисы приложения, которые координируют
взаимодействие между внешними интерфейсами и доменной моделью.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from ..booking.infrastructure import ConsoleLogger
from ..shared_kernel import EntityId
from . import interfaces as ports
from .domain import (
    AccommodationService,
    CheckInRecord,
    Guest,
    Room,
    RoomMaintenanceService,
    RoomStatus,
)

# DTO (Data Transfer Objects) для входящих данных


class CheckInGuestRequest(BaseModel):
    """Запрос на заселение гостя."""

    room_id: EntityId
    guest_id: EntityId
    check_in_date: date
    check_out_date: date
    adults: int = Field(..., gt=0)
    children: int = Field(0, ge=0)
    booking_id: Optional[EntityId] = None
    special_requests: Optional[str] = None

    @validator("check_out_date")
    def check_out_after_check_in(cls, v, values):
        if "check_in_date" in values and v <= values["check_in_date"]:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return v


class CheckOutGuestRequest(BaseModel):
    """Запрос на выселение гостя."""

    check_in_id: EntityId
    check_out_time: Optional[datetime] = None


class ScheduleMaintenanceRequest(BaseModel):
    """Запрос на планирование технического обслуживания номера."""

    room_id: EntityId
    start_time: datetime
    end_time: datetime
    reason: str

    @validator("end_time")
    def end_time_after_start_time(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("Время окончания должно быть позже времени начала")
        return v


# DTO для исходящих данных


class RoomDTO(BaseModel):
    """DTO для представления номера."""

    id: EntityId
    number: str
    type: str
    status: str
    floor: int
    capacity: int
    amenities: List[str]
    base_price_per_night: Dict[str, Any]
    last_cleaned_at: Optional[datetime]
    next_cleaning_scheduled: Optional[datetime]

    @classmethod
    def from_domain(cls, room: Room) -> "RoomDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=room.id,
            number=room.number,
            type=room.type.value,
            status=room.status.value,
            floor=room.floor,
            capacity=room.capacity,
            amenities=room.amenities,
            base_price_per_night=room.base_price_per_night,
            last_cleaned_at=room.last_cleaned_at,
            next_cleaning_scheduled=room.next_cleaning_scheduled,
        )


class GuestDTO(BaseModel):
    """DTO для представления гостя."""

    id: EntityId
    first_name: str
    last_name: str
    email: str
    phone: str
    document_number: str
    address: Optional[Dict[str, Any]]
    preferences: Dict[str, Any]

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
            address=guest.address,
            preferences=guest.preferences,
        )


class CheckInRecordDTO(BaseModel):
    """DTO для представления записи о заселении."""

    id: EntityId
    booking_id: Optional[EntityId]
    room_id: EntityId
    guest_id: EntityId
    check_in_date: date
    check_out_date: date
    actual_check_in: Optional[datetime]
    actual_check_out: Optional[datetime]
    status: str
    room_number: str
    guest_name: str
    adults: int
    children: int
    special_requests: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, check_in: CheckInRecord) -> "CheckInRecordDTO":
        """Создает DTO из доменной модели."""
        return cls(
            id=check_in.id,
            booking_id=check_in.booking_id,
            room_id=check_in.room_id,
            guest_id=check_in.guest_id,
            check_in_date=check_in.check_in_date,
            check_out_date=check_in.check_out_date,
            actual_check_in=check_in.actual_check_in,
            actual_check_out=check_in.actual_check_out,
            status=check_in.status.value,
            room_number=check_in.room_number,
            guest_name=check_in.guest_name,
            adults=check_in.adults,
            children=check_in.children,
            special_requests=check_in.special_requests,
            created_at=check_in.created_at,
            updated_at=check_in.updated_at,
        )


# Сервисы приложения


class AccommodationApplicationService:
    """Сервис приложения для управления проживанием."""

    def __init__(
        self,
        uow: ports.IAccommodationUnitOfWork,
        event_publisher: Optional[ports.IEventPublisher] = None,
        logger: Optional[ports.ILogger] = None,
    ):
        """Инициализирует сервис."""
        self._uow = uow
        self._event_publisher = event_publisher
        self._logger = logger or ConsoleLogger()
        self._accommodation_service = AccommodationService(uow.check_ins)

    def check_in_guest(self, request: CheckInGuestRequest) -> CheckInRecordDTO:
        """Выполняет заселение гостя."""
        try:
            # Получаем номер и гостя
            room = self._uow.rooms.get_by_id(request.room_id)
            guest = self._uow.guests.get_by_id(request.guest_id)

            # Выполняем заселение
            check_in = self._accommodation_service.check_in_guest(
                room=room,
                guest=guest,
                check_in_date=request.check_in_date,
                check_out_date=request.check_out_date,
                adults=request.adults,
                children=request.children,
                booking_id=request.booking_id,
                special_requests=request.special_requests,
            )

            # Сохраняем запись о заселении
            self._uow.check_ins.add(check_in)

            # Обновляем статус номера
            self._uow.rooms.update(room)

            # Фиксируем изменения
            self._uow.commit()

            # Публикуем доменные события, если есть подписчики
            if self._event_publisher:
                for event in check_in.domain_events:
                    self._event_publisher.publish(event)
                check_in.clear_events()

            return CheckInRecordDTO.from_domain(check_in)

        except Exception as e:
            self._uow.rollback()
            self._logger.error(f"Ошибка при заселении гостя: {str(e)}")
            raise

    def check_out_guest(self, request: CheckOutGuestRequest) -> CheckInRecordDTO:
        """Выполняет выселение гостя."""
        try:
            # Получаем запись о заселении
            check_in = self._uow.check_ins.get_by_id(request.check_in_id)

            # Выполняем выселение
            check_in.check_out(request.check_out_time)

            # Обновляем запись
            self._uow.check_ins.update(check_in)

            # Помечаем номер как требующий уборки
            room = self._uow.rooms.get_by_id(check_in.room_id)
            room.mark_for_cleaning()
            self._uow.rooms.update(room)

            # Фиксируем изменения
            self._uow.commit()

            # Публикуем доменные события, если есть подписчики
            if self._event_publisher:
                for event in check_in.domain_events:
                    self._event_publisher.publish(event)
                check_in.clear_events()

            return CheckInRecordDTO.from_domain(check_in)

        except Exception as e:
            self._uow.rollback()
            self._logger.error(f"Ошибка при выселении гостя: {str(e)}")
            raise

    def get_check_in_record(self, check_in_id: EntityId) -> CheckInRecordDTO:
        """Возвращает информацию о заселении."""
        check_in = self._uow.check_ins.get_by_id(check_in_id)
        return CheckInRecordDTO.from_domain(check_in)

    def list_current_guests(self) -> List[CheckInRecordDTO]:
        """Возвращает список текущих гостей отеля."""
        check_ins = self._uow.check_ins.find_current_guests()
        return [CheckInRecordDTO.from_domain(ci) for ci in check_ins]

    def list_expected_arrivals(self, date: date) -> List[CheckInRecordDTO]:
        """Возвращает список ожидаемых заездов на указанную дату."""
        check_ins = self._uow.check_ins.find_expected_arrivals(date)
        return [CheckInRecordDTO.from_domain(ci) for ci in check_ins]

    def list_expected_departures(self, date: date) -> List[CheckInRecordDTO]:
        """Возвращает список ожидаемых выездов на указанную дату."""
        check_ins = self._uow.check_ins.find_expected_departures(date)
        return [CheckInRecordDTO.from_domain(ci) for ci in check_ins]


class RoomApplicationService:
    """Сервис приложения для работы с номерами."""

    def __init__(
        self,
        uow: ports.IAccommodationUnitOfWork,
        event_publisher: Optional[ports.IEventPublisher] = None,
        logger: Optional[ports.ILogger] = None,
    ):
        """Инициализирует сервис."""
        self._uow = uow
        self._event_publisher = event_publisher
        self._logger = logger or ConsoleLogger()
        self._maintenance_service = RoomMaintenanceService()

    def get_room(self, room_id: EntityId) -> RoomDTO:
        """Возвращает информацию о номере."""
        room = self._uow.rooms.get_by_id(room_id)
        return RoomDTO.from_domain(room)

    def list_available_rooms(
        self,
        check_in: date,
        check_out: date,
        room_type: Optional[str] = None,
        capacity: Optional[int] = None,
    ) -> List[RoomDTO]:
        """Возвращает список доступных номеров."""
        rooms = self._uow.rooms.find_available_rooms(
            check_in=check_in,
            check_out=check_out,
            room_type=room_type,
            capacity=capacity,
        )
        return [RoomDTO.from_domain(room) for room in rooms]

    def list_rooms_by_status(self, status: str) -> List[RoomDTO]:
        """Возвращает список номеров с указанным статусом."""
        try:
            room_status = RoomStatus(status)
            rooms = self._uow.rooms.find_by_status(room_status)
            return [RoomDTO.from_domain(room) for room in rooms]
        except ValueError:
            raise ValueError(f"Неизвестный статус номера: {status}")

    def schedule_maintenance(
        self, request: ScheduleMaintenanceRequest
    ) -> Dict[str, Any]:
        """Планирует техническое обслуживание номера."""
        try:
            # Получаем номер
            room = self._uow.rooms.get_by_id(request.room_id)

            # Планируем техническое обслуживание
            event = self._maintenance_service.schedule_maintenance(
                room=room,
                start_time=request.start_time,
                end_time=request.end_time,
                reason=request.reason,
            )

            # Обновляем информацию о номере
            self._uow.rooms.update(room)

            # Фиксируем изменения
            self._uow.commit()

            # Публикуем событие, если есть подписчики
            if self._event_publisher:
                self._event_publisher.publish(event)

            return {
                "room_id": room.id,
                "room_number": room.number,
                "status": room.status.value,
                "maintenance_start": request.start_time,
                "maintenance_end": request.end_time,
                "reason": request.reason,
            }

        except Exception as e:
            self._uow.rollback()
            self._logger.error(f"Ошибка при планировании ТО номера: {str(e)}")
            raise

    def complete_maintenance(self, room_id: EntityId) -> RoomDTO:
        """Завершает техническое обслуживание номера."""
        try:
            # Получаем номер
            room = self._uow.rooms.get_by_id(room_id)

            # Проверяем, что номер находится на обслуживании
            if room.status != RoomStatus.MAINTENANCE:
                raise ValueError("Номер не находится на техническом обслуживании")

            # Помечаем номер как доступный
            room.mark_as_available()

            # Обновляем информацию о номере
            self._uow.rooms.update(room)

            # Фиксируем изменения
            self._uow.commit()

            return RoomDTO.from_domain(room)

        except Exception as e:
            self._uow.rollback()
            self._logger.error(f"Ошибка при завершении ТО номера: {str(e)}")
            raise


class GuestApplicationService:
    """Сервис приложения для работы с гостями."""

    def __init__(
        self,
        uow: ports.IAccommodationUnitOfWork,
        logger: Optional[ports.ILogger] = None,
    ):
        """Инициализирует сервис."""
        self._uow = uow
        self._logger = logger or ConsoleLogger()

    def register_guest(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        document_number: str,
        address: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> GuestDTO:
        """Регистрирует нового гостя."""
        try:
            # Создаем гостя
            guest = Guest(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                document_number=document_number,
                address=address or {},
                preferences=preferences or {},
            )

            # Сохраняем гостя
            self._uow.guests.add(guest)
            self._uow.commit()

            return GuestDTO.from_domain(guest)

        except Exception as e:
            self._uow.rollback()
            self._logger.error(f"Ошибка при регистрации гостя: {str(e)}")
            raise

    def get_guest(self, guest_id: EntityId) -> GuestDTO:
        """Возвращает информацию о госте."""
        guest = self._uow.guests.get_by_id(guest_id)
        return GuestDTO.from_domain(guest)

    def find_guest_by_document(self, document_number: str) -> Optional[GuestDTO]:
        """Находит гостя по номеру документа."""
        guest = self._uow.guests.find_by_document(document_number)
        if guest is None:
            return None
        return GuestDTO.from_domain(guest)

    def find_guests_by_name(self, first_name: str, last_name: str) -> List[GuestDTO]:
        """Находит гостей по имени и фамилии."""
        guests = self._uow.guests.find_by_name(first_name, last_name)
        return [GuestDTO.from_domain(guest) for guest in guests]

    def update_guest(self, guest_id: EntityId, **updates) -> GuestDTO:
        """Обновляет информацию о госте."""
        try:
            # Получаем гостя
            guest = self._uow.guests.get_by_id(guest_id)

            # Обновляем поля
            for field, value in updates.items():
                if hasattr(guest, field) and value is not None:
                    setattr(guest, field, value)

            # Обновляем гостя
            self._uow.guests.update(guest)
            self._uow.commit()

            return GuestDTO.from_domain(guest)

        except Exception as e:
            self._uow.rollback()
            self._logger.error(f"Ошибка при обновлении данных гостя: {str(e)}")
            raise
