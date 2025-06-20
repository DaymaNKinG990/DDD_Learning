# Упражнение по модулю "Агрегаты (Aggregates)"

## Задание: Разработка Агрегата `Order` (Заказ)

В этом упражнении вам предстоит спроектировать и реализовать Агрегат `Order` для упрощенной системы электронной коммерции. Основное внимание следует уделить правильному определению Корня Агрегата, его внутренних Сущностей и Объектов-значений, а также обеспечению инвариантов.

### Контекст:
Представьте, что вы разрабатываете систему, где клиенты могут создавать заказы, добавлять в них товары, указывать адрес доставки и отслеживать статус заказа.

### Часть 1: Проектирование Агрегата `Order`

Прежде чем писать код, продумайте структуру Агрегата.

1.  **Корень Агрегата (Aggregate Root):**
    *   `Order`: Основная Сущность, представляющая заказ клиента. Должна иметь уникальный идентификатор (`OrderId`).

2.  **Внутренние Сущности (Entities within Aggregate):**
    *   `OrderItem`: Представляет одну позицию в заказе (конкретный товар, количество, цена за единицу на момент добавления). Каждая `OrderItem` должна иметь уникальный идентификатор в рамках заказа (`OrderItemId`) и ссылку на `ProductId` (идентификатор товара из другого Агрегата/контекста).

3.  **Объекты-значения (Value Objects within Aggregate):**
    *   `Money`: Для представления цены и суммы (например, с атрибутами `amount` и `currency`).
    *   `ShippingAddress`: Адрес доставки (например, с атрибутами `street`, `city`, `postal_code`, `country`). Должен быть неизменяемым.
    *   `OrderStatus`: Перечисление (Enum) или Объект-значение для представления статуса заказа (например, `PENDING`, `PAID`, `SHIPPED`, `DELIVERED`, `CANCELLED`).

### Часть 2: Реализация Агрегата `Order`

Разработайте класс `Order` и связанные с ним классы на Python.

**Требования к `Order` (Корень Агрегата):**
1.  **Атрибуты `Order`:**
    *   `order_id: OrderId` (может быть UUID или другой уникальный тип)
    *   `customer_id: CustomerId` (ID клиента, ссылка на другой Агрегат)
    *   `order_items: list[OrderItem]` (список позиций заказа)
    *   `shipping_address: ShippingAddress`
    *   `status: OrderStatus`
    *   `total_amount: Money` (общая сумма заказа, вычисляемая)
    *   `created_at: datetime`
    *   `updated_at: datetime`

2.  **Методы `Order` (должны обеспечивать инварианты):**
    *   Конструктор (или фабричный метод) для создания нового заказа. Начальный статус `PENDING`.
    *   `add_item(product_id: ProductId, quantity: int, price_per_unit: Money)`:
        *   Создает новую `OrderItem` и добавляет ее в заказ.
        *   **Инвариант:** Нельзя добавить товар с количеством <= 0.
        *   **Инвариант:** Если товар уже есть в заказе, его количество должно увеличиваться, а не создаваться новая позиция (или это может быть отдельный метод `update_item_quantity`). Для упрощения, можно разрешить дублирование ProductId в разных OrderItem, если это разные "добавления". Либо, более сложный вариант - объединять. Выберите один подход.
        *   **Инвариант:** Общая сумма заказа (`total_amount`) должна корректно пересчитываться.
        *   *Упрощение:* Не будем проверять реальное наличие товара на складе в этом упражнении.
    *   `remove_item(order_item_id: OrderItemId)`:
        *   Удаляет позицию из заказа.
        *   **Инвариант:** Общая сумма заказа должна корректно пересчитываться.
        *   **Инвариант:** Нельзя удалить несуществующую позицию.
    *   `update_item_quantity(order_item_id: OrderItemId, new_quantity: int)`:
        *   Изменяет количество товара в существующей позиции.
        *   **Инвариант:** Количество не может быть <= 0. Если 0, позиция должна удаляться (или это отдельный бизнес-кейс).
        *   **Инвариант:** Общая сумма заказа должна корректно пересчитываться.
    *   `change_shipping_address(new_address: ShippingAddress)`:
        *   **Инвариант:** Нельзя изменить адрес для заказа, который уже `SHIPPED` или `DELIVERED`.
    *   `pay()`:
        *   Изменяет статус на `PAID`.
        *   **Инвариант:** Можно оплатить только заказ в статусе `PENDING`.
        *   *Опционально:* Может генерировать доменное событие `OrderPaid`.
    *   `ship()`:
        *   Изменяет статус на `SHIPPED`.
        *   **Инвариант:** Можно отправить только заказ в статусе `PAID`.
        *   *Опционально:* Может генерировать доменное событие `OrderShipped`.
    *   `deliver()`:
        *   Изменяет статус на `DELIVERED`.
        *   **Инвариант:** Можно доставить только заказ в статусе `SHIPPED`.
    *   `cancel()`:
        *   Изменяет статус на `CANCELLED`.
        *   **Инвариант:** Нельзя отменить заказ, который уже `DELIVERED`. (Правила отмены могут быть сложнее, но для упражнения это достаточно).
        *   *Опционально:* Может генерировать доменное событие `OrderCancelled`.

3.  **Требования к `OrderItem` (Внутренняя Сущность):**
    *   **Атрибуты:** `order_item_id: OrderItemId`, `product_id: ProductId`, `quantity: int`, `price_per_unit: Money`.
    *   Метод `calculate_item_total() -> Money` для расчета суммы по этой позиции.
    *   Доступ к изменению `OrderItem` должен быть только через методы Корня Агрегата `Order`.

4.  **Требования к `ShippingAddress`, `Money`, `OrderStatus` (Объекты-значения):**
    *   Должны быть неизменяемыми.
    *   Должны реализовывать `__eq__` и `__hash__` для сравнения по значению.
    *   `Money` должен поддерживать операции сложения и, возможно, умножения на число (для расчета общей стоимости).

### Что нужно предоставить:
-   Код на Python с реализацией классов `Order`, `OrderItem`, `ShippingAddress`, `Money`, `OrderStatus` и вспомогательных типов ID.
-   Краткие примеры использования вашего Агрегата `Order`, демонстрирующие создание заказа, добавление/удаление позиций, изменение статусов и проверку инвариантов.

### Критерии оценки:
-   Корректность определения Корня Агрегата и его границ.
-   Правильное управление жизненным циклом внутренних Сущностей (`OrderItem`) через Корень Агрегата.
-   Обеспечение инвариантов Агрегата его методами.
-   Корректная реализация Объектов-значений (`ShippingAddress`, `Money`, `OrderStatus`).
-   Соблюдение принципа инкапсуляции (внутреннее состояние Агрегата не должно быть напрямую изменяемо извне, кроме как через его публичные методы).
-   Читаемость и чистота кода (соответствие PEP 8, наличие type hints и docstrings будет плюсом).

Удачи!
