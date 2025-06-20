# Упражнение по модулю "Доменные события (Domain Events)"

## Задание: Интеграция Доменных Событий в Агрегат `Order`

В этом упражнении вам предстоит модифицировать Агрегат `Order`, разработанный в предыдущем модуле (или создать его упрощенную версию), чтобы он генерировал Доменные События при значимых изменениях своего состояния. Это позволит другим частям системы реагировать на эти изменения.

### Контекст:
Представьте, что после создания заказа, добавления в него позиций или изменения его статуса, другие части системы (например, модуль уведомлений, модуль складского учета, аналитический модуль) должны быть оповещены об этих изменениях.

### Часть 1: Определение и Реализация Доменных Событий

1.  **Определите следующие Доменные События:**
    *   `OrderCreatedEvent`:
        *   Должно генерироваться при создании нового заказа.
        *   **Содержимое**: `order_id: OrderId`, `customer_id: CustomerId`, `shipping_address: ShippingAddress`, `created_at: datetime` (время создания заказа).
    *   `OrderItemAddedEvent`:
        *   Должно генерироваться при добавлении новой позиции в заказ.
        *   **Содержимое**: `order_id: OrderId`, `order_item_id: OrderItemId`, `product_id: ProductId`, `quantity: int`, `price_per_unit: Money`, `added_at: datetime` (время добавления позиции).
    *   `OrderStatusChangedEvent`:
        *   Должно генерироваться при изменении статуса заказа (например, с `PENDING` на `PAID`, с `PAID` на `SHIPPED` и т.д.).
        *   **Содержимое**: `order_id: OrderId`, `old_status: OrderStatus`, `new_status: OrderStatus`, `changed_at: datetime` (время изменения статуса).
    *   *(Опционально)* `OrderTotalAmountRecalculatedEvent`:
        *   Может генерироваться при каждом изменении состава заказа, влияющем на общую сумму (например, при добавлении/удалении позиции, изменении количества).
        *   **Содержимое**: `order_id: OrderId`, `new_total_amount: Money`, `recalculated_at: datetime`.

2.  **Реализуйте классы для этих событий.**
    *   События должны быть неизменяемыми (например, с использованием `dataclass(frozen=True)`).
    *   Каждое событие должно иметь как минимум общий базовый класс (например, `DomainEvent`) и содержать уникальный идентификатор самого события (`event_id: uuid.UUID`) и временную метку его возникновения (`occurred_on: datetime`).

### Часть 2: Модификация Агрегата `Order`

1.  **Сбор событий в Агрегате:**
    *   Агрегат `Order` должен накапливать сгенерированные им события во внутреннем списке (например, `_domain_events: List[DomainEvent]`).
    *   При каждом действии, изменяющем состояние Агрегата и требующем оповещения (создание, добавление позиции, смена статуса), соответствующее событие должно создаваться и добавляться в этот список.

2.  **Предоставление доступа к событиям:**
    *   Реализуйте метод в Агрегате `Order` (например, `get_uncommitted_events() -> List[DomainEvent]`), который возвращает список накопленных (еще не опубликованных) событий.
    *   После того как события получены из Агрегата (предположительно, для их последующей публикации внешним механизмом), внутренний список событий в Агрегате должен быть очищен. Для этого можно добавить метод `clear_uncommitted_events()`. Это гарантирует, что одни и те же экземпляры событий не будут опубликованы многократно из одного и того же экземпляра агрегата.

3.  **Примеры генерации событий в методах `Order`:**
    *   В конструкторе `Order` или его фабричном методе: генерировать `OrderCreatedEvent`.
    *   В методе `add_item`: генерировать `OrderItemAddedEvent` (и, возможно, `OrderTotalAmountRecalculatedEvent`).
    *   В методах `pay()`, `ship()`, `deliver()`, `cancel()`: генерировать `OrderStatusChangedEvent`.
    *   При удалении позиции или изменении количества также может генерироваться `OrderTotalAmountRecalculatedEvent`.

### Часть 3: (Опционально) Реализация Простого Обработчика и Диспетчера Событий

1.  **Создайте простой обработчик (или несколько обработчиков) событий.**
    *   Например, `LoggingOrderEventHandler`, который "обрабатывает" события, выводя информацию о них в консоль (например, "EVENT: Order Created - ID: {order_id}, Customer: {customer_id}, Timestamp: {occurred_on}").

2.  **Создайте простой Диспетчер Событий (Event Dispatcher/Bus) "in-memory".**
    *   Диспетчер должен иметь метод `register(event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None])` для регистрации обработчиков для определенных типов событий.
    *   Диспетчер должен иметь метод `dispatch(event: DomainEvent)`, который находит всех зарегистрированных обработчиков для типа переданного события (и его родительских типов, если это предусмотрено) и вызывает их, передавая событие.

3.  **Интеграция:**
    *   В вашем примере использования, после вызова метода Агрегата `Order`, который генерирует события:
        1.  Получите эти события с помощью `order.get_uncommitted_events()`.
        2.  Для каждого события вызовите `dispatcher.dispatch(event)`.
        3.  Очистите события в Агрегате с помощью `order.clear_uncommitted_events()`.

### Что нужно предоставить:
-   Код на Python с реализацией классов Доменных Событий (включая базовый класс `DomainEvent`).
-   Модифицированный код Агрегата `Order` и связанных с ним классов, включающий генерацию, сбор и предоставление Доменных Событий.
-   (Опционально) Код простого Диспетчера Событий и Обработчика(ов).
-   Краткие примеры использования, демонстрирующие генерацию событий Агрегатом и их (опциональную) обработку через Диспетчер.

### Критерии оценки:
-   Корректность определения и реализации Доменных Событий (включая их содержимое, неизменяемость, наличие `event_id` и `occurred_on`).
-   Правильная интеграция механизма генерации и сбора событий непосредственно в Агрегат `Order`.
-   Обеспечение того, что события генерируются в соответствующие моменты жизненного цикла Агрегата и при выполнении соответствующих операций.
-   Корректная реализация методов для получения и очистки списка событий из Агрегата.
-   (Для опциональной части) Функциональность и корректность работы простого Диспетчера и Обработчика(ов) событий.
-   Читаемость и чистота кода (соответствие PEP 8, наличие type hints и docstrings будет плюсом).

Удачи!
