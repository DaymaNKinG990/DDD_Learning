# Модуль 7: Доменные события (Domain Events)

## Содержание

- Что такое Доменные события
- Назначение и преимущества
- Характеристики Доменных событий (прошедшее время, неизменяемость)
- Моделирование событий
- Публикация и подписка на события (Event Dispatching)
- Использование для интеграции между Агрегатами и Ограниченными контекстами
- Реализация на Python
- Примеры

---

## 1. Что такое Доменные события (Domain Events)?

**Доменное событие (Domain Event)** — это объект, который представляет собой что-то значимое, что произошло в домене. События являются фактами прошлого и, как правило, неизменяемы. Они фиксируют изменения состояния в системе или важные бизнес-моменты.

В отличие от команд, которые выражают намерение что-то сделать, доменные события сообщают о том, что уже произошло.

Примеры доменных событий:
-   `OrderPlaced` (Заказ размещен)
-   `PaymentProcessed` (Платеж обработан)
-   `UserRegistered` (Пользователь зарегистрирован)
-   `InventoryItemOutOfStock` (Товар на складе закончился)
-   `ShipmentDispatched` (Отправка отгружена)

## 2. Назначение и преимущества

Доменные события играют важную роль в DDD и архитектуре сложных систем:

-   **Декомпозиция и слабая связанность:** Позволяют различным частям системы (например, разным Агрегатам или Ограниченным Контекстам) реагировать на изменения в других частях, не имея прямых зависимостей.
-   **Интеграция:** Служат механизмом для интеграции между Агрегатами внутри одного Ограниченного Контекста или между разными Ограниченными Контекстами.
-   **Итоговая согласованность (Eventual Consistency):** Помогают достичь согласованности данных между различными частями системы асинхронно.
-   **Аудит и история:** Запись доменных событий может служить журналом аудита, отражающим историю изменений в системе.
-   **Уведомления:** Могут использоваться для уведомления внешних систем или пользователей о произошедших событиях.
-   **Побочные эффекты:** Позволяют вынести побочные эффекты из логики Агрегата. Агрегат генерирует событие, а другие компоненты (обработчики событий) выполняют связанные действия (например, отправка email, обновление другого Агрегата).
-   **CQRS (Command Query Responsibility Segregation):** Доменные события часто используются для обновления "читающей" модели (Query Model) в системах, построенных по принципу CQRS.

## 3. Характеристики Доменных событий

-   **Именование в прошедшем времени:** Имена событий обычно являются глаголами в прошедшем времени, так как они описывают уже свершившийся факт (например, `OrderCreated`, `ItemAddedToCart`).
-   **Неизменяемость (Immutability):** Поскольку событие представляет собой факт из прошлого, оно не должно изменяться после создания. Все необходимые данные для понимания события должны быть включены в него в момент создания.
-   **Содержат данные о событии:** Событие должно нести достаточную информацию, чтобы подписчики могли на него отреагировать, не обращаясь за дополнительными данными к источнику события (хотя иногда передают только ID сущности, если объем данных велик).
-   **Уникальность (не всегда):** Иногда событиям присваивают уникальный идентификатор, особенно если они сохраняются или передаются через очереди сообщений.
-   **Временная метка:** Часто полезно включать временную метку, указывающую, когда событие произошло.

## 4. Моделирование событий

При моделировании доменных событий следует учитывать:

-   **Зернистость:** События могут быть мелкозернистыми (например, `CustomerAddressChanged`) или крупнозернистыми (`OrderShipped`, которое может подразумевать множество мелких изменений). Выбор зависит от потребностей домена.
-   **Данные события:** Определите, какие данные должны содержаться в событии. Включайте только то, что релевантно для потенциальных подписчиков и описывает сам факт события.
    -   **Толстые события (Fat Events):** Содержат все необходимые данные. Упрощают работу подписчиков, но могут быть избыточны.
    -   **Тонкие события (Thin Events):** Содержат только идентификаторы затронутых сущностей. Подписчикам нужно будет запрашивать детали, что может привести к дополнительным запросам и проблемам с согласованностью во времени.
-   **Именование:** Имя события должно четко отражать его суть с точки зрения бизнеса.
-   **Источник события:** Иногда полезно знать, какой Агрегат или компонент сгенерировал событие.

## 5. Публикация и подписка на события (Event Dispatching)

Механизм публикации и подписки (часто называемый **Event Dispatcher** или **Event Bus**) позволяет компонентам публиковать события, а другим компонентам (подписчикам или обработчикам) — реагировать на них.

**Процесс обычно выглядит так:**
1.  **Генерация события:** Агрегат или Сервис Приложения создает экземпляр доменного события после выполнения какой-либо операции.
2.  **Публикация события:** Событие передается в Диспетчер Событий.
3.  **Обработка события:** Диспетчер Событий находит всех зарегистрированных подписчиков (обработчиков) для данного типа события и вызывает их.

**Способы реализации Диспетчера Событий:**
-   **Синхронный (In-Process):** Обработчики вызываются немедленно в том же процессе и потоке, что и публикатор. Это просто в реализации, но может замедлить основную операцию, если обработчики выполняются долго. Обычно используется для реакций внутри одного Агрегата или для немедленных побочных эффектов в рамках той же транзакции.
-   **Асинхронный (Out-of-Process или Background):** События помещаются в очередь (например, RabbitMQ, Kafka, Redis Streams), а обработчики выполняются в отдельных процессах или потоках. Это обеспечивает лучшую отзывчивость основной операции и отказоустойчивость, но вводит итоговую согласованность.
-   **Комбинированный подход:** Некоторые обработчики могут быть синхронными, другие — асинхронными.

**Регистрация обработчиков:**
-   Явная регистрация: `dispatcher.subscribe(OrderPlacedEvent, SendOrderConfirmationEmailHandler)`
-   На основе соглашений или декораторов: `@handles(OrderPlacedEvent)`

## 6. Использование для интеграции

### Между Агрегатами (внутри одного Ограниченного Контекста)

Когда изменение в одном Агрегате должно вызвать реакцию в другом Агрегате, но мы хотим избежать прямой зависимости между ними.
Пример: После события `OrderPaid` (из Агрегата `Order`), Агрегат `Customer` может обновить свой статус лояльности или кредитный лимит. Обработчик события `OrderPaid` загрузит нужный `Customer` и вызовет его метод.

### Между Ограниченными Контекстами

Доменные события — один из основных способов интеграции между различными Ограниченными Контекстами.
Пример: В Контексте "Продажи" происходит событие `OrderShipped`. Контекст "Уведомления" подписывается на это событие и отправляет email клиенту.
Здесь часто используются асинхронные брокеры сообщений. События, публикуемые одним контекстом, могут быть преобразованы (через Anti-Corruption Layer) перед тем, как их получит другой контекст, если их модели домена различаются.

## 7. Реализация на Python

Существует несколько подходов к реализации доменных событий на Python:

### Простая реализация с колбэками:

```python
import datetime
import uuid
from typing import Callable, Dict, List, Type, Any
from dataclasses import dataclass # Добавим для OrderPlaced
from decimal import Decimal # Добавим для OrderPlaced

class DomainEvent:
    def __init__(self):
        self.occurred_on: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        self.event_id: uuid.UUID = uuid.uuid4()

@dataclass
class OrderPlaced(DomainEvent):
    order_id: uuid.UUID
    customer_id: uuid.UUID
    total_amount: Decimal

# Простой диспетчер событий
class EventDispatcher:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent):
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event) # Синхронный вызов
                except Exception as e:
                    # Логирование ошибки, но не прерывание других обработчиков
                    print(f"Error handling event {event_type.__name__}: {e}")

# Пример использования
dispatcher = EventDispatcher()

def send_confirmation_email(event: OrderPlaced):
    print(f"Sending confirmation email for order {event.order_id} to customer {event.customer_id}")

def update_reporting_dashboard(event: OrderPlaced):
    print(f"Updating reporting dashboard for new order {event.order_id} with amount {event.total_amount}")

dispatcher.subscribe(OrderPlaced, send_confirmation_email)
dispatcher.subscribe(OrderPlaced, update_reporting_dashboard)

# В Агрегате или Сервисе Приложения:
# new_order_event = OrderPlaced(order_id=uuid.uuid4(), customer_id=uuid.uuid4(), total_amount=Decimal("99.99"))
# dispatcher.publish(new_order_event)
```

### Использование библиотек

Существуют библиотеки, которые упрощают работу с событиями, например:
-   **`events` (от python-events):** Простая библиотека для публикации/подписки.
-   **`PyPubSub`:** Более зрелая библиотека для pub/sub.
-   Интеграция с брокерами сообщений (например, `pika` для RabbitMQ, `kafka-python` для Kafka) для асинхронной обработки.

Пример с `events`:

```python
from events import Events as EventManager # Renamed to avoid conflict
from dataclasses import dataclass
import datetime
import uuid
from decimal import Decimal

# Базовый класс события (не обязательно, но может быть полезен)
class DomainEvent:
    def __init__(self):
        self.occurred_on: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        self.event_id: uuid.UUID = uuid.uuid4()

@dataclass
class ProductCreated(DomainEvent):
    product_id: uuid.UUID
    name: str
    price: Decimal

# Создаем экземпляр менеджера событий
event_manager = EventManager()

# Обработчики
def log_product_creation(event: ProductCreated):
    print(f"[{event.occurred_on}] Product created: ID={event.product_id}, Name='{event.name}', Price={event.price}")

def notify_inventory_system(event: ProductCreated):
    print(f"Notifying inventory system about new product: {event.product_id}")

# Подписываем обработчики на событие ProductCreated
event_manager.on_event(ProductCreated, log_product_creation)
event_manager.on_event(ProductCreated, notify_inventory_system)


# Генерация и публикация события
# if __name__ == "__main__":
#     # Внутри вашего Агрегата или Сервиса Приложения
#     new_product = ProductCreated(
#         product_id=uuid.uuid4(),
#         name="Awesome Gadget",
#         price=Decimal("199.99")
#     )
#     # Для библиотеки python-events, если ProductCreated не наследуется от events.Event,
#     # и мы хотим передать инстанс, нужно обернуть или использовать другой метод.
#     # Обычно trigger_event ожидает тип и kwargs, либо объект, который сам знает как себя триггерить.
#     # Простой способ - передать сам объект, если обработчики ожидают именно его тип:
#     event_manager.trigger_event(ProductCreated, new_product)
```
В библиотеке `events` принято передавать тип события и аргументы для его конструктора, либо сам объект события.
Более каноничным для `python-events` является передача аргументов:
`event_manager.trigger_event(ProductCreated, product_id=new_product.product_id, name=new_product.name, price=new_product.price)`
Или определение события как класса, наследуемого от `events.Event`:
```python
from events import Events as EventManager, Event
# ...
class ProductCreated(Event): # Наследуемся от events.Event
    def __init__(self, product_id: uuid.UUID, name: str, price: Decimal, occurred_on: datetime.datetime):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.occurred_on = occurred_on
# ...
# event_manager.trigger_event(ProductCreated(product_id=..., name=..., price=..., occurred_on=...))
```
Однако, передача инстанса события, как в примере выше, тоже часто используется для интеграции с кастомными базовыми классами событий.

## 8. Примеры

### Пример 1: Регистрация пользователя

1.  **Команда:** `RegisterUserCommand(username, email, password)`
2.  **Сервис Приложения:** Обрабатывает команду, создает Агрегат `User`.
3.  **Агрегат `User`:** После успешного создания и сохранения генерирует событие `UserRegistered(user_id, username, email, registration_date)`.
4.  **Диспетчер Событий:** Публикует `UserRegistered`.
5.  **Обработчики:**
    -   `SendWelcomeEmailHandler`: Подписывается на `UserRegistered`, отправляет приветственное письмо.
    -   `CreateUserProfileHandler`: Подписывается на `UserRegistered`, создает начальный профиль для пользователя.
    -   `LogUserActivityHandler`: Подписывается на `UserRegistered`, логирует факт регистрации.

### Пример 2: Изменение цены товара

1.  **Команда:** `ChangeProductPriceCommand(product_id, new_price)`
2.  **Агрегат `Product`:** Обновляет свою цену, генерирует событие `ProductPriceChanged(product_id, old_price, new_price, changed_at)`.
3.  **Диспетчер Событий:** Публикует `ProductPriceChanged`.
4.  **Обработчики:**
    -   `UpdateSearchIndexHandler`: Подписывается на `ProductPriceChanged`, обновляет цену товара в поисковом индексе.
    -   `NotifyWatchlistUsersHandler`: Подписывается на `ProductPriceChanged`, проверяет, есть ли пользователи, отслеживающие этот товар, и уведомляет их об изменении цены (если изменение существенное).
    -   `InvalidateProductCacheHandler`: Подписывается на `ProductPriceChanged`, инвалидирует кэш для данного товара.

Доменные события являются фундаментальным строительным блоком для создания гибких, масштабируемых и слабосвязанных систем, основанных на принципах DDD.
