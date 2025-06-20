# Решение: Ограниченные контексты – Бухгалтерия и Бронирование

В этом документе мы рассмотрим два ограниченных контекста: "Бухгалтерия" (`accounting`) и "Бронирование" (`booking`), а также их "Общее ядро" (`shared_kernel`). Мы проанализируем их доменные модели, сервисы приложений, интерфейсы и инфраструктурные компоненты.

## 1. Общее ядро (Shared Kernel)

Общее ядро содержит элементы, используемые несколькими ограниченными контекстами. Это помогает избежать дублирования кода и обеспечивает согласованность общих концепций.

### 1.1. Ключевые компоненты общего ядра

*   Общие типы данных (например, `Money`, `DateRange`, `Address`)
*   Базовые доменные события и исключения
*   Утилиты (например, генерация ID, работа с датами)

### 1.2. Пример кода из `shared_kernel`

Ниже приведены ключевые компоненты общего ядра, используемые в контекстах `booking` и `accounting`.

**Объект-значение `Money`:**

Представляет денежную сумму с указанием валюты. Используется для расчетов стоимости, платежей и т.д.

```python
from pydantic import BaseModel, Field

class Money(BaseModel):
    """Денежная сумма с валютой."""
    amount: float = Field(..., ge=0, description="Сумма денег")
    currency: str = Field(default="RUB", max_length=3, description="Код валюты (ISO 4217)")

    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            raise TypeError("Можно складывать только объекты Money")
        if self.currency != other.currency:
            raise ValueError("Нельзя складывать разные валюты")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    # ... другие методы (__sub__, __mul__)
```

**Объект-значение `DateRange`:**

Представляет диапазон дат, например, для периода бронирования.

```python
from datetime import date
from pydantic import BaseModel, validator

class DateRange(BaseModel):
    """Диапазон дат."""
    check_in: date
    check_out: date

    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        return v

    @property
    def nights(self) -> int:
        """Количество ночей в бронировании."""
        return (self.check_out - self.check_in).days
```

**Базовый класс `DomainEvent`:**

Основа для всех доменных событий в системе.

```python
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    """Базовый класс для всех доменных событий."""
    event_id: UUID = Field(default_factory=uuid4)
    occurred_on: datetime = Field(default_factory=datetime.utcnow)
    event_type: str

    class Config:
        arbitrary_types_allowed = True
```

**Общие перечисления:**

Используются для стандартизации статусов и типов в различных контекстах.

```python
from enum import Enum

class RoomType(str, Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
```

**Общие исключения:**

Базовые классы для обработки доменных ошибок.

```python
class DomainException(Exception):
    """Базовое исключение для доменных ошибок."""
    pass

class BusinessRuleValidationException(DomainException):
    """Исключение при нарушении бизнес-правил."""
    pass
```

**Утилиты:**

Вспомогательные функции, например, для генерации уникальных идентификаторов.

```python
from uuid import UUID, uuid4

def generate_id() -> UUID:
    """Генерирует новый UUID."""
    return uuid4()
```

## 2. Контекст Бронирования (Booking Context)

Контекст бронирования отвечает за управление процессом бронирования номеров в отеле.

### 2.1. Доменный слой контекста `booking`

Доменный слой контекста `booking` содержит бизнес-логику, связанную с процессом бронирования номеров.

*   **Агрегат `Booking`**: Центральный элемент, представляющий собой бронирование. Он инкапсулирует состояние и поведение, связанное с жизненным циклом бронирования.
    *   **Сущности, входящие в агрегат или тесно связанные**:
        *   `Guest`: Информация о госте.
        *   `Room`: Информация о бронируемом номере (в данном контексте `Room` может рассматриваться как сущность, на которую ссылается `Booking`, или как отдельный агрегат в контексте управления номерным фондом).
    *   **Объекты-значения**: Используются `Money` и `DateRange` из `shared_kernel` для представления стоимости и периода бронирования.
*   **Доменные события**:
    *   `BookingCreated`: Генерируется при создании нового бронирования.
    *   `BookingConfirmed`: Генерируется при подтверждении бронирования.
    *   `BookingCancelled`: Генерируется при отмене бронирования.
*   **Политики/Доменные сервисы**:
    *   `BookingPolicy`: Содержит правила, которые должны соблюдаться при бронировании (например, ограничения на длительность бронирования).

### 2.2. Прикладной слой контекста `booking`

Прикладной слой отвечает за координацию выполнения пользовательских сценариев (use cases). Он использует доменные объекты и сервисы для выполнения бизнес-логики и работает с инфраструктурой через интерфейсы (репозитории, UoW).

*   **Сервисы приложения**:
    *   `BookingApplicationService`: Обрабатывает запросы на создание, изменение, отмену и получение информации о бронированиях.
    *   `RoomApplicationService`: Предоставляет функциональность для поиска доступных номеров.
    *   `GuestApplicationService`: Управляет регистрацией и информацией о гостях.
*   **DTO (Data Transfer Objects)**: Используются для передачи данных между внешними интерфейсами (например, API) и прикладным слоем, а также между прикладным и доменным слоями (хотя последнее стараются минимизировать).
*   **Unit of Work (UoW)**: Паттерн, используемый для управления транзакциями и обеспечения согласованности данных при выполнении операций, затрагивающих несколько репозиториев.

### 2.3. Интерфейсы (Порты) контекста `booking`

Интерфейсы (или порты в терминологии "гексагональной архитектуры") определяют контракты, через которые прикладной и доменный слои взаимодействуют с внешним миром (например, с базой данных, системой уведомлений, другими сервисами). Они обеспечивают слабую связанность и позволяют легко заменять реализации.

В контексте `booking` определены следующие основные интерфейсы:

*   **Репозитории**:
    *   `IBookingRepository`: Контракт для хранения и извлечения агрегатов `Booking`.
    *   `IRoomRepository`: Контракт для работы с информацией о `Room`.
    *   `IGuestRepository`: Контракт для работы с информацией о `Guest`.
*   **`IBookingUnitOfWork`**: Интерфейс для паттерна "Единица Работы" (Unit of Work), который координирует изменения в нескольких репозиториях в рамках одной транзакции.
*   **Другие сервисы-адаптеры**:
    *   `IBookingNotifier`: Абстракция для отправки уведомлений (например, подтверждение бронирования).
    *   `IEventBus`: Абстракция для шины событий, используемой для публикации и обработки доменных событий.
    *   `ILogger`: Абстракция для системы логирования.

#### Пример интерфейса `IBookingRepository`

```python
from abc import abstractmethod
from typing import List, Optional, Protocol # Protocol используется для определения интерфейсов
from uuid import UUID

from ..shared_kernel import EntityId, DateRange
from .domain import Booking, BookingStatus # Импорты из домена Booking

class IBookingRepository(Protocol):
    """Репозиторий для работы с бронированиями."""

    @abstractmethod
    def get_by_id(self, booking_id: EntityId) -> Booking:
        """Возвращает бронирование по идентификатору."""
        ... # Многоточие означает, что реализация отсутствует в протоколе

    @abstractmethod
    def add(self, booking: Booking) -> None:
        """Добавляет новое бронирование."""
        ...

    @abstractmethod
    def update(self, booking: Booking) -> None:
        """Обновляет существующее бронирование."""
        ...

    @abstractmethod
    def find_by_guest(self, guest_id: EntityId) -> List[Booking]:
        """Находит все бронирования гостя."""
        ...

    # ... другие методы, такие как find_by_status, find_overlapping_bookings ...
```

#### Пример интерфейса `IBookingUnitOfWork`

```python
from abc import Protocol

# Импорты интерфейсов репозиториев
from .interfaces import IBookingRepository, IRoomRepository, IGuestRepository

class IBookingUnitOfWork(Protocol):
    """Единица работы (Unit of Work) для контекста бронирования."""

    @property
    def bookings(self) -> IBookingRepository:
        """Репозиторий бронирований."""
        ...

    @property
    def rooms(self) -> IRoomRepository:
        """Репозиторий номеров."""
        ...

    @property
    def guests(self) -> IGuestRepository:
        """Репозиторий гостей."""
        ...

    def commit(self) -> None:
        """Фиксирует все изменения в рамках единицы работы."""
        ...

    def rollback(self) -> None:
        """Откатывает все изменения в рамках единицы работы."""
        ...
```

### 2.4. Инфраструктурный слой контекста `booking`

Инфраструктурный слой содержит конкретные реализации интерфейсов (портов), определенных на предыдущем шаге. Эти реализации зависят от конкретных технологий и внешних систем (базы данных, файловые системы, брокеры сообщений, API и т.д.).

В данном примере используются преимущественно "in-memory" реализации для простоты и демонстрации.

*   **Реализации репозиториев**:
    *   `InMemoryBookingRepository`: Реализация `IBookingRepository`, хранящая данные в памяти.
    *   `InMemoryRoomRepository`: Реализация `IRoomRepository` в памяти.
    *   `InMemoryGuestRepository`: Реализация `IGuestRepository` в памяти.
    *   (Мог бы быть `JsonFileBookingRepository`, наследующий от `JsonFileRepository` и реализующий `IBookingRepository` для хранения данных в JSON).
*   **Реализация Unit of Work**:
    *   `BookingUnitOfWork`: Реализация `IBookingUnitOfWork`, которая может работать с различными типами репозиториев (по умолчанию in-memory).
*   **Другие инфраструктурные компоненты**:
    *   `ConsoleLogger`: Простая реализация `ILogger` для вывода в консоль.
    *   `InMemoryEventBus`: Реализация `IEventBus` для обработки событий в памяти.


### 2.5. Пример кода из `booking`

#### Агрегат `Booking`

{{ ... }}
```python
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from shared_kernel import (
    EntityId, Money, DateRange, DomainEvent, BusinessRuleValidationException,
    BookingStatus, RoomType, generate_id
)

# ... определения Guest и Room (будут показаны ниже или предполагаются существующими) ...

class BookingCreated(DomainEvent):
    """Событие создания бронирования."""
    booking_id: EntityId
    room_id: EntityId
    guest_id: EntityId
    period: DateRange
    event_type: str = "booking_created" # Явно указываем тип события

class BookingCancelled(DomainEvent):
    """Событие отмены бронирования."""
    booking_id: EntityId
    reason: Optional[str] = None
    event_type: str = "booking_cancelled"

class BookingConfirmed(DomainEvent):
    """Событие подтверждения бронирования."""
    booking_id: EntityId
    confirmed_at: datetime
    event_type: str = "booking_confirmed"

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
        return self._domain_events

    def clear_events(self) -> None:
        self._domain_events = []

    def confirm(self) -> None:
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
        if self.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
            raise BusinessRuleValidationException(
                f"Невозможно отменить бронирование в статусе {self.status}"
            )
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self._domain_events.append(
            BookingCancelled(booking_id=self.id, reason=reason)
        )

    @classmethod
    def create(
        cls,
        room_id: EntityId, # Изменено: принимаем room_id вместо объекта Room для упрощения
        guest_id: EntityId,
        period: DateRange,
        adults: int,
        # room_capacity: int, # Добавлено: для проверки вместимости
        children: int = 0,
        special_requests: Optional[str] = None
    ) -> 'Booking':
        # Проверка вместимости должна быть здесь или в BookingPolicy/Application Service
        # if adults + children > room_capacity:
        #     raise BusinessRuleValidationException("Превышена вместимость номера")

        booking = cls(
            room_id=room_id,
            guest_id=guest_id,
            period=period,
            adults=adults,
            children=children,
            special_requests=special_requests
        )
        booking._domain_events.append(
            BookingCreated(
                booking_id=booking.id,
                room_id=room_id,
                guest_id=guest_id,
                period=period
            )
        )
        return booking
```

#### Сущность `Guest`

```python
class Guest(BaseModel):
    """Гость отеля."""
    id: EntityId = Field(default_factory=generate_id)
    first_name: str
    last_name: str
    email: str
    phone: str
    document_number: str
```

#### Сущность `Room` (упрощенное представление для контекста бронирования)

```python
class Room(BaseModel):
    """Номер в отеле (представление в контексте бронирования)."""
    id: EntityId
    number: str
    type: RoomType
    capacity: int
    base_price_per_night: Money
    # is_available: bool - доступность проверяется отдельно, не хранится в этой сущности напрямую
```

#### Политика `BookingPolicy`

```python
from datetime import timedelta

class BookingPolicy:
    """Политики и бизнес-правила для бронирований."""
    MAX_BOOKING_DAYS = 30
    MIN_ADVANCE_BOOKING_DAYS = 1 # Бронирование минимум за 1 день до заезда

    @classmethod
    def validate_booking_period(cls, period: DateRange, check_in_reference_date: date = date.today()) -> None:
        if period.nights < 1:
            raise BusinessRuleValidationException("Минимальный срок бронирования - 1 ночь")
        if period.nights > cls.MAX_BOOKING_DAYS:
            raise BusinessRuleValidationException(
                f"Максимальный срок бронирования - {cls.MAX_BOOKING_DAYS} дней"
            )

        min_check_in_date = check_in_reference_date + timedelta(days=cls.MIN_ADVANCE_BOOKING_DAYS)
        if period.check_in < min_check_in_date:
            raise BusinessRuleValidationException(
                f"Бронирование должно быть не раньше чем через {cls.MIN_ADVANCE_BOOKING_DAYS} день/дней от {check_in_reference_date}"
            )
        if period.check_in <= check_in_reference_date: # Строго больше текущей (или референсной) даты
             raise BusinessRuleValidationException("Дата заезда должна быть в будущем.")
```

#### Сервис приложения `BookingApplicationService` (фрагмент)

```python
from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

# Импорты из shared_kernel и локального домена/интерфейсов
from ..shared_kernel import EntityId, DateRange # Пример относительного импорта
from .interfaces import IBookingUnitOfWork # Используем псевдоним ports из application.py
from .domain import Booking, Room, Guest, BookingService, BookingPolicy, BookingStatus

# DTO для запроса
class CreateBookingRequest(BaseModel):
    """Запрос на создание бронирования."""
    room_id: EntityId
    guest_id: EntityId
    check_in: date
    check_out: date
    adults: int = Field(..., gt=0)
    children: int = Field(0, ge=0)
    special_requests: Optional[str] = None

    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        return v

# DTO для ответа
class BookingDTO(BaseModel):
    """DTO для представления бронирования."""
    id: EntityId
    room_id: EntityId
    guest_id: EntityId
    check_in: date
    check_out: date
    status: BookingStatus # Используем Enum из shared_kernel или domain
    # ... другие поля ...

    @classmethod
    def from_domain(cls, booking: Booking) -> 'BookingDTO':
        return cls(
            id=booking.id,
            room_id=booking.room_id,
            guest_id=booking.guest_id,
            check_in=booking.period.check_in,
            check_out=booking.period.check_out,
            status=booking.status,
            # ... маппинг остальных полей ...
            adults=booking.adults, # Добавлено для полноты
            children=booking.children, # Добавлено для полноты
            special_requests=booking.special_requests # Добавлено для полноты
        )

class BookingApplicationService:
    """Сервис приложения для работы с бронированиями."""

    def __init__(self, uow: IBookingUnitOfWork):
        self._uow = uow
        # Доменный сервис BookingService может быть создан здесь или передан
        # В данном примере он создается внутри методов, использующих репозиторий из UoW

    def create_booking(self, request: CreateBookingRequest) -> BookingDTO:
        """Создает новое бронирование."""
        try:
            with self._uow: # Используем UoW как контекстный менеджер
                period = DateRange(check_in=request.check_in, check_out=request.check_out)
                BookingPolicy.validate_booking_period(period) # Валидация политик

                room = self._uow.rooms.get_by_id(request.room_id)
                if not room: # Проверка существования комнаты
                    raise ValueError(f"Комната с ID {request.room_id} не найдена.")

                # guest = self._uow.guests.get_by_id(request.guest_id) # Аналогично для гостя
                # if not guest:
                #     raise ValueError(f"Гость с ID {request.guest_id} не найден.")

                # Используем доменный сервис BookingService для проверки доступности и создания
                # В оригинальном коде BookingService инициализируется с booking_repository
                # Здесь мы можем либо передать uow.bookings, либо создать BookingService внутри
                booking_domain_service = BookingService(self._uow.bookings)

                # Проверка доступности номера (логика из BookingService.create_booking)
                if not booking_domain_service.is_room_available(room.id, period):
                     raise ValueError( # Используем ValueError или кастомное исключение
                        f"Номер {room.number} уже забронирован на выбранные даты"
                    )

                # Создание бронирования через фабричный метод агрегата
                booking = Booking.create(
                    room_id=room.id, # Передаем room.id и room.capacity
                    # room_capacity=room.capacity, # Убрано, т.к. в Booking.create нет этого параметра
                    guest_id=request.guest_id, # Предполагаем, что guest_id валиден
                    period=period,
                    adults=request.adults,
                    children=request.children,
                    special_requests=request.special_requests
                )

                self._uow.bookings.add(booking)
                self._uow.commit() # Явный коммит в конце

            return BookingDTO.from_domain(booking)

        except Exception as e:
            # self._uow.rollback() - rollback будет вызван автоматически при выходе из with, если было исключение
            raise # Перевыбрасываем исключение для обработки выше
```

#### Пример реализации `InMemoryBookingRepository`

```python
from typing import Dict, List, Optional
from uuid import UUID

from ..shared_kernel import EntityId, DateRange, BookingStatus
from .interfaces import IBookingRepository # Импорт интерфейса
from .domain import Booking # Импорт доменной модели

class InMemoryBookingRepository(IBookingRepository):
    """Реализация репозитория бронирований в памяти."""

    def __init__(self):
        self._bookings: Dict[EntityId, Booking] = {}

    def get_by_id(self, booking_id: EntityId) -> Booking:
        if booking_id not in self._bookings:
            # В реальном приложении лучше использовать кастомные исключения
            raise KeyError(f"Booking with id {booking_id} not found")
        return self._bookings[booking_id]

    def add(self, booking: Booking) -> None:
        if booking.id in self._bookings:
            raise ValueError(f"Booking with id {booking.id} already exists")
        self._bookings[booking.id] = booking

    def update(self, booking: Booking) -> None:
        if booking.id not in self._bookings:
            raise KeyError(f"Booking with id {booking.id} not found")
        self._bookings[booking.id] = booking

    def find_by_guest(self, guest_id: EntityId) -> List[Booking]:
        return [
            booking for booking in self._bookings.values()
            if booking.guest_id == guest_id
        ]

    # ... другие методы ...
```

#### Пример реализации `BookingUnitOfWork`

```python
from typing import Optional

from .interfaces import ( # Импорты интерфейсов
    IBookingRepository,
    IRoomRepository,
    IGuestRepository,
    IBookingUnitOfWork,
    ILogger
)
# Импорты конкретных реализаций (могут быть заменены другими)
from .infrastructure import (
    InMemoryBookingRepository,
    InMemoryRoomRepository,
    InMemoryGuestRepository,
    ConsoleLogger
)

class BookingUnitOfWork(IBookingUnitOfWork):
    """Единица работы для контекста бронирования."""

    def __init__(
        self,
        bookings_repo: Optional[IBookingRepository] = None,
        rooms_repo: Optional[IRoomRepository] = None,
        guests_repo: Optional[IGuestRepository] = None,
        logger: Optional[ILogger] = None
    ):
        # Если репозитории не переданы, используются in-memory реализации по умолчанию
        self._bookings = bookings_repo or InMemoryBookingRepository()
        self._rooms = rooms_repo or InMemoryRoomRepository()
        self._guests = guests_repo or InMemoryGuestRepository()
        self._logger = logger or ConsoleLogger()
        self._committed = False # Флаг для отслеживания состояния транзакции

    @property
    def bookings(self) -> IBookingRepository:
        return self._bookings

    @property
    def rooms(self) -> IRoomRepository:
        return self._rooms

    @property
    def guests(self) -> IGuestRepository:
        return self._guests

    def commit(self) -> None:
        # В реальном приложении здесь была бы логика фиксации транзакции в БД
        # Например, self._session.commit() для SQLAlchemy
        self._committed = True
        self._logger.info("BookingUnitOfWork committed")

    def rollback(self) -> None:
        # Логика отката транзакции
        # Например, self._session.rollback()
        self._committed = False
        self._logger.warning("BookingUnitOfWork rolled back")

    # Реализация контекстного менеджера для удобства использования
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None: # Если не было исключений
            self.commit()
        else: # Если было исключение
            self.rollback()
        return False # Пробрасываем исключение дальше, если оно было
```

## 3. Контекст Бухгалтерии (Accounting Context)

Контекст бухгалтерии отвечает за финансовые операции, связанные с бронированиями и другими услугами. Он управляет счетами, платежами, финансовыми периодами и отчетностью.

### 3.1. Доменный слой контекста `accounting`

Доменный слой содержит основные бизнес-сущности, правила и логику, специфичную для бухгалтерии.

*   **Агрегаты и Сущности**:
    *   `Invoice`: Агрегат, представляющий счет на оплату. Корень агрегата. Включает позиции счета (`InvoiceItem`), общие суммы, статус и методы для управления жизненным циклом счета.
    *   `Payment`: Агрегат, представляющий платеж по счету. Корень агрегата. Содержит информацию о сумме, методе оплаты, статусе.
    *   `FinancialPeriod`: Сущность, определяющая финансовый период для отчетности и закрытия.
*   **Объекты-значения**:
    *   `InvoiceItem`: Позиция в счете с деталями (описание, количество, цена, налоги, скидки).
    *   `Money`: Используется из `shared_kernel` для представления денежных сумм.
*   **Перечисления**:
    *   `InvoiceStatus`, `PaymentStatus`, `PaymentMethod`, `TransactionType`, `FinancialPeriodStatus`: Определяют возможные состояния и типы для доменных объектов.
*   **Доменные сервисы**:
    *   `AccountingService`: Координирует операции, такие как создание счетов, регистрация и применение платежей.
*   **Классы для отчетности**:
    *   `FinancialReport`: Генерирует финансовые отчеты на основе счетов и платежей за период.

### 3.1. Доменный слой контекста `accounting`

*   Сущности (например, `Invoice`, `Payment`, `LedgerEntry`)
*   Объекты-значения
*   Агрегаты
*   Доменные события (например, `InvoiceIssued`, `PaymentReceived`)

#### Агрегат `Invoice` (фрагмент)

```python
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, root_validator

from shared_kernel import EntityId, DomainEvent, DomainException, Money # Предполагаем, что shared_kernel доступен

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    # ... другие статусы ...
    CANCELLED = "cancelled"

class InvoiceItem(BaseModel):
    id: EntityId = Field(default_factory=uuid4)
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Money
    tax_rate: Decimal = Field(0, ge=0, le=100)
    discount: Money = Field(Money(amount=0))
    total: Money # Рассчитывается автоматически

    @root_validator(pre=True)
    def calculate_total(cls, values):
        # ... логика расчета total для InvoiceItem ...
        if 'total' in values and values['total'] is not None:
            return values
        quantity = Decimal(str(values.get('quantity', 1)))
        unit_price = values.get('unit_price')
        tax_rate = Decimal(str(values.get('tax_rate', 0)))
        discount = values.get('discount', Money(amount=0))
        if not unit_price: raise ValueError("unit_price is required")
        subtotal = unit_price * quantity - discount
        tax = subtotal * (tax_rate / 100)
        values['total'] = subtotal + tax
        return values

class Invoice(DomainEvent): # Может быть и просто Entity, если не публикует события сам
    id: EntityId = Field(default_factory=uuid4)
    number: str
    guest_id: EntityId
    issue_date: date = Field(default_factory=date.today)
    due_date: date
    status: InvoiceStatus = InvoiceStatus.DRAFT
    items: List[InvoiceItem] = Field(default_factory=list)
    subtotal: Money
    tax_amount: Money
    total: Money
    # ... другие поля и метаданные ...

    @root_validator(pre=True)
    def calculate_totals(cls, values):
        # ... логика расчета subtotal, tax_amount, total для Invoice ...
        if 'subtotal' in values and 'total' in values and 'tax_amount' in values:
            return values
        items_data = values.get('items', [])
        items = [InvoiceItem(**item) if isinstance(item, dict) else item for item in items_data]

        subtotal = Money(amount=0)
        tax_amount = Money(amount=0)
        discount_amount_val = Money(amount=0) # Используем другое имя, чтобы не конфликтовать с полем

        for item_obj in items:
            item_subtotal_calc = item_obj.unit_price * item_obj.quantity - item_obj.discount
            item_tax_calc = item_subtotal_calc * (item_obj.tax_rate / 100)

            subtotal += item_obj.unit_price * item_obj.quantity
            tax_amount += item_tax_calc
            discount_amount_val += item_obj.discount

        total_calc = subtotal - discount_amount_val + tax_amount

        values['subtotal'] = subtotal
        values['tax_amount'] = tax_amount
        values['discount_amount'] = discount_amount_val # Присваиваем рассчитанное значение
        values['total'] = total_calc
        values['items'] = [item.dict() for item in items] # Обновляем items, если они были dict
        return values

    def add_item(self, item: InvoiceItem) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise DomainException("Невозможно изменить счет в текущем статусе")
        self.items.append(item)
        self._recalculate_totals_from_internal_items() # Вызов внутреннего метода
        self.updated_at = datetime.utcnow()

    def _recalculate_totals_from_internal_items(self) -> None:
        """Пересчитывает итоговые суммы счета на основе текущих self.items."""
        # Эта функция должна быть похожа на calculate_totals, но работать с self.items
        subtotal = Money(amount=0)
        tax_amount = Money(amount=0)
        discount_amount_val = Money(amount=0)

        for item_obj in self.items: # self.items уже содержит объекты InvoiceItem
            item_subtotal_calc = item_obj.unit_price * item_obj.quantity - item_obj.discount
            item_tax_calc = item_subtotal_calc * (item_obj.tax_rate / 100)

            subtotal += item_obj.unit_price * item_obj.quantity
            tax_amount += item_tax_calc
            discount_amount_val += item_obj.discount

        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount_val
        self.total = subtotal - discount_amount_val + tax_amount

    def issue(self) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise DomainException("Счет уже выставлен или аннулирован")
        if not self.items:
            raise DomainException("Невозможно выставить пустой счет")
        self.status = InvoiceStatus.ISSUED
        self.updated_at = datetime.utcnow()
    # ... другие методы (cancel, remove_item) ...
```

#### Агрегат `Payment` (фрагмент)

```python
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    # ... другие методы ...

class Payment(DomainEvent): # Может быть и просто Entity
    id: EntityId = Field(default_factory=uuid4)
    invoice_id: EntityId
    amount: Money
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    processed_at: Optional[datetime] = None
    # ... другие поля и метаданные ...

    def complete(self, transaction_id: Optional[str] = None) -> None:
        if self.status != PaymentStatus.PENDING:
            raise DomainException("Платеж уже обработан")
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id
        self.updated_at = datetime.utcnow()

    def fail(self, reason: Optional[str] = None) -> None:
        if self.status != PaymentStatus.PENDING:
            raise DomainException("Платеж уже обработан")
        self.status = PaymentStatus.FAILED
        # ... логика обработки неудачного платежа ...

    # ... другие методы (refund) ...

### 3.2. Прикладной слой контекста `accounting`

Прикладной слой координирует выполнение бизнес-операций, используя доменные объекты и сервисы. Он не содержит бизнес-логики, а делегирует ее доменному слою. Также он отвечает за управление транзакциями и взаимодействие с внешними сервисами через интерфейсы (порты).

*   **DTO (Data Transfer Objects)**:
    *   `InvoiceDTO`, `PaymentDTO`, `FinancialPeriodDTO`, `FinancialReportDTO`: Используются для передачи данных между слоями. Преобразуют доменные модели в простые структуры данных и обратно.
*   **Команды (Commands)**:
    *   `CreateInvoiceCommand`, `IssueInvoiceCommand`, `CancelInvoiceCommand`: Представляют намерения пользователя или системы изменить состояние (например, создать или выставить счет).
    *   `RecordPaymentCommand`, `ProcessPaymentCommand`, `IssueRefundCommand`: Команды для управления платежами.
*   **Запросы (Queries)**:
    *   `GetInvoiceQuery`, `ListInvoicesQuery`: Представляют запросы на получение данных без изменения состояния.
*   **Прикладные сервисы**:
    *   `AccountingApplicationService`: Обрабатывает команды и запросы, взаимодействует с репозиториями через Unit of Work, использует доменные сервисы и может вызывать внешние сервисы (например, платежный шлюз, сервис email-уведомлений).

#### Пример команды `CreateInvoiceCommand`

```python
from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from shared_kernel import EntityId, Money

class InvoiceItemDTO(BaseModel):
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Money
    tax_rate: Decimal = Field(0, ge=0, le=100)
    discount: Money = Field(Money(amount=0))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CreateInvoiceCommand(BaseModel):
    guest_id: EntityId
    items: List[InvoiceItemDTO]
    due_date: date
    booking_id: Optional[EntityId] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### Фрагмент `AccountingApplicationService`

```python
from .domain import Invoice, InvoiceItem, DomainAccountingService # Упрощенные импорты
from .interfaces import (
    IAccountingUnitOfWork,
    IPaymentGateway,
    IEmailService,
    IAccountingService # Интерфейс, который реализует сервис
)
# ... другие импорты DTO и команд ...

class AccountingApplicationService(IAccountingService):
    def __init__(
        self,
        uow: IAccountingUnitOfWork,
        payment_gateway: IPaymentGateway,
        email_service: IEmailService,
        # ... другие зависимости ...
    ):
        self.uow = uow
        self.payment_gateway = payment_gateway
        self.email_service = email_service
        self.domain_service = DomainAccountingService(uow.invoices) # Используем доменный сервис

    async def create_invoice_from_command(self, command: CreateInvoiceCommand) -> InvoiceDTO:
        # Преобразование DTO из команды в доменные InvoiceItem
        domain_items = [
            InvoiceItem(
                description=item_dto.description,
                quantity=item_dto.quantity,
                unit_price=item_dto.unit_price,
                tax_rate=item_dto.tax_rate,
                discount=item_dto.discount,
                metadata=item_dto.metadata
                # total будет рассчитан в доменной модели InvoiceItem или Invoice
            ) for item_dto in command.items
        ]

        try:
            async with self.uow: # Используем Unit of Work для транзакционности
                invoice = await self.domain_service.create_invoice(
                    guest_id=command.guest_id,
                    items=domain_items,
                    due_date=command.due_date,
                    booking_id=command.booking_id,
                    notes=command.notes,
                    metadata=command.metadata
                )
                # В реальном domain_service.create_invoice может не сохранять,
                # а только создавать объект. Сохранение - задача UoW.
                await self.uow.invoices.save(invoice)
                await self.uow.commit() # Явный коммит, если UoW не делает это автоматически при выходе из контекста

            return InvoiceDTO.from_domain(invoice)
        except Exception as e:
            # await self.uow.rollback() # UoW может делать это автоматически при исключении
            raise # Пробрасываем исключение дальше

    async def issue_invoice_from_command(self, command: IssueInvoiceCommand) -> InvoiceDTO:
        try:
            async with self.uow:
                invoice = await self.uow.invoices.get_by_id(command.invoice_id)
                if not invoice:
                    raise ValueError(f"Счет с ID {command.invoice_id} не найден")

                invoice.issue() # Вызов доменного метода

                await self.uow.invoices.save(invoice)
                await self.uow.commit()

                # Опциональная отправка email
                # await self.email_service.send_invoice_issued_notification(invoice)

            return InvoiceDTO.from_domain(invoice)
        except Exception as e:
            raise
    # ... другие методы для обработки команд и запросов ...

### 3.3. Интерфейсы (Порты) контекста `accounting`

Интерфейсный слой определяет контракты (абстрактные базовые классы или протоколы в Python), которые должны быть реализованы инфраструктурным слоем (адаптеры). Эти интерфейсы обеспечивают слабую связанность между прикладным/доменным слоями и конкретными технологиями инфраструктуры.

*   **Репозитории**:
    *   `IInvoiceRepository`: Определяет операции для доступа к данным счетов (CRUD, поиск).
    *   `IPaymentRepository`: Определяет операции для доступа к данным платежей.
    *   `IFinancialPeriodRepository`: Определяет операции для доступа к данным финансовых периодов.
*   **Unit of Work**:
    *   `IAccountingUnitOfWork`: Абстракция для управления транзакциями, объединяющая несколько репозиториев. Гарантирует атомарность операций.
*   **Внешние сервисы (Адаптеры)**:
    *   `IPaymentGateway`: Абстракция для взаимодействия с платежными системами (например, Stripe, PayPal).
    *   `IFinancialReportGenerator`: Абстракция для создания финансовых отчетов в различных форматах (PDF, CSV).
    *   `IEmailService`: Абстракция для отправки уведомлений по электронной почте.
*   **Интерфейс прикладного сервиса**:
    *   `IAccountingService`: Определяет публичный контракт прикладного сервиса `AccountingApplicationService`, который используется другими контекстами или внешними клиентами.

#### Пример интерфейса `IInvoiceRepository`

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from shared_kernel import EntityId
from .domain import Invoice, InvoiceStatus # Упрощенные импорты

class IInvoiceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, invoice_id: EntityId) -> Optional[Invoice]:
        pass

    @abstractmethod
    async def save(self, invoice: Invoice) -> None:
        pass

    @abstractmethod
    async def list_by_guest(
        self,
        guest_id: EntityId,
        status: Optional[InvoiceStatus] = None
    ) -> List[Invoice]:
        pass
    # ... другие методы ...
```

#### Пример интерфейса `IPaymentGateway`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from shared_kernel import Money

class IPaymentGateway(ABC):
    @abstractmethod
    async def process_payment(
        self,
        amount: Money,
        payment_method_token: str, # Например, токен карты
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]: # Возвращает результат операции (id транзакции, статус)
        pass

    @abstractmethod
    async def process_refund(
        self,
        transaction_id: str, # ID оригинальной транзакции для возврата
        amount: Money,
        reason: Optional[str] = None
    ) -> Dict[str, Any]: # Возвращает результат операции
        pass
    # ... другие методы ...

### 3.4. Инфраструктурный слой контекста `accounting`

Инфраструктурный слой содержит конкретные реализации интерфейсов (портов), определенных в предыдущем слое. Он отвечает за все технические детали: взаимодействие с базами данных, файловой системой, внешними API, отправку сообщений и т.д.

В данном примере решения контекста `accounting` используются **in-memory** реализации для репозиториев и Unit of Work, а также **заглушки** (dummy/mock implementations) для внешних сервисов. Это упрощает запуск и тестирование примера без настройки внешних зависимостей.

*   **Реализации репозиториев**:
    *   `InMemoryInvoiceRepository`: Хранит счета в словаре Python.
    *   `InMemoryPaymentRepository`: Хранит платежи в словаре.
    *   `InMemoryFinancialPeriodRepository`: Хранит финансовые периоды в словаре.
*   **Реализация Unit of Work**:
    *   `AccountingUnitOfWork`: Управляет in-memory репозиториями. `commit()` и `rollback()` адаптированы для работы с данными в памяти.
*   **Адаптеры внешних сервисов**:
    *   `DummyPaymentGateway`: Имитирует работу платежного шлюза, возвращая успешный или неуспешный результат обработки платежа/возврата.
    *   `ConsoleEmailService`: Вместо отправки реальных email, выводит информацию о письме в консоль.
    *   `SimpleFinancialReportGenerator`: Генерирует простые текстовые финансовые отчеты на основе данных из UoW.

#### Пример реализации `InMemoryInvoiceRepository`

```python
from typing import Dict, List, Optional, Set
from shared_kernel import EntityId
from .domain import Invoice, InvoiceStatus
from .interfaces import IInvoiceRepository

class InMemoryInvoiceRepository(IInvoiceRepository):
    def __init__(self):
        self._invoices: Dict[EntityId, Invoice] = {}
        # ... другие внутренние структуры для индексации ...

    async def get_by_id(self, invoice_id: EntityId) -> Optional[Invoice]:
        return self._invoices.get(invoice_id)

    async def save(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice
        # ... обновление индексов ...

    # ... другие методы ...
```

#### Пример реализации `DummyPaymentGateway`

```python
from typing import Dict, Any, Optional
from uuid import uuid4
from shared_kernel import Money
from .interfaces import IPaymentGateway

class DummyPaymentGateway(IPaymentGateway):
    def __init__(self, success_rate: float = 1.0):
        self.success_rate = success_rate
        self.processed_payments: Dict[str, Dict[str, Any]] = {}

    async def process_payment(
        self,
        amount: Money,
        payment_method_token: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        transaction_id = f"TXN-{uuid4().hex[:8].upper()}"
        # Имитация успеха/неудачи
        success = hash(transaction_id) % 100 < int(self.success_rate * 100)

        result = {
            "transaction_id": transaction_id,
            "status": "completed" if success else "failed",
            # ... другие детали ...
        }
        self.processed_payments[transaction_id] = result
        return result
    # ... другие методы ...

### 3.5. Пример кода из `accounting`: Взаимодействие слоев

Ниже приведены примеры, демонстрирующие, как прикладной сервис `AccountingApplicationService` использует доменные объекты, репозитории (через Unit of Work) и другие сервисы для выполнения операций.

#### 1. Создание нового счета (`create_invoice`)

Этот метод в `AccountingApplicationService` координирует создание нового счета.

```python
# В accounting/application.py -> class AccountingApplicationService

async def create_invoice(
    self,
    guest_id: EntityId,
    items: List[InvoiceItem], # Принимает доменные объекты InvoiceItem
    due_date: date,
    booking_id: Optional[EntityId] = None,
    notes: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Invoice: # Возвращает доменный объект Invoice
    """Создает новый счет."""
    try:
        # 1. Используется доменный сервис для создания экземпляра Invoice
        #    Доменный сервис инкапсулирует логику создания номера счета,
        #    расчета итоговых сумм и т.д.
        invoice = await self.domain_service.create_invoice(
            guest_id=guest_id,
            items=items,
            due_date=due_date,
            booking_id=booking_id,
            notes=notes,
            metadata=metadata or {}
        )

        # 2. Счет сохраняется через репозиторий, полученный из Unit of Work
        await self.uow.invoices.save(invoice)

        # 3. Изменения фиксируются через Unit of Work
        await self.uow.commit()

        return invoice

    except Exception as e:
        # В случае ошибки изменения откатываются
        await self.uow.rollback()
        raise

# Вспомогательный доменный сервис (может быть в domain.py)
# class DomainAccountingService:
#     def __init__(self, invoice_repo: IInvoiceRepository):
#         self.invoice_repo = invoice_repo # Может понадобиться для генерации номера

#     async def create_invoice(self, ...) -> Invoice:
#         # ... логика генерации номера счета (например, на основе последнего)
#         # ... создание объекта Invoice
#         # ... расчет total, subtotal, tax_amount
#         new_invoice = Invoice(...)
#         return new_invoice
```
*   **Прикладной сервис** (`AccountingApplicationService`) получает данные (возможно, через DTO, которые затем преобразуются в доменные объекты `InvoiceItem`).
*   Он делегирует создание объекта `Invoice` **доменному сервису** (`DomainAccountingService`). Доменный сервис может содержать логику, специфичную для создания счета, например, генерацию уникального номера счета или сложные расчеты.
*   Созданный доменный объект `Invoice` сохраняется с использованием **репозитория** (`self.uow.invoices`), доступ к которому осуществляется через **Unit of Work** (`self.uow`).
*   Операция завершается вызовом `self.uow.commit()` для фиксации изменений или `self.uow.rollback()` в случае ошибки.

#### 2. Регистрация платежа (`record_payment`)

Этот метод обрабатывает регистрацию нового платежа по счету.

```python
# В accounting/application.py -> class AccountingApplicationService

async def record_payment(
    self,
    invoice_id: EntityId,
    amount: Money,
    payment_method_str: str, # Строка из DTO/команды
    transaction_id: Optional[str] = None,
    notes: Optional[str] = None,
    process_online: bool = False,
    payment_details: Optional[Dict[str, Any]] = None # Для онлайн-обработки
) -> Payment: # Возвращает доменный объект Payment
    """Регистрирует платеж по счету."""
    try:
        # 1. Получаем счет из репозитория
        invoice = await self.uow.invoices.get_by_id(invoice_id)
        if not invoice:
            raise ValueError(f"Счет с ID {invoice_id} не найден")

        # Преобразуем строку метода оплаты в доменный enum
        payment_method_enum = PaymentMethod(payment_method_str)

        # 2. Создаем доменный объект Payment
        payment = Payment.create(
            invoice_id=invoice.id,
            amount=amount,
            payment_method=payment_method_enum,
            transaction_id=transaction_id,
            notes=notes
        )

        # 3. Если требуется онлайн-обработка, используем платежный шлюз
        if process_online:
            if not self.payment_gateway:
                raise RuntimeError("Платежный шлюз не настроен.")

            gateway_response = await self.payment_gateway.process_payment(
                amount=payment.amount,
                payment_method=payment_method_enum.value, # или токен/детали карты
                payment_details=payment_details or {},
                metadata={'invoice_id': str(invoice.id), 'payment_id': str(payment.id)}
            )

            payment.process_online_payment(
                gateway_transaction_id=gateway_response.get("transaction_id"),
                status=PaymentStatus.COMPLETED if gateway_response.get("status") == "completed"
                       else PaymentStatus.FAILED,
                response_data=gateway_response
            )
        else:
            # Для оффлайн платежей или уже обработанных
            payment.confirm_manual_payment(transaction_id=transaction_id)

        # 4. Обновляем статус счета на основе нового платежа
        invoice.apply_payment(payment)

        # 5. Сохраняем платеж и обновленный счет
        await self.uow.payments.save(payment)
        await self.uow.invoices.save(invoice)
        await self.uow.commit()

        # 6. Отправляем подтверждение платежа (опционально)
        if payment.status == PaymentStatus.COMPLETED and hasattr(self, 'email_service'):
             await self.email_service.send_payment_confirmation(
                 to_email=invoice.customer_email or "",
                 payment=payment
             )

        return payment

    except Exception as e:
        await self.uow.rollback()
        raise
```
*   **Прикладной сервис** получает данные о платеже.
*   Загружает соответствующий **доменный объект** `Invoice` из репозитория.
*   Создает **доменный объект** `Payment`.
*   Если платеж должен быть обработан онлайн, сервис вызывает метод `process_payment` у **интерфейса платежного шлюза** (`self.payment_gateway`). Реализация этого интерфейса (например, `DummyPaymentGateway` или реальный шлюз) находится в инфраструктурном слое.
*   Обновляет статус `Payment` на основе ответа от шлюза.
*   Вызывает метод `apply_payment` у доменного объекта `Invoice`, чтобы обновить его баланс и статус.
*   Сохраняет `Payment` и `Invoice` через репозитории и фиксирует UoW.
*   Может использовать **сервис email-уведомлений** (`self.email_service`) для отправки подтверждения.

Эти примеры показывают, как прикладной слой оркестрирует взаимодействие, делегируя бизнес-логику доменному слою и используя инфраструктурный слой через четко определенные интерфейсы.

### 3.5. Пример кода из `accounting`

Здесь будут приведены примеры кода из контекста `accounting`.

## 4. Взаимодействие контекстов

Описание того, как контексты `booking` и `accounting` могут взаимодействовать, например, через доменные события или другие механизмы интеграции.
