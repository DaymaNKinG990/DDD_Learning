"""
Примеры кода для модуля "Доменные события (Domain Events)".

Демонстрирует создание, генерацию и обработку доменных событий.
Включает базовый класс события, конкретные события,
интеграцию с агрегатом (упрощенный Заказ)
и простой механизм диспетчеризации событий.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Type, TypeVar


# 1. Определение базового Доменного События
class DomainEvent:
    """Базовый класс для всех доменных событий."""

    event_id: uuid.UUID
    occurred_on: datetime

    def __init__(self):
        self.event_id = uuid.uuid4()
        self.occurred_on = datetime.utcnow()


# 2. Конкретные Доменные События
@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """Событие: Пользователь зарегистрирован."""

    user_id: uuid.UUID
    email: str

    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class OrderIdValueObject:  # Используем простой VO для ID заказа
    value: uuid.UUID


@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """Событие: Заказ создан."""

    order_id: OrderIdValueObject
    customer_id: uuid.UUID
    total_amount: float

    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class OrderPaid(DomainEvent):
    """Событие: Заказ оплачен."""

    order_id: OrderIdValueObject
    payment_reference: str

    def __post_init__(self):
        super().__init__()


# 3. Агрегат, генерирующий события (упрощенный)
class OrderStatus:
    PENDING = "PENDING"
    PAID = "PAID"


@dataclass
class Order:
    """Упрощенный агрегат Заказа, способный генерировать доменные события."""

    id: OrderIdValueObject
    customer_id: uuid.UUID
    items: Dict[str, int]  # {product_name: quantity}
    total_amount: float
    status: str = OrderStatus.PENDING
    _domain_events: List[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    @classmethod
    def create(
        cls, customer_id: uuid.UUID, items: Dict[str, int], total_amount: float
    ) -> "Order":
        order_id = OrderIdValueObject(value=uuid.uuid4())
        order = cls(
            id=order_id, customer_id=customer_id, items=items, total_amount=total_amount
        )
        order._add_domain_event(
            OrderCreated(
                order_id=order.id,
                customer_id=order.customer_id,
                total_amount=order.total_amount,
            )
        )
        return order

    def _add_domain_event(self, event: DomainEvent):
        self._domain_events.append(event)

    def pull_domain_events(self) -> List[DomainEvent]:
        """Извлекает события и очищает список.

        Важно для гарантии однократной обработки.
        """
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def pay(self, payment_reference: str):
        if self.status == OrderStatus.PAID:
            raise ValueError("Заказ уже оплачен.")
        self.status = OrderStatus.PAID
        self._add_domain_event(
            OrderPaid(order_id=self.id, payment_reference=payment_reference)
        )
        print(f"Заказ {self.id.value} оплачен (ref: {payment_reference}).")


# 4. Диспетчер Доменных Событий и Обработчики

# Тип для обработчика события
EventHandler = Callable[[DomainEvent], None]


# 4. Диспетчер Доменных Событий и Обработчики

# Определяем TypeVar для обобщенного типа события.
# Это позволяет нам создавать функции, которые работают с подтипами DomainEvent.
T_Event = TypeVar("T_Event", bound=DomainEvent)


class DomainEventDispatcher:
    """Простой диспетчер доменных событий."""

    def __init__(self) -> None:
        """Инициализирует диспетчер, добавляя аннотацию типа для mypy."""
        self._handlers: Dict[
            Type[DomainEvent], List[Callable[[DomainEvent], None]]
        ] = {}

    def register(
        self, event_type: Type[T_Event], handler: Callable[[T_Event], None]
    ) -> None:
        """
        Регистрирует обработчик для указанного типа события.
        Использует TypeVar T_Event, чтобы mypy понял, что обработчик
        для UserRegistered является валидным.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        # Mypy будет жаловаться на следующую строку из-за сложной логики типов.
        # Мы знаем, что это безопасно, так как dispatch вызывает обработчик
        # только для соответствующего типа события, поэтому игнорируем ошибку.
        self._handlers[event_type].append(handler)  # type: ignore[arg-type]
        print(
            f"Обработчик {handler.__name__} зарегистрирован "
            f"для события {event_type.__name__}."
        )

    def dispatch(self, event: DomainEvent) -> None:
        """Отправляет событие всем зарегистрированным обработчикам."""
        event_type = type(event)
        if event_type in self._handlers:
            print(f"\nДиспетчеризация события: {event}")
            for handler in self._handlers[event_type]:
                try:
                    print(f"  Вызов обработчика: {handler.__name__}...")
                    # Вызов здесь безопасен, так как мы получаем обработчики
                    handler(event)
                except Exception as e:
                    print(f"  Ошибка в обработчике {handler.__name__}: {e}")
        else:
            print(f"\nНет обработчиков для события: {event_type.__name__}")

    def dispatch_batch(self, events: List[DomainEvent]) -> None:
        """Отправляет список событий."""
        for event in events:
            self.dispatch(event)


# Пример обработчиков
class EmailService:
    """Заглушка для сервиса отправки email."""

    def send_welcome_email(self, email: str, user_id: uuid.UUID):
        print(f"    [EmailService] Welcome email to {email} for user {user_id}.")

    def send_order_confirmation_email(
        self, customer_id: uuid.UUID, order_id: OrderIdValueObject, amount: float
    ):
        print(
            f"    [EmailService] Order confirmation for {order_id.value} "
            f"to {customer_id} for {amount:.2f}."
        )

    def send_payment_receipt_email(
        self, customer_id: uuid.UUID, order_id: OrderIdValueObject, payment_ref: str
    ):
        # В реальном приложении мы бы получили email клиента по customer_id
        print(
            f"    [EmailService] Payment receipt for order {order_id.value} "
            f"(ref: {payment_ref}) to {customer_id}."
        )


class AnalyticsService:
    """Заглушка для сервиса аналитики."""

    def track_user_registration(self, user_id: uuid.UUID, occurred_on: datetime):
        print(f"    [AnalyticsService] New user {user_id} registered at {occurred_on}.")

    def track_order_creation(
        self, order_id: OrderIdValueObject, amount: float, occurred_on: datetime
    ):
        print(
            f"    [AnalyticsService] New order {order_id.value} for {amount:.2f} "
            f"at {occurred_on}."
        )


# Глобальные экземпляры сервисов-заглушек для простоты примера
email_service = EmailService()
analytics_service = AnalyticsService()


def handle_user_registered_email(event: UserRegistered) -> None:
    if not isinstance(event, UserRegistered):
        return  # Дополнительная проверка типа, хотя диспетчер должен это делать
    email_service.send_welcome_email(event.email, event.user_id)


def handle_user_registered_analytics(event: UserRegistered) -> None:
    if not isinstance(event, UserRegistered):
        return
    analytics_service.track_user_registration(event.user_id, event.occurred_on)


def handle_order_created_email(event: OrderCreated) -> None:
    if not isinstance(event, OrderCreated):
        return
    # В реальном приложении мы бы получили email клиента по event.customer_id
    email_service.send_order_confirmation_email(
        event.customer_id, event.order_id, event.total_amount
    )


def handle_order_created_analytics(event: OrderCreated) -> None:
    if not isinstance(event, OrderCreated):
        return
    analytics_service.track_order_creation(
        event.order_id, event.total_amount, event.occurred_on
    )


def handle_order_paid_email_receipt(event: OrderPaid) -> None:
    if not isinstance(event, OrderPaid):
        return
    # Нужен способ получить customer_id из OrderPaid или через order_id
    # Для примера предположим, что мы можем его получить (например, из репозитория)
    print(
        f"    (Предполагаем, что customer_id для заказа {event.order_id.value} найден)"
    )
    customer_id_placeholder = uuid.uuid4()  # Заглушка
    email_service.send_payment_receipt_email(
        customer_id_placeholder, event.order_id, event.payment_reference
    )


if __name__ == "__main__":
    print("--- Демонстрация Доменных Событий ---")

    # 1. Инициализация диспетчера и регистрация обработчиков
    dispatcher = DomainEventDispatcher()
    dispatcher.register(UserRegistered, handle_user_registered_email)
    dispatcher.register(UserRegistered, handle_user_registered_analytics)
    dispatcher.register(OrderCreated, handle_order_created_email)
    dispatcher.register(OrderCreated, handle_order_created_analytics)
    dispatcher.register(OrderPaid, handle_order_paid_email_receipt)

    # 2. Симуляция регистрации пользователя
    print("\n--- Регистрация пользователя ---")
    user_id_new = uuid.uuid4()
    user_registered_event = UserRegistered(
        user_id=user_id_new, email="new.user@example.com"
    )
    dispatcher.dispatch(user_registered_event)

    # 3. Симуляция создания и обработки заказа
    print("\n--- Создание и обработка Заказа ---")
    customer1_id = uuid.uuid4()
    order1_items = {"Ноутбук 'Прогресс'": 1, "Мышь 'Точность'": 2}
    order1_amount = 85000.00

    # Создание заказа (генерирует OrderCreated внутри)
    order1 = Order.create(
        customer_id=customer1_id, items=order1_items, total_amount=order1_amount
    )
    print(f"Создан заказ: {order1.id.value}, Статус: {order1.status}")

    # Извлечение и диспетчеризация событий из заказа
    order1_events = order1.pull_domain_events()
    dispatcher.dispatch_batch(order1_events)

    # Оплата заказа (генерирует OrderPaid внутри)
    print("\n--- Оплата Заказа ---")
    try:
        order1.pay("PAY_REF_12345")
        order1_payment_events = order1.pull_domain_events()
        dispatcher.dispatch_batch(order1_payment_events)
    except ValueError as e:
        print(f"Ошибка оплаты: {e}")

    # Попытка повторной оплаты
    print("\n--- Попытка повторной оплаты Заказа ---")
    try:
        order1.pay("PAY_REF_67890")
    except ValueError as e:
        print(f"Ошибка повторной оплаты: {e}")

    print("\n--- Демонстрация завершена ---")
