# Модуль 8: Репозитории (Repositories)

## Содержание

- Что такое Репозитории
- Назначение: абстракция доступа к данным
- Отделение доменного слоя от инфраструктуры
- Интерфейс Репозитория и его методы (например, `add`, `get_by_id`, `find`, `remove`)
- Реализация Репозиториев (in-memory, с использованием ORM типа SQLAlchemy)
- Связь с Агрегатами
- Примеры

---

## 1. Что такое Репозитории (Repositories)?

**Репозиторий (Repository)** в Domain-Driven Design — это компонент, который инкапсулирует логику доступа к данным для Агрегатов. Он предоставляет интерфейс, имитирующий коллекцию объектов в памяти, позволяя доменному слою запрашивать и сохранять Агрегаты, не зная о деталях их хранения (база данных, файлы, веб-сервисы и т.д.).

Репозитории являются ключевым элементом для отделения доменной модели от инфраструктурных проблем, связанных с персистентностью.

## 2. Назначение: абстракция доступа к данным

Основное назначение Репозиториев:

-   **Абстрагирование хранилища:** Скрывают детали конкретного механизма хранения (SQL база данных, NoSQL, файловая система, API) от доменного слоя и сервисов приложения.
-   **Централизация логики запросов:** Предоставляют четко определенные методы для получения Агрегатов на основе различных критериев. Это помогает избежать дублирования кода запросов по всей системе.
-   **Имитация коллекции в памяти:** Для клиента (например, Сервиса Приложения) Репозиторий выглядит как обычная коллекция объектов, поддерживающая операции добавления, удаления и поиска.
-   **Управление жизненным циклом Агрегатов:** Репозитории отвечают за восстановление Агрегатов из хранилища и сохранение их изменений.

## 3. Отделение доменного слоя от инфраструктуры

Репозитории играют критическую роль в поддержании чистоты доменного слоя:

-   **Интерфейс в домене, реализация в инфраструктуре:** Интерфейс Репозитория (абстрактный класс или протокол) определяется в доменном слое, так как он описывает контракт, необходимый домену. Конкретные реализации этого интерфейса (например, `SqlAlchemyOrderRepository`) находятся в инфраструктурном слое.
-   **Принцип инверсии зависимостей (DIP):** Доменный слой зависит от абстракции Репозитория, а не от конкретной реализации. Это позволяет легко заменять или тестировать различные механизмы хранения.
-   **Тестируемость:** Возможность подменить реальную реализацию Репозитория на in-memory версию (заглушку или мок) значительно упрощает модульное тестирование доменной логики и сервисов приложения без необходимости подключения к реальной базе данных.

## 4. Интерфейс Репозитория и его методы

Интерфейс Репозитория обычно определяется для каждого типа Агрегата, которым нужно управлять. Типичные методы включают:

-   `add(aggregate: AggregateRoot)`: Добавляет новый Агрегат в Репозиторий (для последующего сохранения).
-   `get_by_id(id: AggregateId) -> Optional[AggregateRoot]`: Находит Агрегат по его уникальному идентификатору. Возвращает `None` или выбрасывает исключение, если Агрегат не найден.
-   `save(aggregate: AggregateRoot)`: Сохраняет изменения в существующем Агрегате. Иногда этот метод объединяют с `add` (например, `upsert` или просто `save`, который определяет, новый ли это объект).
-   `remove(aggregate: AggregateRoot)` или `remove_by_id(id: AggregateId)`: Удаляет Агрегат из Репозитория.
-   `find_all() -> List[AggregateRoot]`: Возвращает все Агрегаты данного типа (использовать с осторожностью для больших коллекций).
-   **Специфичные методы поиска:** `find_by_criteria(criteria: Criteria) -> List[AggregateRoot]`. Например, `find_by_customer_id(customer_id: CustomerId) -> List[Order]`. Такие методы инкапсулируют конкретные запросы, необходимые домену.

**Паттерн Спецификация (Specification Pattern):**
Для более сложных и гибких запросов может использоваться паттерн Спецификация. Спецификация — это объект, который инкапсулирует критерии запроса. Репозиторий может иметь метод типа `query(specification: Specification) -> List[AggregateRoot]`.

## 5. Реализация Репозиториев

### In-Memory Реализация
Используется для тестирования или в простых случаях. Хранит объекты в словаре или списке в памяти.

```python
import abc
import uuid
from typing import Dict, List, Optional, TypeVar, Generic # Добавим Generic

# Предположим, у нас есть Агрегат Order
class Order: # Упрощенный Агрегат для примера
    def __init__(self, order_id: uuid.UUID, customer_id: uuid.UUID):
        self.id: uuid.UUID = order_id
        self.customer_id: uuid.UUID = customer_id
        self._items: list = [] # упрощенно

    def add_item(self, product_name: str, quantity: int):
        self._items.append({"product": product_name, "quantity": quantity})

    # ... другие методы ...


T = TypeVar('T')

class AbstractRepository(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def add(self, entity: T):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, entity_id: uuid.UUID) -> Optional[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def list_all(self) -> List[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, entity: T): # Может быть не нужен, если add/get работают с уже сохраненными
        raise NotImplementedError

    @abc.abstractmethod # Добавим remove в интерфейс
    def remove(self, entity_id: uuid.UUID):
        raise NotImplementedError

class InMemoryOrderRepository(AbstractRepository[Order]):
    def __init__(self):
        self._orders: Dict[uuid.UUID, Order] = {}

    def add(self, order: Order):
        if order.id in self._orders:
            raise ValueError(f"Order with ID {order.id} already exists.")
        self._orders[order.id] = order
        print(f"Order {order.id} added to in-memory repository.")

    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        return self._orders.get(order_id)

    def list_all(self) -> List[Order]:
        return list(self._orders.values())

    def save(self, order: Order):
        # В in-memory, если объект уже есть (получен через get_by_id и изменен),
        # он уже обновлен в словаре, так как хранится по ссылке.
        # Этот метод может быть нужен для явного указания на сохранение
        # или если объекты копируются при извлечении.
        if order.id not in self._orders:
            raise ValueError(f"Order with ID {order.id} not found for saving.")
        self._orders[order.id] = order # Перезаписываем на случай, если объект был заменен
        print(f"Order {order.id} 'saved' in in-memory repository.")

    def remove(self, order_id: uuid.UUID):
        if order_id in self._orders:
            del self._orders[order_id]
            print(f"Order {order_id} removed from in-memory repository.")
        else:
            raise ValueError(f"Order with ID {order_id} not found for removal.")

```

### Реализация с использованием ORM (например, SQLAlchemy)
Здесь Репозиторий будет взаимодействовать с сессией SQLAlchemy для выполнения операций с базой данных.

```python
from sqlalchemy.orm import Session # Типизация для сессии

# class SqlAlchemyOrderRepository(AbstractRepository[Order]):
#     def __init__(self, session: Session):
#         self.session = session
#
#     def add(self, order: Order):
#         # Преобразование доменной модели Order в модель SQLAlchemy (если они разные)
#         # или直接использование доменной модели, если она маппится ORM
#         self.session.add(order)
#         # Коммит обычно происходит вне репозитория, например, в Unit of Work или Application Service
#         print(f"Order {order.id} added to SQLAlchemy session.")
#
#     def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
#         # Здесь Order должен быть классом, смапленным SQLAlchemy
#         return self.session.query(Order).filter_by(id=order_id).first()
#
#     def list_all(self) -> List[Order]:
#         return self.session.query(Order).all()
#
#     def save(self, order: Order):
#         # SQLAlchemy сессия отслеживает изменения в объектах, полученных из нее.
#         # Явный вызов add или merge может потребоваться, если объект 'отсоединен' от сессии
#         # или если это новый объект, который должен быть обновлен (upsert).
#         # Часто, если объект уже в сессии, изменения будут сохранены при коммите сессии.
#         self.session.add(order) # или self.session.merge(order)
#         print(f"Order {order.id} marked for save in SQLAlchemy session.")
#
#     def remove(self, order_id: uuid.UUID): # или remove_by_id
#         order_to_delete = self.get_by_id(order_id)
#         if order_to_delete:
#             self.session.delete(order_to_delete)
#             print(f"Order {order_id} marked for deletion in SQLAlchemy session.")
#         else:
#             print(f"Order {order_id} not found for deletion.")

```
**Примечание:** В реальном приложении с SQLAlchemy, управление транзакциями и сессиями часто выносится в паттерн **Unit of Work (Единица Работы)**, который координирует работу одного или нескольких Репозиториев в рамках одной бизнес-транзакции.

## 6. Связь с Агрегатами

-   **Один Репозиторий на Корень Агрегата:** Как правило, для каждого типа Корня Агрегата создается свой Репозиторий (например, `OrderRepository`, `CustomerRepository`).
-   **Возвращают Агрегаты:** Методы Репозитория, которые извлекают данные (например, `get_by_id`, `find_`), должны возвращать полностью восстановленные экземпляры Агрегатов. Это гарантирует, что клиент получает объект, готовый к выполнению доменной логики и соблюдению своих инвариантов.
-   **Работают с Агрегатами целиком:** Репозитории загружают и сохраняют Агрегаты как единое целое. Не должно быть методов, которые загружают или сохраняют только части Агрегата.

## 7. Примеры и лучшие практики

-   **Методы Репозитория должны быть специфичны для домена:** Называйте методы поиска так, чтобы они отражали бизнес-запросы (например, `find_overdue_invoices()` вместо `find_by_status_and_due_date_less_than_now()`).
-   **Транзакции:** Репозитории сами по себе обычно не управляют транзакциями БД. Управление транзакциями (начало, коммит, откат) — это ответственность вышестоящего слоя, часто Сервисов Приложения или паттерна Unit of Work. Репозиторий просто выполняет операции в рамках текущей транзакции.
-   **Избегайте утечки деталей инфраструктуры:** Интерфейс Репозитория не должен содержать типов или концепций, специфичных для конкретной СУБД или ORM (например, не должен возвращать `QuerySet` Django или `sqlalchemy.Query`).
-   **Оптимизация запросов:** Хотя Репозиторий абстрагирует хранилище, его реализация должна быть эффективной. Это может потребовать написания оптимизированных запросов в инфраструктурном слое.
-   **Не возвращайте `None` без необходимости:** Если ожидается, что Агрегат должен существовать (например, при обновлении), то его отсутствие может быть ошибкой, и Репозиторий может выбросить исключение `NotFoundException`. Для опциональных поисков возврат `Optional[AggregateRoot]` (или `None`) уместен.

Репозитории являются мощным средством для создания чистой и поддерживаемой архитектуры, позволяя доменной логике оставаться независимой от способа хранения данных.
