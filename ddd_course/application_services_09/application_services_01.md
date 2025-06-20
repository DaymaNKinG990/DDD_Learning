# Модуль 9: Сервисы приложения (Application Services)

## Содержание

- Что такое Сервисы приложения
- Роль: оркестрация доменных объектов, координация вариантов использования (use cases)
- Отличие от Доменных сервисов
- Взаимодействие с Репозиториями и другими инфраструктурными компонентами
- Управление транзакциями и Единица работы (Unit of Work)
- Входные и выходные данные (DTO - Data Transfer Objects)
- Реализация на Python
- Примеры

---

## 1. Что такое Сервисы приложения (Application Services)?

**Сервисы приложения (Application Services)** — это компоненты в архитектуре DDD, которые отвечают за координацию выполнения вариантов использования (use cases) системы. Они являются точкой входа для внешних клиентов (например, UI, API контроллеров, других систем) и оркеструют взаимодействие между доменными объектами (Сущностями, Объектами-значениями, Агрегатами, Доменными сервисами) и инфраструктурными компонентами (Репозиториями, внешними сервисами).

Сервисы приложения не содержат бизнес-логики; эта логика принадлежит доменным объектам. Вместо этого они:
-   Извлекают Агрегаты из Репозиториев.
-   Вызывают методы на этих Агрегатах для выполнения бизнес-операций.
-   Сохраняют измененные Агрегаты обратно через Репозитории.
-   Управляют транзакциями.
-   Преобразуют данные между форматом, удобным для клиента (DTO), и доменными объектами.

## 2. Роль: оркестрация доменных объектов, координация вариантов использования

Ключевые роли Сервисов приложения:

-   **Определение вариантов использования:** Каждый публичный метод Сервиса приложения обычно соответствует одному варианту использования системы. Например, `CreateOrderService.execute(customer_id, items_data)` или `ChangeProductPriceService.execute(product_id, new_price_data)`.
-   **Оркестрация:** Они дирижируют процессом, координируя шаги, необходимые для выполнения задачи. Это может включать:
    1.  Получение данных от клиента (часто в виде DTO).
    2.  Валидацию входных данных (простую, не бизнес-правила).
    3.  Загрузку необходимых Агрегатов из Репозиториев.
    4.  Вызов методов на Агрегатах или Доменных сервисах.
    5.  Сохранение результатов через Репозитории.
    6.  Публикацию Доменных событий (если это не делает сам Агрегат).
    7.  Возврат результата клиенту (часто в виде DTO).
-   **Тонкий слой:** Сервисы приложения должны быть "тонкими", то есть не содержать сложной логики. Вся бизнес-логика должна находиться в доменном слое.

## 3. Отличие от Доменных сервисов

Важно различать Сервисы приложения и Доменные сервисы:

| Характеристика         | Сервис приложения (Application Service)                                  | Доменный сервис (Domain Service)                                       |
| :--------------------- | :----------------------------------------------------------------------- | :--------------------------------------------------------------------- |
| **Местоположение**     | Слой приложения (над доменным слоем)                                     | Доменный слой                                                          |
| **Назначение**         | Координация вариантов использования, оркестрация.                         | Реализация бизнес-логики, которая не естественна для Сущности или VO. |
| **Состояние**          | Обычно не имеют состояния (stateless).                                   | Обычно не имеют состояния (stateless).                                   |
| **Бизнес-логика**      | Не содержат бизнес-логики.                                               | Содержат бизнес-логику.                                                |
| **Зависимости**        | Зависят от доменного слоя и инфраструктурного слоя (Репозитории).        | Зависят только от других элементов доменного слоя.                     |
| **Пример**             | `OrderPlacementService`, `UserRegistrationService`                       | `FundTransferService`, `DiscountCalculationService`                    |
| **Взаимодействие с UI**| Напрямую вызываются из UI (через контроллеры, например).                 | Не вызываются напрямую из UI.                                          |

## 4. Взаимодействие с Репозиториями и другими инфраструктурными компонентами

-   **Репозитории:** Сервисы приложения используют Репозитории для загрузки Агрегатов перед выполнением операций и для сохранения их после. Они передают Агрегаты Репозиториям и получают их оттуда.
-   **Внешние сервисы:** Если вариант использования требует взаимодействия с внешними системами (например, отправка email, обработка платежей), Сервис приложения может координировать это взаимодействие, часто через адаптеры или шлюзы, определенные в инфраструктурном слое.
-   **Безопасность и авторизация:** Проверки прав доступа часто выполняются на уровне Сервисов приложения перед тем, как делегировать выполнение доменной логике.
-   **Логирование:** Сервисы приложения могут инициировать логирование операций.

## 5. Управление транзакциями и Единица работы (Unit of Work)

Одной из важнейших задач Сервисов приложения является управление транзакциями. Каждая операция, выполняемая Сервисом приложения, обычно должна быть атомарной: либо все изменения успешно сохраняются, либо никакие изменения не применяются.

-   **Начало и завершение транзакции:** Сервис приложения отвечает за начало транзакции перед выполнением доменных операций и за ее коммит (в случае успеха) или откат (в случае ошибки).
-   **Паттерн "Единица работы" (Unit of Work - UoW):** Этот паттерн помогает управлять транзакциями и отслеживать изменения в объектах. UoW собирает все изменения, сделанные в рамках одной бизнес-операции, и применяет их к базе данных атомарно.
    -   Сервис приложения начинает UoW.
    -   Все операции с Репозиториями (добавление, изменение, удаление Агрегатов) регистрируются в UoW.
    -   В конце операции Сервис приложения вызывает `commit()` у UoW, что приводит к сохранению всех изменений в одной транзакции. В случае ошибки вызывается `rollback()`.

```python
# Пример с Unit of Work (концептуально)
import abc

class AbstractUnitOfWork(abc.ABC):
    # orders: AbstractOrderRepository # Пример репозитория
    # products: AbstractProductRepository

    def __enter__(self): # Для использования с 'with'
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

# В Сервисе Приложения:
# class OrderApplicationService:
#     def __init__(self, uow: AbstractUnitOfWork):
#         self.uow = uow
#
#     def place_order(self, customer_id: CustomerId, items_data: List[ItemDataDTO]):
#         with self.uow: # Начинает транзакцию, управляет коммитом/откатом
#             # 1. Загрузить или создать Customer (через uow.customers репозиторий)
#             # 2. Создать Order (Агрегат)
#             # 3. Добавить Order в uow.orders репозиторий
#             # 4. uow.commit() будет вызван автоматически при выходе из 'with' без ошибок
#             pass
```

## 6. Входные и выходные данные (DTO - Data Transfer Objects)

Сервисы приложения часто принимают данные от клиентов и возвращают им результаты в виде **Объектов Передачи Данных (Data Transfer Objects - DTO)**.

-   **Назначение DTO:**
    -   Изолировать доменную модель от деталей представления или API.
    -   Передавать только необходимые данные, избегая избыточности.
    -   Упростить сериализацию/десериализацию данных.
-   **Характеристики DTO:**
    -   Простые структуры данных (часто dataclasses, Pydantic модели или словари).
    -   Не содержат логики.
    -   Могут включать валидацию формата данных.

```python
from dataclasses import dataclass
from typing import List
import uuid

@dataclass(frozen=True) # DTO обычно неизменяемы
class OrderItemDTO:
    product_id: uuid.UUID
    quantity: int
    price_per_unit: float # Или использовать Money VO

@dataclass(frozen=True)
class PlaceOrderCommandDTO: # DTO для команды/запроса
    customer_id: uuid.UUID
    items: List[OrderItemDTO]
    shipping_address: str

@dataclass(frozen=True)
class OrderSummaryDTO: # DTO для ответа
    order_id: uuid.UUID
    status: str
    total_amount: float

# class OrderApplicationService:
#     # ...
#     def place_order(self, command: PlaceOrderCommandDTO) -> OrderSummaryDTO:
#         # ... логика оркестрации ...
#         # 1. Преобразовать command.items в доменные OrderItem (если нужно)
#         # 2. Создать Агрегат Order
#         # 3. Сохранить
#         # 4. Вернуть OrderSummaryDTO
#         # ...
#         return OrderSummaryDTO(order_id=new_order.id, status="PENDING", total_amount=new_order.total_amount())
```

## 7. Реализация на Python

```python
import uuid
import abc # Добавим импорт abc
from typing import List, Optional

# Предположим, у нас есть доменные объекты и репозитории
# (Order, OrderItem, Product, CustomerId, OrderRepository, ProductRepository)
# и DTO (PlaceOrderCommandDTO, OrderItemDTO, OrderSummaryDTO)

class Order: # Упрощенный Агрегат
    def __init__(self, order_id: uuid.UUID, customer_id: uuid.UUID):
        self.id = order_id
        self.customer_id = customer_id
        self._items = []
        self.status = "NEW"

    def add_item(self, product_id: uuid.UUID, quantity: int, price: float):
        # Здесь может быть логика проверки инвариантов
        self._items.append({"product_id": product_id, "quantity": quantity, "price": price})

    def calculate_total(self) -> float:
        return sum(item['quantity'] * item['price'] for item in self._items)

    def confirm(self):
        # Логика подтверждения заказа
        self.status = "CONFIRMED"

# Интерфейс репозитория (определен в домене)
class AbstractOrderRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, order: Order):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, order: Order):
        raise NotImplementedError

# Сервис приложения
class OrderApplicationService:
    def __init__(self, order_repository: AbstractOrderRepository, uow: AbstractUnitOfWork):
        self.order_repository = order_repository # Может быть частью UoW
        self.uow = uow

    def place_order(self, command: PlaceOrderCommandDTO) -> OrderSummaryDTO:
        with self.uow: # Управление транзакцией
            order_id = uuid.uuid4()
            # Здесь может быть загрузка Customer, Product и т.д. для проверок
            # Например, проверка существования продуктов, кредитного лимита клиента.

            new_order = Order(order_id=order_id, customer_id=command.customer_id)

            for item_dto in command.items:
                # В реальном приложении здесь может быть получение цены продукта из ProductRepository
                # или передача цены в DTO, если она фиксируется на момент заказа.
                # Предположим, цена передается в DTO для простоты.
                new_order.add_item(
                    product_id=item_dto.product_id,
                    quantity=item_dto.quantity,
                    price=item_dto.price_per_unit
                )

            self.order_repository.add(new_order) # Репозиторий регистрирует в UoW
            # self.uow.commit() будет вызван автоматически

        return OrderSummaryDTO(
            order_id=new_order.id,
            status=new_order.status,
            total_amount=new_order.calculate_total()
        )

    def confirm_order(self, order_id: uuid.UUID) -> OrderSummaryDTO:
        with self.uow:
            order = self.order_repository.get_by_id(order_id)
            if not order:
                raise ValueError(f"Order with ID {order_id} not found.") # Или специфическое исключение

            order.confirm() # Вызов доменной логики
            self.order_repository.save(order) # Сохранение изменений
            # self.uow.commit()

        return OrderSummaryDTO(
            order_id=order.id,
            status=order.status,
            total_amount=order.calculate_total()
        )

```

## 8. Примеры и лучшие практики

-   **Простота:** Сервисы приложения должны быть простыми и фокусироваться на координации.
-   **Одна ответственность:** Каждый метод сервиса обычно соответствует одному варианту использования.
-   **Использование DTO:** Использование DTO для входных и выходных данных помогает поддерживать слабую связанность.
-   **Обработка ошибок:** Сервисы приложения должны обрабатывать ошибки, возникающие в процессе выполнения (например, ошибки валидации, не найденные сущности, ошибки доменной логики), и преобразовывать их в понятные ответы для клиента (например, HTTP статусы и сообщения об ошибках).
-   **Идемпотентность:** По возможности, делайте операции сервисов приложения идемпотентными, особенно если они вызываются через сеть.
-   **Безопасность:** Интегрируйте проверки авторизации и аутентификации на этом уровне.

Сервисы приложения являются важным связующим звеном между внешним миром и богатой доменной моделью, обеспечивая чистоту и структурированность приложения.
