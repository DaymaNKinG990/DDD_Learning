# Решение упражнения по модулю "Сервисы приложения (Application Services)"

## Введение

В этом решении мы реализуем `OrderApplicationService`, который будет управлять Агрегатом `Order`. Мы определим необходимые Объекты Передачи Данных (DTO), Команды, а также вспомогательные классы, такие как идентификаторы, доменные объекты (`Money`, `ShippingAddress`, `OrderStatus`, `Order`, `OrderItem`) и реализацию `OrderRepository` (используем `InMemoryOrderRepository` из предыдущих модулей для простоты).

## Часть 1: Определение идентификаторов и базовых доменных объектов

Сначала определим базовые типы и классы, которые будут использоваться в нашем решении. Многие из них уже могли быть определены в предыдущих модулях.

```python
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, NewType, Set
import copy

# --- Идентификаторы --- (Предполагается, что они уже определены)
OrderId = NewType("OrderId", uuid.UUID)
OrderItemId = NewType("OrderItemId", uuid.UUID)
CustomerId = NewType("CustomerId", uuid.UUID)
ProductId = NewType("ProductId", uuid.UUID)

# --- Вспомогательные доменные объекты --- (Предполагается, что они уже определены)

@dataclass(frozen=True)
class Money:
    """Объект-значение для представления денежной суммы."""
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < Decimal(0):
            raise ValueError("Сумма не может быть отрицательной.")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов (например, USD, RUB).")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Нельзя складывать деньги в разных валютах.")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int) -> "Money":
        if factor < 0:
            raise ValueError("Множитель не может быть отрицательным.")
        return Money(self.amount * Decimal(factor), self.currency)

@dataclass(frozen=True)
class ShippingAddress:
    """Объект-значение для адреса доставки."""
    street: str
    city: str
    postal_code: str
    country: str

class OrderStatus(Enum):
    """Статус заказа."""
    PENDING = "PENDING"  # Ожидание
    PAID = "PAID"        # Оплачен
    SHIPPED = "SHIPPED"    # Отправлен
    DELIVERED = "DELIVERED"  # Доставлен
    CANCELLED = "CANCELLED"  # Отменен

# --- Доменные события (если используются) ---
@dataclass(frozen=True)
class DomainEvent:
    """Базовый класс для доменных событий."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    order_id: OrderId
    customer_id: CustomerId
    total_amount: Money

@dataclass(frozen=True)
class OrderItemAddedEvent(DomainEvent):
    order_id: OrderId
    order_item_id: OrderItemId
    product_id: ProductId

@dataclass(frozen=True)
class OrderStatusChangedEvent(DomainEvent):
    order_id: OrderId
    old_status: OrderStatus
    new_status: OrderStatus

# --- Агрегат OrderItem (вложенная Сущность) ---
@dataclass
class OrderItem:
    """Элемент заказа (позиция в заказе)."""
    id: OrderItemId
    product_id: ProductId
    quantity: int
    price_per_unit: Money

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Количество товара должно быть положительным.")

    @property
    def item_total(self) -> Money:
        """Общая стоимость данной позиции заказа."""
        return self.price_per_unit * self.quantity

# --- Агрегат Order ---
@dataclass
class Order:
    """Агрегат Заказ."""
    id: OrderId
    customer_id: CustomerId
    status: OrderStatus
    shipping_address: ShippingAddress
    items: List[OrderItem]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _domain_events: List[DomainEvent] = field(default_factory=list, repr=False)

    def __post_init__(self):
        if not self.items:
            raise ValueError("Заказ должен содержать хотя бы одну позицию.")
        self.updated_at = self.created_at

    @property
    def total_amount(self) -> Money:
        """Общая сумма заказа."""
        if not self.items:
            return Money(Decimal(0), "USD") # Пример валюты по умолчанию

        # Предполагаем, что все товары в одной валюте или конвертация уже произошла
        # Для простоты берем валюту первого товара
        currency = self.items[0].price_per_unit.currency
        total = Money(Decimal(0), currency)
        for item in self.items:
            if item.price_per_unit.currency != currency:
                # В реальном приложении здесь нужна логика конвертации или ошибка
                raise ValueError("Все товары в заказе должны быть в одной валюте или должна быть реализована конвертация.")
            total += item.item_total
        return total

    def add_item(self, product_id: ProductId, quantity: int, price_per_unit: Money) -> OrderItemId:
        """Добавляет новую позицию в заказ."""
        # Проверка, можно ли добавлять товары в заказ с текущим статусом
        if self.status not in [OrderStatus.PENDING]:
            raise ValueError(f"Нельзя добавлять товары в заказ со статусом {self.status.value}")

        new_item_id = OrderItemId(uuid.uuid4())
        new_item = OrderItem(
            id=new_item_id,
            product_id=product_id,
            quantity=quantity,
            price_per_unit=price_per_unit
        )
        self.items.append(new_item)
        self.updated_at = datetime.utcnow()
        self._add_event(OrderItemAddedEvent(order_id=self.id, order_item_id=new_item_id, product_id=product_id))
        return new_item_id

    def _can_change_status(self, new_status: OrderStatus) -> bool:
        """Проверяет допустимость смены статуса."""
        # Упрощенная логика переходов
        if self.status == OrderStatus.PENDING and new_status in [OrderStatus.PAID, OrderStatus.CANCELLED]:
            return True
        if self.status == OrderStatus.PAID and new_status in [OrderStatus.SHIPPED, OrderStatus.CANCELLED]:
            return True
        if self.status == OrderStatus.SHIPPED and new_status == OrderStatus.DELIVERED:
            return True
        return False

    def change_status(self, new_status: OrderStatus):
        """Изменяет статус заказа."""
        if not self._can_change_status(new_status):
            raise ValueError(f"Нельзя изменить статус с {self.status.value} на {new_status.value}")

        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        self._add_event(OrderStatusChangedEvent(order_id=self.id, old_status=old_status, new_status=new_status))

    def pay(self):
        self.change_status(OrderStatus.PAID)

    def ship(self):
        self.change_status(OrderStatus.SHIPPED)

    def deliver(self):
        self.change_status(OrderStatus.DELIVERED)

    def cancel(self):
        self.change_status(OrderStatus.CANCELLED)

    def _add_event(self, event: DomainEvent):
        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events[:]

    def clear_domain_events(self):
        self._domain_events.clear()

    @classmethod
    def create(cls, customer_id: CustomerId, shipping_address: ShippingAddress, items_data: List[Dict[str, any]]) -> "Order":
        """Фабричный метод для создания нового заказа."""
        order_id = OrderId(uuid.uuid4())
        order_items = []
        for item_data in items_data:
            order_items.append(
                OrderItem(
                    id=OrderItemId(uuid.uuid4()),
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"],
                    price_per_unit=item_data["price_per_unit"]
                )
            )

        order = cls(
            id=order_id,
            customer_id=customer_id,
            status=OrderStatus.PENDING,
            shipping_address=shipping_address,
            items=order_items,
            created_at=datetime.utcnow()
        )
        order._add_event(OrderCreatedEvent(order_id=order.id, customer_id=order.customer_id, total_amount=order.total_amount))
        return order

# --- Интерфейс репозитория и его In-Memory реализация --- (Из предыдущего модуля)

class OrderRepositoryError(Exception):
    """Базовое исключение для ошибок репозитория заказов."""
    pass

class OrderNotFoundError(OrderRepositoryError):
    """Заказ не найден."""
    def __init__(self, order_id: OrderId):
        super().__init__(f"Заказ с ID {order_id} не найден.")

class OrderAlreadyExistsError(OrderRepositoryError):
    """Заказ с таким ID уже существует."""
    def __init__(self, order_id: OrderId):
        super().__init__(f"Заказ с ID {order_id} уже существует.")

class IOrderRepository:
    """Интерфейс репозитория для агрегата Order."""
    def add(self, order: Order) -> None:
        raise NotImplementedError

    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        raise NotImplementedError

    def save(self, order: Order) -> None:
        raise NotImplementedError

    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        raise NotImplementedError

    def delete(self, order_id: OrderId) -> None:
        raise NotImplementedError

class InMemoryOrderRepository(IOrderRepository):
    """In-memory реализация репозитория заказов."""
    def __init__(self):
        self._orders: Dict[OrderId, Order] = {}

    def add(self, order: Order) -> None:
        if order.id in self._orders:
            raise OrderAlreadyExistsError(order.id)
        # Сохраняем глубокую копию, чтобы избежать модификации объекта вне репозитория
        self._orders[order.id] = copy.deepcopy(order)

    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        order = self._orders.get(order_id)
        # Возвращаем глубокую копию, чтобы избежать модификации объекта вне репозитория
        return copy.deepcopy(order) if order else None

    def save(self, order: Order) -> None:
        if order.id not in self._orders:
            raise OrderNotFoundError(order.id)
        # Обновляем глубокой копией
        self._orders[order.id] = copy.deepcopy(order)

    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        # Возвращаем глубокие копии
        return [
            copy.deepcopy(order)
            for order in self._orders.values()
            if order.customer_id == customer_id
        ]

    def delete(self, order_id: OrderId) -> None:
        if order_id not in self._orders:
            raise OrderNotFoundError(order_id)
        del self._orders[order_id]

```

## Часть 2: Определение DTO и Команд

Теперь определим DTO (Data Transfer Objects) и Команды, которые будут использоваться Сервисом Приложения.

```python
# --- DTO и Команды ---

@dataclass(frozen=True)
class MoneyDTO:
    amount: str  # Используем str для Decimal для сериализации/десериализации
    currency: str

@dataclass(frozen=True)
class ShippingAddressDTO:
    street: str
    city: str
    postal_code: str
    country: str

@dataclass(frozen=True)
class OrderItemCommandDTO: # Для создания/добавления элемента заказа
    product_id: str # UUID в виде строки
    quantity: int
    price_per_unit_amount: str # Decimal в виде строки
    price_per_unit_currency: str

@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str # UUID в виде строки
    shipping_address: ShippingAddressDTO
    items: List[OrderItemCommandDTO]

@dataclass(frozen=True)
class AddItemToOrderCommand:
    order_id: str # UUID в виде строки
    product_id: str # UUID в виде строки
    quantity: int
    price_per_unit_amount: str # Decimal в виде строки
    price_per_unit_currency: str

@dataclass(frozen=True)
class ChangeOrderStatusCommand:
    order_id: str # UUID в виде строки
    new_status: str # Например, "PAID", "SHIPPED"

# DTO для чтения
@dataclass(frozen=True)
class OrderItemDTO:
    order_item_id: str # UUID в виде строки
    product_id: str # UUID в виде строки
    quantity: int
    price_per_unit: MoneyDTO
    item_total: MoneyDTO

@dataclass(frozen=True)
class OrderDTO:
    order_id: str # UUID в виде строки
    customer_id: str # UUID в виде строки
    status: str
    shipping_address: ShippingAddressDTO
    items: List[OrderItemDTO]
    total_amount: MoneyDTO
    created_at: str # ISO формат datetime
    updated_at: str # ISO формат datetime

```

## Часть 3: Вспомогательные функции / Мапперы

Создадим функции для преобразования между доменными объектами и DTO.

```python
# --- Мапперы ---

def to_money_dto(money: Money) -> MoneyDTO:
    return MoneyDTO(amount=str(money.amount), currency=money.currency)

def from_money_dto(dto: MoneyDTO) -> Money:
    return Money(amount=Decimal(dto.amount), currency=dto.currency)

def to_shipping_address_dto(address: ShippingAddress) -> ShippingAddressDTO:
    return ShippingAddressDTO(
        street=address.street,
        city=address.city,
        postal_code=address.postal_code,
        country=address.country
    )

def from_shipping_address_dto(dto: ShippingAddressDTO) -> ShippingAddress:
    return ShippingAddress(
        street=dto.street,
        city=dto.city,
        postal_code=dto.postal_code,
        country=dto.country
    )

def to_order_item_dto(item: OrderItem) -> OrderItemDTO:
    return OrderItemDTO(
        order_item_id=str(item.id),
        product_id=str(item.product_id),
        quantity=item.quantity,
        price_per_unit=to_money_dto(item.price_per_unit),
        item_total=to_money_dto(item.item_total)
    )

def to_order_dto(order: Order) -> OrderDTO:
    return OrderDTO(
        order_id=str(order.id),
        customer_id=str(order.customer_id),
        status=order.status.value,
        shipping_address=to_shipping_address_dto(order.shipping_address),
        items=[to_order_item_dto(item) for item in order.items],
        total_amount=to_money_dto(order.total_amount),
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat()
    )

# (Опционально) Маппер для OrderItemCommandDTO в словарь для Order.create
def map_item_command_to_domain_data(item_cmd_dto: OrderItemCommandDTO) -> Dict[str, any]:
    return {
        "product_id": ProductId(uuid.UUID(item_cmd_dto.product_id)),
        "quantity": item_cmd_dto.quantity,
        "price_per_unit": Money(
            amount=Decimal(item_cmd_dto.price_per_unit_amount),
            currency=item_cmd_dto.price_per_unit_currency
        )
    }

```

## Часть 4: Реализация `OrderApplicationService`

Теперь реализуем сам сервис приложения.

```python
# --- Сервис Приложения ---

class ApplicationServiceError(Exception):
    """Базовое исключение для ошибок сервиса приложения."""
    pass

class OrderApplicationServiceError(ApplicationServiceError):
    """Ошибка, специфичная для OrderApplicationService."""
    pass

class OrderNotFoundInAppServiceError(OrderApplicationServiceError):
    def __init__(self, order_id: str):
        super().__init__(f"Заказ с ID {order_id} не найден в сервисе приложения.")

class InvalidOrderStatusInAppServiceError(OrderApplicationServiceError):
    def __init__(self, status_value: str):
        super().__init__(f"Недопустимое значение статуса заказа: {status_value}")

class OrderApplicationService:
    """Сервис приложения для управления заказами."""

    def __init__(self, order_repository: IOrderRepository):
        self._order_repository = order_repository
        # В реальном приложении здесь мог бы быть EventPublisher
        # self._event_publisher = event_publisher

    def create_order(self, command: CreateOrderCommand) -> OrderDTO:
        """Создает новый заказ."""
        try:
            customer_id = CustomerId(uuid.UUID(command.customer_id))
            shipping_address = from_shipping_address_dto(command.shipping_address)

            items_data_for_domain = [
                map_item_command_to_domain_data(item_cmd)
                for item_cmd in command.items
            ]

            if not items_data_for_domain:
                 raise OrderApplicationServiceError("Заказ должен содержать хотя бы одну позицию.")

            # Используем фабричный метод Агрегата Order
            new_order = Order.create(
                customer_id=customer_id,
                shipping_address=shipping_address,
                items_data=items_data_for_domain
            )

            self._order_repository.add(new_order)
            # Здесь могла бы быть публикация доменных событий new_order.get_domain_events()
            # new_order.clear_domain_events()

            return to_order_dto(new_order)
        except ValueError as e: # Ошибки валидации из доменных объектов или UUID
            raise OrderApplicationServiceError(f"Ошибка при создании заказа: {e}")
        except OrderAlreadyExistsError as e:
            # Можно логировать или перевыбросить как есть, или специфичное для сервиса
            raise OrderApplicationServiceError(f"Ошибка репозитория: {e}")
        except Exception as e:
            # Общая обработка непредвиденных ошибок
            # Логирование!
            raise OrderApplicationServiceError(f"Непредвиденная ошибка при создании заказа: {e}")

    def get_order_details(self, order_id_str: str) -> Optional[OrderDTO]:
        """Получает детали заказа по ID."""
        try:
            order_id = OrderId(uuid.UUID(order_id_str))
            order = self._order_repository.get_by_id(order_id)
            if order:
                return to_order_dto(order)
            return None
        except ValueError: # Некорректный UUID
            return None # Или выбросить ошибку, если ID должен быть всегда валидным
        except Exception as e:
            raise OrderApplicationServiceError(f"Непредвиденная ошибка при получении заказа: {e}")

    def add_item_to_order(self, command: AddItemToOrderCommand) -> OrderDTO:
        """Добавляет позицию в существующий заказ."""
        try:
            order_id = OrderId(uuid.UUID(command.order_id))
            order = self._order_repository.get_by_id(order_id)

            if not order:
                raise OrderNotFoundInAppServiceError(command.order_id)

            product_id = ProductId(uuid.UUID(command.product_id))
            price_per_unit = Money(
                amount=Decimal(command.price_per_unit_amount),
                currency=command.price_per_unit_currency
            )

            order.add_item(
                product_id=product_id,
                quantity=command.quantity,
                price_per_unit=price_per_unit
            )

            self._order_repository.save(order)
            # Публикация событий order.get_domain_events()
            # order.clear_domain_events()

            return to_order_dto(order)
        except (OrderNotFoundError, ValueError) as e: # Ошибки из репозитория или домена
            raise OrderApplicationServiceError(f"Ошибка при добавлении товара в заказ: {e}")
        except Exception as e:
            raise OrderApplicationServiceError(f"Непредвиденная ошибка при добавлении товара: {e}")

    def change_order_status(self, command: ChangeOrderStatusCommand) -> OrderDTO:
        """Изменяет статус заказа."""
        try:
            order_id = OrderId(uuid.UUID(command.order_id))
            order = self._order_repository.get_by_id(order_id)

            if not order:
                raise OrderNotFoundInAppServiceError(command.order_id)

            try:
                new_status_enum = OrderStatus[command.new_status.upper()]
            except KeyError:
                raise InvalidOrderStatusInAppServiceError(command.new_status)

            # Логика смены статуса инкапсулирована в агрегате
            # Например, order.pay(), order.ship(), или order.change_status(new_status_enum)
            # Для данного примера используем общий метод change_status, если он есть,
            # или специфичные методы, если они определены в агрегате.

            # Проверяем, есть ли специфичный метод для этого статуса
            if new_status_enum == OrderStatus.PAID:
                order.pay()
            elif new_status_enum == OrderStatus.SHIPPED:
                order.ship()
            elif new_status_enum == OrderStatus.DELIVERED:
                order.deliver()
            elif new_status_enum == OrderStatus.CANCELLED:
                order.cancel()
            else:
                # Если нет специфичного метода, пытаемся использовать общий (если он есть)
                # В нашем примере Order.change_status() уже вызывается внутри pay, ship и т.д.
                # Если бы был только общий метод, то: order.change_status(new_status_enum)
                # Но так как у нас есть специфичные, этот else может быть не нужен
                # или должен вызывать order.change_status(new_status_enum) напрямую,
                # если такая логика предусмотрена.
                # Для данного примера, если статус не один из вышеперечисленных,
                # это может считаться ошибкой, т.к. нет прямого метода для него.
                raise InvalidOrderStatusInAppServiceError(
                    f"Прямой метод для изменения статуса на '{command.new_status}' не предусмотрен."
                )

            self._order_repository.save(order)
            # Публикация событий order.get_domain_events()
            # order.clear_domain_events()

            return to_order_dto(order)
        except (OrderNotFoundError, ValueError, InvalidOrderStatusInAppServiceError) as e:
            raise OrderApplicationServiceError(f"Ошибка при изменении статуса заказа: {e}")
        except Exception as e:
            raise OrderApplicationServiceError(f"Непредвиденная ошибка при изменении статуса: {e}")

```

## Часть 5: Пример использования и простые тесты

Продемонстрируем работу сервиса.

```python
if __name__ == "__main__":
    # Инициализация репозитория
    order_repo = InMemoryOrderRepository()

    # Инициализация сервиса приложения
    order_service = OrderApplicationService(order_repository=order_repo)

    # Данные для создания заказа
    customer1_id = str(uuid.uuid4())
    product1_id = str(uuid.uuid4())
    product2_id = str(uuid.uuid4())

    shipping_addr_dto = ShippingAddressDTO(
        street="123 Main St", city="Anytown", postal_code="12345", country="USA"
    )

    item1_cmd_dto = OrderItemCommandDTO(
        product_id=product1_id, quantity=2, price_per_unit_amount="10.00", price_per_unit_currency="USD"
    )
    item2_cmd_dto = OrderItemCommandDTO(
        product_id=product2_id, quantity=1, price_per_unit_amount="25.50", price_per_unit_currency="USD"
    )

    create_cmd = CreateOrderCommand(
        customer_id=customer1_id,
        shipping_address=shipping_addr_dto,
        items=[item1_cmd_dto, item2_cmd_dto]
    )

    print("--- Создание заказа ---")
    try:
        created_order_dto = order_service.create_order(create_cmd)
        print(f"Заказ создан: {created_order_dto.order_id}")
        print(f"Статус: {created_order_dto.status}")
        print(f"Сумма: {created_order_dto.total_amount.amount} {created_order_dto.total_amount.currency}")
        order_id_for_tests = created_order_dto.order_id
    except OrderApplicationServiceError as e:
        print(f"Ошибка: {e}")
        order_id_for_tests = None

    if order_id_for_tests:
        print("\n--- Получение деталей заказа ---")
        retrieved_order_dto = order_service.get_order_details(order_id_for_tests)
        if retrieved_order_dto:
            print(f"Найден заказ: {retrieved_order_dto.order_id}, Статус: {retrieved_order_dto.status}")
            assert retrieved_order_dto.order_id == order_id_for_tests
        else:
            print(f"Заказ {order_id_for_tests} не найден.")

        print("\n--- Добавление товара в заказ ---")
        product3_id = str(uuid.uuid4())
        add_item_cmd = AddItemToOrderCommand(
            order_id=order_id_for_tests,
            product_id=product3_id,
            quantity=3,
            price_per_unit_amount="5.00",
            price_per_unit_currency="USD"
        )
        try:
            updated_order_dto = order_service.add_item_to_order(add_item_cmd)
            print(f"Товар добавлен. Новый статус: {updated_order_dto.status}")
            print(f"Новая сумма: {updated_order_dto.total_amount.amount} {updated_order_dto.total_amount.currency}")
            # Проверка: 2*10 + 1*25.50 + 3*5.00 = 20 + 25.50 + 15.00 = 60.50
            assert updated_order_dto.total_amount.amount == "60.50"
        except OrderApplicationServiceError as e:
            print(f"Ошибка: {e}")

        print("\n--- Изменение статуса заказа на PAID ---")
        change_status_cmd_paid = ChangeOrderStatusCommand(order_id=order_id_for_tests, new_status="PAID")
        try:
            paid_order_dto = order_service.change_order_status(change_status_cmd_paid)
            print(f"Статус изменен на: {paid_order_dto.status}")
            assert paid_order_dto.status == OrderStatus.PAID.value
        except OrderApplicationServiceError as e:
            print(f"Ошибка: {e}")

        print("\n--- Попытка изменить статус на некорректный (PENDING из PAID) ---")
        change_status_cmd_invalid = ChangeOrderStatusCommand(order_id=order_id_for_tests, new_status="PENDING")
        try:
            order_service.change_order_status(change_status_cmd_invalid)
        except OrderApplicationServiceError as e:
            print(f"Ожидаемая ошибка: {e}") # Должна быть ошибка о недопустимом переходе

        print("\n--- Изменение статуса заказа на SHIPPED ---")
        change_status_cmd_shipped = ChangeOrderStatusCommand(order_id=order_id_for_tests, new_status="SHIPPED")
        try:
            shipped_order_dto = order_service.change_order_status(change_status_cmd_shipped)
            print(f"Статус изменен на: {shipped_order_dto.status}")
            assert shipped_order_dto.status == OrderStatus.SHIPPED.value
        except OrderApplicationServiceError as e:
            print(f"Ошибка: {e}")

    print("\n--- Попытка получить несуществующий заказ ---")
    non_existent_id = str(uuid.uuid4())
    non_existent_order = order_service.get_order_details(non_existent_id)
    if non_existent_order is None:
        print(f"Заказ {non_existent_id} не найден, как и ожидалось.")
    else:
        print(f"Ошибка: найден несуществующий заказ {non_existent_id}")

    print("\n--- Попытка создать заказ без товаров ---")
    create_empty_cmd = CreateOrderCommand(
        customer_id=customer1_id,
        shipping_address=shipping_addr_dto,
        items=[]
    )
    try:
        order_service.create_order(create_empty_cmd)
    except OrderApplicationServiceError as e:
        print(f"Ожидаемая ошибка при создании заказа без товаров: {e}")

```

## Заключение

Это решение демонстрирует, как `OrderApplicationService` координирует работу с Агрегатом `Order` и его Репозиторием, используя DTO и Команды для взаимодействия. Сервис остается "тонким", делегируя бизнес-логику доменным объектам. Обработка ошибок также показана на базовом уровне.

Важно отметить, что в реальном приложении:
-   Управление транзакциями было бы реализовано с помощью декораторов или Unit of Work паттерна, предоставляемого ORM или инфраструктурным слоем.
-   Публикация доменных событий была бы более явной и управлялась бы через `EventPublisher`.
-   Обработка ошибок была бы более сложной, включая логирование и преобразование в HTTP-статусы или другие форматы, понятные клиенту.
-   Валидация входных данных (DTO/Команд) могла бы быть реализована с помощью библиотек типа Pydantic перед передачей в сервис.
-   Использовались бы асинхронные операции для неблокирующего I/O, если это применимо.
