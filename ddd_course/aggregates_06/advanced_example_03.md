# Продвинутый пример: Агрегат "Отправление"

Этот пример демонстрирует более сложные концепции, связанные с агрегатами:

- **Доменные события (Domain Events):** Агрегат генерирует события при изменении своего состояния.
- **Сложные инварианты:** Проверка бизнес-правил, охватывающих несколько объектов внутри агрегата (например, общий вес и объем).
- **Фабричный метод:** Создание агрегата через специальный метод, который гарантирует его корректную инициализацию.
- **Ссылки на другие агрегаты по ID:** Использование идентификаторов для связи с другими агрегатами вместо прямых ссылок на объекты.

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
import uuid
from enum import Enum

# --- 1. Инфраструктура для Доменных Событий (упрощенная) ---

@dataclass(frozen=True)
class DomainEvent:
    """Базовый класс для всех доменных событий."""
    aggregate_id: uuid.UUID

# Простой обработчик/диспетчер событий для демонстрации
event_handlers: Dict[type, List[Callable]] = {}

def register_handler(event_type: type, handler: Callable):
    """Регистрирует обработчик для типа события."""
    if event_type not in event_handlers:
        event_handlers[event_type] = []
    event_handlers[event_type].append(handler)

def dispatch_event(event: DomainEvent):
    """Вызывает всех зарегистрированных обработчиков для данного события."""
    if type(event) in event_handlers:
        for handler in event_handlers[type(event)]:
            handler(event)

# --- 2. Value Objects и Enums ---

@dataclass(frozen=True)
class ShipmentId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class OrderId:
    """Ссылка на агрегат Заказа по ID."""
    value: uuid.UUID

@dataclass(frozen=True)
class Address:
    city: str
    street: str
    zip_code: str

@dataclass(frozen=True)
class Weight:
    value: float # в килограммах

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Вес должен быть положительным.")

@dataclass(frozen=True)
class Volume:
    value: float # в кубических метрах

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Объем должен быть положительным.")

class ShipmentStatus(Enum):
    PREPARING = "PREPARING"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

# --- 3. Доменные События для Агрегата Shipment ---

@dataclass(frozen=True)
class ShipmentCreated(DomainEvent):
    destination: Address
    max_weight: Weight
    max_volume: Volume

@dataclass(frozen=True)
class ParcelAddedToShipment(DomainEvent):
    order_id: OrderId
    weight: Weight
    volume: Volume

@dataclass(frozen=True)
class ShipmentDispatched(DomainEvent):
    dispatch_timestamp: int

@dataclass(frozen=True)
class ShipmentDelivered(DomainEvent):
    delivery_timestamp: int

# --- 4. Сущности и Агрегат ---

@dataclass
class Parcel: # Локальная сущность внутри агрегата
    order_id: OrderId
    weight: Weight
    volume: Volume

    def __hash__(self):
        return hash(self.order_id)

    def __eq__(self, other):
        if not isinstance(other, Parcel):
            return NotImplemented
        return self.order_id == other.order_id

class Shipment:
    """Агрегат "Отправление". Является корнем агрегата."""

    def __init__(self):
        # Конструктор намеренно оставлен простым.
        # Инициализация происходит через фабричный метод.
        self.id: Optional[ShipmentId] = None
        self.destination: Optional[Address] = None
        self.status: Optional[ShipmentStatus] = None
        self._parcels: List[Parcel] = []
        self._events: List[DomainEvent] = []
        self.max_weight: Optional[Weight] = None
        self.max_volume: Optional[Volume] = None
        self.version: int = 0

    @staticmethod
    def create(destination: Address, max_weight: Weight, max_volume: Volume) -> 'Shipment':
        """Фабричный метод для создания нового Отправления."""
        if not isinstance(destination, Address):
            raise TypeError("Некорректный тип адреса.")

        shipment = Shipment()
        shipment.id = ShipmentId()
        shipment.destination = destination
        shipment.status = ShipmentStatus.PREPARING
        shipment.max_weight = max_weight
        shipment.max_volume = max_volume
        shipment.version = 1

        event = ShipmentCreated(
            aggregate_id=shipment.id.value,
            destination=destination,
            max_weight=max_weight,
            max_volume=max_volume
        )
        shipment._add_event(event)
        return shipment

    @property
    def parcels(self) -> List[Parcel]:
        return list(self._parcels)

    @property
    def current_weight(self) -> Weight:
        return Weight(sum(p.weight.value for p in self._parcels)) if self._parcels else Weight(0.001) # hack for positive value

    @property
    def current_volume(self) -> Volume:
        return Volume(sum(p.volume.value for p in self._parcels)) if self._parcels else Volume(0.001)

    def _add_event(self, event: DomainEvent):
        self._events.append(event)

    def pull_domain_events(self) -> List[DomainEvent]:
        """Инфраструктурный метод для извлечения событий перед сохранением."""
        events = list(self._events)
        self._events.clear()
        return events

    def _increment_version(self):
        self.version += 1

    def add_parcel(self, order_id: OrderId, weight: Weight, volume: Volume):
        """Добавление посылки в отправление с проверкой инвариантов."""
        if self.status != ShipmentStatus.PREPARING:
            raise ValueError(f"Нельзя добавлять посылки в отправление со статусом {self.status.value}")

        # Инвариант: не превышать максимальный вес
        if self.current_weight.value + weight.value > self.max_weight.value:
            raise ValueError("Превышен максимальный вес отправления.")

        # Инвариант: не превышать максимальный объем
        if self.current_volume.value + volume.value > self.max_volume.value:
            raise ValueError("Превышен максимальный объем отправления.")

        # Инвариант: одна посылка на один заказ
        if any(p.order_id == order_id for p in self._parcels):
            raise ValueError(f"Посылка для заказа {order_id.value} уже в этом отправлении.")

        parcel = Parcel(order_id=order_id, weight=weight, volume=volume)
        self._parcels.append(parcel)
        self._increment_version()

        event = ParcelAddedToShipment(
            aggregate_id=self.id.value,
            order_id=order_id,
            weight=weight,
            volume=volume
        )
        self._add_event(event)

    def dispatch(self, timestamp: int):
        """Отправка груза."""
        if self.status != ShipmentStatus.PREPARING:
            raise ValueError("Отправить можно только подготовленный груз.")
        if not self._parcels:
            raise ValueError("Нельзя отправить пустой груз.")

        self.status = ShipmentStatus.DISPATCHED
        self._increment_version()
        self._add_event(ShipmentDispatched(aggregate_id=self.id.value, dispatch_timestamp=timestamp))

    def mark_as_delivered(self, timestamp: int):
        if self.status not in [ShipmentStatus.DISPATCHED, ShipmentStatus.IN_TRANSIT]:
            raise ValueError(f"Нельзя отметить доставленным груз в статусе {self.status.value}")

        self.status = ShipmentStatus.DELIVERED
        self._increment_version()
        self._add_event(ShipmentDelivered(aggregate_id=self.id.value, delivery_timestamp=timestamp))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Shipment):
            return NotImplemented
        return self.id == other.id
```
