# Решение упражнения по модулю "Доменные события (Domain Events)"

## Задание: Интеграция Доменных Событий в Агрегат `Order`

Ниже представлен пример реализации Доменных Событий, их интеграции в Агрегат `Order`, а также простой "in-memory" диспетчер событий и обработчик.

### Код решения

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, NewType, Optional, Type, TypeVar, Callable, Dict, Tuple, Any

# --- Вспомогательные типы и классы из предыдущего модуля (Агрегаты) ---

OrderId = NewType("OrderId", uuid.UUID)
OrderItemId = NewType("OrderItemId", uuid.UUID)
CustomerId = NewType("CustomerId", uuid.UUID)
ProductId = NewType("ProductId", uuid.UUID)

_TMoney = TypeVar("_TMoney", bound="Money")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < Decimal(0):
            raise ValueError("Amount cannot be negative.")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code.")

    def __add__(self: _TMoney, other: _TMoney) -> _TMoney:
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValueError("Cannot add Money with different currencies.")
        return self.__class__(self.amount + other.amount, self.currency)

    def __sub__(self: _TMoney, other: _TMoney) -> _TMoney:
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValueError("Cannot subtract Money with different currencies.")
        return self.__class__(self.amount - other.amount, self.currency)

    def __mul__(self: _TMoney, multiplier: int | Decimal) -> _TMoney:
        if not isinstance(multiplier, (int, Decimal)) or multiplier < 0:
            raise ValueError("Multiplier must be a non-negative number.")
        return self.__class__(self.amount * Decimal(multiplier), self.currency)

    @classmethod
    def zero(cls: Type[_TMoney], currency: str = "USD") -> _TMoney:
        return cls(Decimal(0), currency)


@dataclass(frozen=True)
class ShippingAddress:
    street: str
    city: str
    postal_code: str
    country: str

    def __post_init__(self):
        if not all([self.street, self.city, self.postal_code, self.country]):
            raise ValueError("All address fields must be provided.")


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    order_item_id: OrderItemId
    product_id: ProductId
    quantity: int
    price_per_unit: Money

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive.")

    def calculate_item_total(self) -> Money:
        return self.price_per_unit * self.quantity

    def _update_quantity(self, new_quantity: int) -> None:
        if new_quantity <= 0:
            raise ValueError("New quantity must be positive.")
        self.quantity = new_quantity

# --- Реализация Доменных Событий ---

@dataclass(frozen=True)
class DomainEvent:
    """Базовый класс для всех доменных событий."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    order_id: OrderId
    customer_id: CustomerId
    shipping_address: ShippingAddress
    order_created_at: datetime # Время создания самого заказа


@dataclass(frozen=True)
class OrderItemAddedEvent(DomainEvent):
    order_id: OrderId
    order_item_id: OrderItemId
    product_id: ProductId
    quantity: int
    price_per_unit: Money


@dataclass(frozen=True)
class OrderStatusChangedEvent(DomainEvent):
    order_id: OrderId
    old_status: OrderStatus
    new_status: OrderStatus


@dataclass(frozen=True)
class OrderTotalAmountRecalculatedEvent(DomainEvent): # Опциональное событие
    order_id: OrderId
    new_total_amount: Money


# --- Модифицированный Агрегат Order ---

class Order:
    order_id: OrderId
    customer_id: CustomerId
    _order_items: List[OrderItem]
    shipping_address: ShippingAddress
    status: OrderStatus
    created_at: datetime
    _updated_at: datetime
    _domain_events: List[DomainEvent] # Список для хранения событий

    def __init__(
        self,
        order_id: OrderId,
        customer_id: CustomerId,
        shipping_address: ShippingAddress,
        created_at: Optional[datetime] = None,
    ):
        self.order_id = order_id
        self.customer_id = customer_id
        self._order_items = []
        self.shipping_address = shipping_address
        self.status = OrderStatus.PENDING
        self.created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = self.created_at
        self._domain_events = [] # Инициализация списка событий

        # Генерируем событие создания заказа
        self._add_event(
            OrderCreatedEvent(
                order_id=self.order_id,
                customer_id=self.customer_id,
                shipping_address=self.shipping_address,
                order_created_at=self.created_at
            )
        )
        self._add_event( # Также генерируем событие пересчета суммы (изначально 0)
            OrderTotalAmountRecalculatedEvent(
                order_id=self.order_id,
                new_total_amount=self.total_amount # Будет 0 на момент создания
            )
        )


    def _add_event(self, event: DomainEvent) -> None:
        """Добавляет событие в список."""
        self._domain_events.append(event)

    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Возвращает список несохраненных событий."""
        return list(self._domain_events) # Возвращаем копию

    def clear_uncommitted_events(self) -> None:
        """Очищает список несохраненных событий."""
        self._domain_events.clear()

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def order_items(self) -> Tuple[OrderItem, ...]:
        return tuple(self._order_items)

    @property
    def total_amount(self) -> Money:
        if not self._order_items:
            default_currency = "USD" # Или берем из конфигурации/агрегата
            return Money.zero(default_currency)
        currency = self._order_items[0].price_per_unit.currency
        total = Money.zero(currency)
        for item in self._order_items:
            total += item.calculate_item_total()
        return total

    def _mark_updated(self) -> None:
        self._updated_at = datetime.now(timezone.utc)

    def _recalculate_total_and_notify(self) -> None:
        """Внутренний метод для пересчета суммы и генерации события."""
        self._mark_updated()
        self._add_event(
            OrderTotalAmountRecalculatedEvent(
                order_id=self.order_id,
                new_total_amount=self.total_amount
            )
        )

    def add_item(
        self,
        product_id: ProductId,
        quantity: int,
        price_per_unit: Money,
        order_item_id_val: Optional[OrderItemId] = None
    ) -> OrderItemId:
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot add item to order in status {self.status.value}")
        # ... (остальные проверки как в предыдущей версии)

        new_item_id = order_item_id_val or OrderItemId(uuid.uuid4())
        item = OrderItem(
            order_item_id=new_item_id,
            product_id=product_id,
            quantity=quantity,
            price_per_unit=price_per_unit,
        )
        self._order_items.append(item)

        self._add_event(
            OrderItemAddedEvent(
                order_id=self.order_id,
                order_item_id=item.order_item_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=item.price_per_unit
            )
        )
        self._recalculate_total_and_notify()
        return new_item_id

    def remove_item(self, order_item_id: OrderItemId) -> None:
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot remove item from order in status {self.status.value}")
        # ... (логика удаления)
        item_to_remove = next((item for item in self._order_items if item.order_item_id == order_item_id), None)
        if not item_to_remove:
            raise ValueError(f"OrderItem with id {order_item_id} not found in order.")
        self._order_items.remove(item_to_remove)
        self._recalculate_total_and_notify()


    def update_item_quantity(self, order_item_id: OrderItemId, new_quantity: int) -> None:
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Cannot update item quantity in order with status {self.status.value}")
        # ... (логика обновления)
        item_to_update = next((item for item in self._order_items if item.order_item_id == order_item_id), None)
        if not item_to_update:
            raise ValueError(f"OrderItem with id {order_item_id} not found in order.")
        item_to_update._update_quantity(new_quantity)
        self._recalculate_total_and_notify()


    def _change_status(self, new_status: OrderStatus) -> None:
        """Внутренний метод для смены статуса и генерации события."""
        old_status = self.status
        self.status = new_status
        self._mark_updated()
        self._add_event(
            OrderStatusChangedEvent(
                order_id=self.order_id,
                old_status=old_status,
                new_status=self.status
            )
        )

    def pay(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Order can only be paid if status is PENDING. Current status: {self.status.value}")
        if not self._order_items:
            raise ValueError("Cannot pay for an empty order.")
        self._change_status(OrderStatus.PAID)

    def ship(self) -> None:
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Order can only be shipped if status is PAID. Current status: {self.status.value}")
        self._change_status(OrderStatus.SHIPPED)

    def deliver(self) -> None:
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"Order can only be delivered if status is SHIPPED. Current status: {self.status.value}")
        self._change_status(OrderStatus.DELIVERED)

    def cancel(self) -> None:
        if self.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]: # Нельзя отменить доставленный или уже отмененный
            raise ValueError(f"Order cannot be cancelled if status is {self.status.value}")
        self._change_status(OrderStatus.CANCELLED)

    def change_shipping_address(self, new_address: ShippingAddress) -> None:
        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            raise ValueError(f"Cannot change shipping address for order in status {self.status.value}")
        self.shipping_address = new_address
        self._mark_updated()
        # Можно добавить событие ShippingAddressChangedEvent, если это важно для домена

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __repr__(self) -> str:
        return (f"<Order id={self.order_id} status='{self.status.value}' "
                f"items={len(self._order_items)} total={self.total_amount} "
                f"events_count={len(self._domain_events)}>"
               )


# --- (Опционально) Простой Диспетчер и Обработчик Событий ---

# Тип для обработчика событий
EventHandler = Callable[[DomainEvent], None]

class InMemoryEventDispatcher:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def register(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Регистрирует обработчик для указанного типа события."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch(self, event: DomainEvent) -> None:
        """Диспетчеризует событие всем зарегистрированным обработчикам этого типа."""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # В реальной системе здесь должна быть более сложная обработка ошибок
                    print(f"Error handling event {event_type.__name__} by {handler.__name__}: {e}")
        # Можно добавить логику для обработки событий родительских классов, если необходимо

# Пример обработчика
def logging_event_handler(event: DomainEvent) -> None:
    """Простой обработчик, который логирует информацию о событии."""
    print(f"[EVENT LOG] Time: {event.occurred_on.isoformat()}, Type: {type(event).__name__}, ID: {event.event_id}")
    if isinstance(event, OrderCreatedEvent):
        print(f"  Order Created: ID={event.order_id}, Customer={event.customer_id}, Address='{event.shipping_address.city}'")
    elif isinstance(event, OrderItemAddedEvent):
        print(f"  Item Added to Order {event.order_id}: ItemID={event.order_item_id}, Product={event.product_id}, Qty={event.quantity}")
    elif isinstance(event, OrderStatusChangedEvent):
        print(f"  Order Status Changed for {event.order_id}: {event.old_status.value} -> {event.new_status.value}")
    elif isinstance(event, OrderTotalAmountRecalculatedEvent):
        print(f"  Order Total Recalculated for {event.order_id}: New Total={event.new_total_amount.amount} {event.new_total_amount.currency}")


# --- Примеры использования ---
if __name__ == "__main__":
    # 1. Настройка Диспетчера и Обработчиков
    dispatcher = InMemoryEventDispatcher()
    dispatcher.register(OrderCreatedEvent, logging_event_handler)
    dispatcher.register(OrderItemAddedEvent, logging_event_handler)
    dispatcher.register(OrderStatusChangedEvent, logging_event_handler)
    dispatcher.register(OrderTotalAmountRecalculatedEvent, logging_event_handler)

    # Функция для публикации событий
    def publish_events(order_instance: Order, event_dispatcher: InMemoryEventDispatcher) -> None:
        events = order_instance.get_uncommitted_events()
        print(f"\nPublishing {len(events)} events for Order ID {order_instance.order_id}:")
        for e in events:
            event_dispatcher.dispatch(e)
        order_instance.clear_uncommitted_events()
        print(f"Events cleared from order. Remaining events in order: {len(order_instance.get_uncommitted_events())}")


    # 2. Работа с Агрегатом Order
    print("--- Scenario 1: Creating Order and Adding Items ---")
    customer1_id = CustomerId(uuid.uuid4())
    product1_id = ProductId(uuid.uuid4())
    addr = ShippingAddress(street="123 Main St", city="Anytown", postal_code="12345", country="USA")

    # Создание заказа (генерирует OrderCreatedEvent и OrderTotalAmountRecalculatedEvent)
    order1 = Order(OrderId(uuid.uuid4()), customer1_id, addr)
    print(f"Initial Order state: {order1}")
    publish_events(order1, dispatcher) # Публикуем события после создания

    # Добавление позиции (генерирует OrderItemAddedEvent и OrderTotalAmountRecalculatedEvent)
    price_p1 = Money(Decimal("19.99"))
    try:
        item1_id = order1.add_item(product1_id, 2, price_p1)
        print(f"\nAfter adding item: {order1}")
        publish_events(order1, dispatcher) # Публикуем события после добавления
    except ValueError as e:
        print(f"Error: {e}")


    print("\n\n--- Scenario 2: Changing Order Status ---")
    order2 = Order(OrderId(uuid.uuid4()), CustomerId(uuid.uuid4()), addr)
    publish_events(order2, dispatcher) # События создания

    order2.add_item(ProductId(uuid.uuid4()), 1, Money(Decimal("10.00")))
    publish_events(order2, dispatcher) # События добавления

    try:
        # Оплата заказа (генерирует OrderStatusChangedEvent)
        order2.pay()
        print(f"\nAfter payment: {order2}")
        publish_events(order2, dispatcher)

        # Отправка заказа (генерирует OrderStatusChangedEvent)
        order2.ship()
        print(f"\nAfter shipping: {order2}")
        publish_events(order2, dispatcher)
    except ValueError as e:
        print(f"Error: {e}")

    print(f"\nFinal state of order1: {order1}")
    print(f"Final state of order2: {order2}")
