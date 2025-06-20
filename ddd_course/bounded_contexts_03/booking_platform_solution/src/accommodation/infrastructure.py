"""
Инфраструктурный слой контекста проживания.

Содержит реализации репозиториев и других интерфейсов,
зависимые от конкретных технологий (БД, внешние сервисы и т.д.).
"""

import json
import sys
from datetime import date, datetime, timedelta
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
)
from uuid import UUID

from pydantic import BaseModel

from ..accounting.shared_kernel import DomainEvent, EntityId
from . import interfaces as ports
from .domain import (
    CheckInRecord,
    CheckInStatus,
    Guest,
    Room,
    RoomStatus,
    RoomType,
)

T_Event = TypeVar("T_Event", bound=DomainEvent)
T = TypeVar("T", bound=BaseModel)


class InMemoryRoomRepository(ports.IRoomRepository):
    """Реализация репозитория номеров в памяти."""

    def __init__(self) -> None:
        self._rooms: Dict[EntityId, Room] = {}
        self._room_by_number: Dict[str, Room] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self) -> None:
        """Инициализирует тестовые данные."""
        sample_rooms = [
            Room(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                number="101",
                type=RoomType.STANDARD,
                floor=1,
                capacity=2,
                amenities=["TV", "Wi-Fi", "Mini-bar"],
                base_price_per_night={"amount": 3500.0, "currency": "RUB"},
                status=RoomStatus.AVAILABLE,
                last_cleaned_at=datetime.utcnow() - timedelta(days=1),
            ),
            Room(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                number="201",
                type=RoomType.DELUXE,
                floor=2,
                capacity=2,
                amenities=["TV", "Wi-Fi", "Mini-bar", "Sea View"],
                base_price_per_night={"amount": 5000.0, "currency": "RUB"},
                status=RoomStatus.AVAILABLE,
                last_cleaned_at=datetime.utcnow() - timedelta(days=1),
            ),
            Room(
                id=UUID("33333333-3333-3333-3333-333333333333"),
                number="301",
                type=RoomType.SUITE,
                floor=3,
                capacity=4,
                amenities=["TV", "Wi-Fi", "Mini-bar", "Sea View", "Jacuzzi"],
                base_price_per_night={"amount": 10000.0, "currency": "RUB"},
                status=RoomStatus.AVAILABLE,
                last_cleaned_at=datetime.utcnow() - timedelta(days=1),
            ),
            Room(
                id=UUID("44444444-4444-4444-4444-444444444444"),
                number="401",
                type=RoomType.FAMILY,
                floor=4,
                capacity=6,
                amenities=["TV", "Wi-Fi", "Kitchen", "Balcony"],
                base_price_per_night={"amount": 15000.0, "currency": "RUB"},
                status=RoomStatus.AVAILABLE,
                last_cleaned_at=datetime.utcnow() - timedelta(days=1),
            ),
        ]

        for room in sample_rooms:
            self._rooms[room.id] = room
            self._room_by_number[room.number] = room

    def get_by_id(self, room_id: EntityId) -> Room:
        if room_id not in self._rooms:
            raise KeyError(f"Room with id {room_id} not found")
        return self._rooms[room_id]

    def get_by_number(self, room_number: str) -> Room:
        if room_number not in self._room_by_number:
            raise KeyError(f"Room with number {room_number} not found")
        return self._room_by_number[room_number]

    def find_available_rooms(
        self,
        check_in: date,
        check_out: date,
        room_type: Optional[str] = None,
        capacity: Optional[int] = None,
    ) -> List[Room]:
        # В реальном приложении здесь была бы проверка доступности по датам
        rooms = list(self._rooms.values())

        # Фильтруем по типу, если указан
        if room_type is not None:
            rooms = [r for r in rooms if r.type.value.lower() == room_type.lower()]

        # Фильтруем по вместимости, если указана
        if capacity is not None:
            rooms = [r for r in rooms if r.capacity >= capacity]

        return rooms

    def update(self, room: Room) -> None:
        if room.id not in self._rooms:
            raise KeyError(f"Room with id {room.id} not found")
        self._rooms[room.id] = room
        self._room_by_number[room.number] = room

    def find_by_status(self, status: RoomStatus) -> List[Room]:
        return [r for r in self._rooms.values() if r.status == status]


class InMemoryGuestRepository(ports.IGuestRepository):
    """Реализация репозитория гостей в памяти."""

    def __init__(self) -> None:
        self._guests: Dict[EntityId, Guest] = {}
        self._email_index: Dict[str, Guest] = {}
        self._document_index: Dict[str, Guest] = {}
        self._name_index: Dict[tuple, Guest] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self) -> None:
        """Инициализирует тестовые данные."""
        sample_guests = [
            Guest(
                id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                first_name="Иван",
                last_name="Иванов",
                email="ivan.ivanov@example.com",
                phone="+79101234567",
                document_number="1234567890",
                address={
                    "country": "Россия",
                    "city": "Москва",
                    "street": "Ленина",
                    "house": "1",
                    "apartment": "10",
                },
                preferences={"preferred_floor": "high", "smoking": False},
            ),
            Guest(
                id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                first_name="Петр",
                last_name="Петров",
                email="petr.petrov@example.com",
                phone="+79111234567",
                document_number="0987654321",
                address={
                    "country": "Россия",
                    "city": "Санкт-Петербург",
                    "street": "Невский проспект",
                    "house": "10",
                    "apartment": "20",
                },
                preferences={"preferred_floor": "low", "smoking": True},
            ),
        ]

        for guest in sample_guests:
            self.add(guest)

    def get_by_id(self, guest_id: EntityId) -> Guest:
        if guest_id not in self._guests:
            raise KeyError(f"Guest with id {guest_id} not found")
        return self._guests[guest_id]

    def find_by_name(self, first_name: str, last_name: str) -> List[Guest]:
        name_key = (first_name.lower(), last_name.lower())
        return [g for key, g in self._name_index.items() if key == name_key]

    def find_by_document(self, document_number: str) -> Optional[Guest]:
        return self._document_index.get(document_number)

    def add(self, guest: Guest) -> None:
        if guest.id in self._guests:
            raise ValueError(f"Guest with id {guest.id} already exists")
        if guest.email.lower() in self._email_index:
            raise ValueError(f"Guest with email {guest.email} already exists")
        if guest.document_number in self._document_index:
            raise ValueError(
                f"Guest with document number {guest.document_number} already exists"
            )

        self._guests[guest.id] = guest
        self._email_index[guest.email.lower()] = guest
        self._document_index[guest.document_number] = guest
        self._name_index[(guest.first_name.lower(), guest.last_name.lower())] = guest

    def update(self, guest: Guest) -> None:
        if guest.id not in self._guests:
            raise KeyError(f"Guest with id {guest.id} not found")

        # Обновляем индексы, если изменились email или номер документа
        existing = self._guests[guest.id]

        if existing.email.lower() != guest.email.lower():
            if guest.email.lower() in self._email_index:
                raise ValueError(f"Email {guest.email} is already in use")
            del self._email_index[existing.email.lower()]
            self._email_index[guest.email.lower()] = guest

        if existing.document_number != guest.document_number:
            if guest.document_number in self._document_index:
                raise ValueError(
                    f"Document number {guest.document_number} is already in use"
                )
            del self._document_index[existing.document_number]
            self._document_index[guest.document_number] = guest

        # Обновляем имя в индексе, если изменилось
        if (
            existing.first_name.lower() != guest.first_name.lower()
            or existing.last_name.lower() != guest.last_name.lower()
        ):
            del self._name_index[
                (existing.first_name.lower(), existing.last_name.lower())
            ]
            self._name_index[(guest.first_name.lower(), guest.last_name.lower())] = (
                guest
            )

        # Обновляем гостя
        self._guests[guest.id] = guest


class InMemoryCheckInRepository(ports.ICheckInRepository):
    """Реализация репозитория заселений в памяти."""

    def __init__(self) -> None:
        self._check_ins: Dict[EntityId, CheckInRecord] = {}
        self._check_ins_by_guest: Dict[EntityId, Set[EntityId]] = {}
        self._check_ins_by_room: Dict[EntityId, Set[EntityId]] = {}
        self._check_ins_by_status: Dict[CheckInStatus, Set[EntityId]] = {}
        self._check_ins_by_arrival: Dict[date, Set[EntityId]] = {}
        self._check_ins_by_departure: Dict[date, Set[EntityId]] = {}

    def get_by_id(self, check_in_id: EntityId) -> CheckInRecord:
        if check_in_id not in self._check_ins:
            raise KeyError(f"Check-in with id {check_in_id} not found")
        return self._check_ins[check_in_id]

    def find_by_guest(self, guest_id: EntityId) -> List[CheckInRecord]:
        check_in_ids = self._check_ins_by_guest.get(guest_id, set())
        return [self._check_ins[check_in_id] for check_in_id in check_in_ids]

    def find_by_room(self, room_id: EntityId) -> List[CheckInRecord]:
        check_in_ids = self._check_ins_by_room.get(room_id, set())
        return [self._check_ins[check_in_id] for check_in_id in check_in_ids]

    def find_by_status(self, status: CheckInStatus) -> List[CheckInRecord]:
        check_in_ids = self._check_ins_by_status.get(status, set())
        return [self._check_ins[check_in_id] for check_in_id in check_in_ids]

    def find_expected_arrivals(self, date: date) -> List[CheckInRecord]:
        check_in_ids = self._check_ins_by_arrival.get(date, set())
        return [self._check_ins[check_in_id] for check_in_id in check_in_ids]

    def find_expected_departures(self, date: date) -> List[CheckInRecord]:
        check_in_ids = self._check_ins_by_departure.get(date, set())
        return [self._check_ins[check_in_id] for check_in_id in check_in_ids]

    def find_current_guests(self) -> List[CheckInRecord]:
        return self.find_by_status(CheckInStatus.IN_HOUSE)

    def add(self, check_in: CheckInRecord) -> None:
        if check_in.id in self._check_ins:
            raise ValueError(f"Check-in with id {check_in.id} already exists")

        self._check_ins[check_in.id] = check_in

        # Обновляем индексы
        # По гостю
        if check_in.guest_id not in self._check_ins_by_guest:
            self._check_ins_by_guest[check_in.guest_id] = set()
        self._check_ins_by_guest[check_in.guest_id].add(check_in.id)

        # По номеру
        if check_in.room_id not in self._check_ins_by_room:
            self._check_ins_by_room[check_in.room_id] = set()
        self._check_ins_by_room[check_in.room_id].add(check_in.id)

        # По статусу
        if check_in.status not in self._check_ins_by_status:
            self._check_ins_by_status[check_in.status] = set()
        self._check_ins_by_status[check_in.status].add(check_in.id)

        # По дате заезда
        if check_in.check_in_date not in self._check_ins_by_arrival:
            self._check_ins_by_arrival[check_in.check_in_date] = set()
        self._check_ins_by_arrival[check_in.check_in_date].add(check_in.id)

        # По дате выезда
        if check_in.check_out_date not in self._check_ins_by_departure:
            self._check_ins_by_departure[check_in.check_out_date] = set()
        self._check_ins_by_departure[check_in.check_out_date].add(check_in.id)

    def update(self, check_in: CheckInRecord) -> None:
        if check_in.id not in self._check_ins:
            raise KeyError(f"Check-in with id {check_in.id} not found")

        existing = self._check_ins[check_in.id]

        # Обновляем индексы, если изменились ключевые поля
        if existing.status != check_in.status:
            # Удаляем из старого статуса
            if existing.status in self._check_ins_by_status:
                self._check_ins_by_status[existing.status].discard(check_in.id)
            # Добавляем в новый статус
            if check_in.status not in self._check_ins_by_status:
                self._check_ins_by_status[check_in.status] = set()
            self._check_ins_by_status[check_in.status].add(check_in.id)

        if existing.check_in_date != check_in.check_in_date:
            # Удаляем из старой даты заезда
            if existing.check_in_date in self._check_ins_by_arrival:
                self._check_ins_by_arrival[existing.check_in_date].discard(check_in.id)
            # Добавляем в новую дату заезда
            if check_in.check_in_date not in self._check_ins_by_arrival:
                self._check_ins_by_arrival[check_in.check_in_date] = set()
            self._check_ins_by_arrival[check_in.check_in_date].add(check_in.id)

        if existing.check_out_date != check_in.check_out_date:
            # Удаляем из старой даты выезда
            if existing.check_out_date in self._check_ins_by_departure:
                self._check_ins_by_departure[existing.check_out_date].discard(
                    check_in.id
                )
            # Добавляем в новую дату выезда
            if check_in.check_out_date not in self._check_ins_by_departure:
                self._check_ins_by_departure[check_in.check_out_date] = set()
            self._check_ins_by_departure[check_in.check_out_date].add(check_in.id)

        # Обновляем запись
        self._check_ins[check_in.id] = check_in


class ConsoleLogger(ports.ILogger):
    """Простая реализация логгера, выводящая сообщения в консоль."""

    def info(self, message: str, **kwargs) -> None:
        print(f"[INFO] {message}", flush=True)
        if kwargs:
            print("  Context:", json.dumps(kwargs, default=str, indent=2), flush=True)

    def error(self, message: str, **kwargs) -> None:
        print(f"[ERROR] {message}", file=sys.stderr, flush=True)
        if kwargs:
            print(
                "  Context:",
                json.dumps(kwargs, default=str, indent=2),
                file=sys.stderr,
                flush=True,
            )

    def warning(self, message: str, **kwargs) -> None:
        print(f"[WARNING] {message}", file=sys.stderr, flush=True)
        if kwargs:
            print(
                "  Context:",
                json.dumps(kwargs, default=str, indent=2),
                file=sys.stderr,
                flush=True,
            )

    def debug(self, message: str, **kwargs) -> None:
        """Записывает отладочное сообщение в консоль."""
        print(f"[DEBUG] {message}", flush=True)
        if kwargs:
            print("  Context:", json.dumps(kwargs, default=str, indent=2), flush=True)


class InMemoryEventBus(ports.IEventPublisher):
    """Реализация шины событий в памяти."""

    def __init__(self, logger: Optional[ports.ILogger] = None):
        self._subscribers: Dict[
            Type[DomainEvent], List[Callable[[DomainEvent], None]]
        ] = {}
        self._logger = logger or ConsoleLogger()

    def publish(self, event: DomainEvent) -> None:
        """Публикует событие."""
        event_type = type(event)
        if event_type not in self._subscribers:
            self._logger.info(f"No subscribers for event type {event_type.__name__}")
            return

        self._logger.info(
            f"Publishing event: {event_type.__name__}", event=event.dict()
        )

        for handler in self._subscribers[event_type]:
            try:
                handler(event)
            except Exception as e:
                self._logger.error(
                    f"Error in event handler for {event_type.__name__}",
                    error=str(e),
                    event=event.dict(),
                )

    def subscribe(
        self, event_type: Type[T_Event], handler: Callable[[T_Event], None]
    ) -> None:  # Уточнена типизация
        """Подписывает обработчик на события указанного типа."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        self._logger.info(f"Subscribed handler to {event_type.__name__} events")


class AccommodationUnitOfWork(ports.IAccommodationUnitOfWork):
    """Единица работы для контекста проживания."""

    def __init__(
        self,
        rooms_repo: Optional[ports.IRoomRepository] = None,
        guests_repo: Optional[ports.IGuestRepository] = None,
        check_ins_repo: Optional[ports.ICheckInRepository] = None,
        logger: Optional[ports.ILogger] = None,
    ):
        self._rooms = rooms_repo or InMemoryRoomRepository()
        self._guests = guests_repo or InMemoryGuestRepository()
        self._check_ins = check_ins_repo or InMemoryCheckInRepository()
        self._logger = logger or ConsoleLogger()
        self._committed = False

    @property
    def rooms(self) -> ports.IRoomRepository:
        return self._rooms

    @property
    def guests(self) -> ports.IGuestRepository:
        return self._guests

    @property
    def check_ins(self) -> ports.ICheckInRepository:
        return self._check_ins

    def commit(self) -> None:
        """Фиксирует все изменения."""
        # В реальном приложении здесь была бы фиксация транзакции
        self._committed = True
        self._logger.info("AccommodationUnitOfWork committed")

    def rollback(self) -> None:
        """Откатывает все изменения."""
        # В реальном приложении здесь был бы откат транзакции
        self._committed = False
        self._logger.warning("AccommodationUnitOfWork rolled back")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False  # Пробрасываем исключение дальше, если оно было


class ConsoleEmailService(ports.IEmailService):
    """Заглушка сервиса отправки email, выводящая письма в консоль."""

    def __init__(self, logger: Optional[ports.ILogger] = None):
        self._logger = logger or ConsoleLogger()

    def send_email(
        self, to: str, subject: str, template_name: str, context: Dict[str, Any]
    ) -> bool:
        """Выводит информацию о письме в консоль."""
        self._logger.info(
            "Sending email",
            to=to,
            subject=subject,
            template=template_name,
            context=context,
        )
        return True
