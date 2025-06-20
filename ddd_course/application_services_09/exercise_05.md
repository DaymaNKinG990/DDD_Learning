# Упражнение по модулю "Сервисы приложения (Application Services)"

## Задание: Разработка `OrderApplicationService`

В этом упражнении вам предстоит разработать `OrderApplicationService`, который будет отвечать за координацию операций, связанных с Агрегатом `Order`. Сервис будет использовать Объекты Передачи Данных (DTO) для взаимодействия с внешним миром (например, с контроллерами API или командами CLI) и `OrderRepository` для работы с персистентностью.

### Контекст:
Представьте, что вы создаете бэкенд для интернет-магазина. Пользователи должны иметь возможность создавать заказы, просматривать их детали, добавлять товары в существующие заказы и отслеживать изменение их статусов. `OrderApplicationService` будет центральной точкой для этих операций.

### Часть 1: Определение Объектов Передачи Данных (DTO) и Команд

Прежде чем реализовывать сервис, определите следующие DTO и Команды (можно использовать `dataclasses`):

1.  **Команды (Commands) - для передачи намерения изменить состояние:**
    *   `CreateOrderCommand`:
        *   `customer_id: CustomerId`
        *   `shipping_address: ShippingAddressDTO` (содержит поля `street`, `city`, `postal_code`, `country`)
        *   `items: List[OrderItemCommandDTO]` (каждый `OrderItemCommandDTO` содержит `product_id: ProductId`, `quantity: int`, `price_per_unit_amount: Decimal`, `price_per_unit_currency: str`)
    *   `AddItemToOrderCommand`:
        *   `order_id: OrderId`
        *   `product_id: ProductId`
        *   `quantity: int`
        *   `price_per_unit_amount: Decimal`
        *   `price_per_unit_currency: str`
    *   `ChangeOrderStatusCommand`:
        *   `order_id: OrderId`
        *   `new_status: str` (например, "PAID", "SHIPPED")

2.  **Объекты для чтения (Query DTOs) - для представления данных:**
    *   `OrderItemDTO`:
        *   `order_item_id: OrderItemId`
        *   `product_id: ProductId`
        *   `quantity: int`
        *   `price_per_unit: MoneyDTO` (содержит `amount: Decimal`, `currency: str`)
        *   `item_total: MoneyDTO`
    *   `OrderDTO`:
        *   `order_id: OrderId`
        *   `customer_id: CustomerId`
        *   `status: str`
        *   `shipping_address: ShippingAddressDTO`
        *   `items: List[OrderItemDTO]`
        *   `total_amount: MoneyDTO`
        *   `created_at: datetime`
        *   `updated_at: datetime`
    *   `MoneyDTO`: (уже упоминался выше)
        *   `amount: Decimal`
        *   `currency: str`

### Часть 2: Реализация `OrderApplicationService`

Создайте класс `OrderApplicationService`. Он должен принимать в конструкторе экземпляр `OrderRepository` (из предыдущего модуля).

Реализуйте следующие методы:

1.  **`create_order(command: CreateOrderCommand) -> OrderDTO`**:
    *   Создает новый экземпляр Агрегата `Order` на основе данных из `command`.
        *   Для `Money` и `ShippingAddress` внутри агрегата используйте соответствующие доменные объекты, а не DTO.
    *   Сохраняет созданный Агрегат `Order` с помощью `OrderRepository.add()`.
    *   *(Опционально)* Если ваш Агрегат `Order` генерирует доменные события (например, `OrderCreatedEvent`), этот сервис может быть ответственен за их публикацию через какой-либо `EventPublisher` (для этого упражнения можно просто логировать или игнорировать).
    *   Преобразует сохраненный Агрегат `Order` в `OrderDTO` и возвращает его.
    *   **Управление транзакциями (концептуально):** Все операции с репозиторием в рамках этого метода должны рассматриваться как одна атомарная транзакция. Если какая-либо часть не удалась (например, сохранение в репозиторий), вся операция должна быть отменена. В "in-memory" репозитории это менее критично, но важно помнить о принципе.

2.  **`get_order_details(order_id: OrderId) -> Optional[OrderDTO]`**:
    *   Загружает Агрегат `Order` из `OrderRepository` по `order_id`.
    *   Если заказ найден, преобразует его в `OrderDTO` и возвращает.
    *   Если заказ не найден, возвращает `None`.

3.  **`add_item_to_order(command: AddItemToOrderCommand) -> OrderDTO`**:
    *   Загружает Агрегат `Order` из `OrderRepository` по `command.order_id`.
    *   Если заказ не найден, выбрасывает соответствующее исключение (например, `OrderNotFoundError`, которое может быть определено в доменном или инфраструктурном слое, или специфичное для сервиса приложения).
    *   Вызывает метод `add_item()` на загруженном Агрегате `Order`, передавая данные из `command`.
    *   Сохраняет измененный Агрегат `Order` с помощью `OrderRepository.save()`.
    *   *(Опционально)* Публикует события, если они были сгенерированы.
    *   Преобразует обновленный Агрегат `Order` в `OrderDTO` и возвращает его.
    *   **Транзакционность**: Загрузка, изменение и сохранение должны быть атомарны.

4.  **`change_order_status(command: ChangeOrderStatusCommand) -> OrderDTO`**:
    *   Загружает Агрегат `Order` из `OrderRepository` по `command.order_id`.
    *   Если заказ не найден, выбрасывает исключение.
    *   Преобразует строковый `command.new_status` в доменный `OrderStatus` (enum).
    *   Вызывает соответствующий метод для изменения статуса на Агрегате `Order` (например, `order.pay()`, `order.ship()`, или более общий `order.change_status(new_status_enum)`). Убедитесь, что Агрегат сам валидирует допустимость смены статуса.
    *   Сохраняет измененный Агрегат `Order` с помощью `OrderRepository.save()`.
    *   *(Опционально)* Публикует события.
    *   Преобразует обновленный Агрегат `Order` в `OrderDTO` и возвращает его.
    *   **Транзакционность**: Загрузка, изменение и сохранение должны быть атомарны.

### Часть 3: Вспомогательные функции / Мапперы

*   Вам могут понадобиться функции-мапперы для преобразования между доменными объектами (`Order`, `OrderItem`, `Money`, `ShippingAddress`) и их DTO-представлениями (`OrderDTO`, `OrderItemDTO`, `MoneyDTO`, `ShippingAddressDTO`).

### Часть 4: (Опционально) Обработка ошибок

*   Продумайте, какие исключения могут возникать (например, `OrderNotFoundError`, `InvalidOrderStatusTransitionError` из домена, ошибки валидации DTO) и как сервис должен на них реагировать. Для этого упражнения достаточно выбрасывать исключения дальше, но в реальном приложении сервис мог бы их логировать или преобразовывать в ошибки, понятные вызывающему слою.

### Что нужно предоставить:
-   Код на Python с определением всех DTO и Команд.
-   Код на Python с реализацией класса `OrderApplicationService` и его методов.
-   Реализацию `OrderRepository` (можно взять из предыдущего упражнения) и необходимые доменные классы (`Order`, `OrderItem`, `Money`, `ShippingAddress`, `OrderStatus`, идентификаторы и т.д.).
-   (Опционально) Примеры использования или простые тесты, демонстрирующие работу сервиса.

### Критерии оценки:
-   Корректное определение DTO и Команд.
-   Правильная реализация методов `OrderApplicationService`, включая:
    -   Делегирование бизнес-логики Агрегату `Order`.
    -   Взаимодействие с `OrderRepository` для загрузки и сохранения агрегатов.
    -   Использование DTO для входных данных и результатов.
    -   Корректное преобразование между доменными объектами и DTO.
-   Соблюдение принципа "тонкого" сервиса приложения (минимум бизнес-логики в самом сервисе).
-   Понимание концепции управления транзакциями (даже если реализация упрощена).
-   Читаемость и чистота кода (PEP 8, type hints, docstrings).

Удачи!
