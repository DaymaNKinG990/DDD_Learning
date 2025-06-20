# Модуль 4: Сущности (Entities)

## Содержание

- Что такое Сущности
- Идентичность и жизненный цикл
- Отличие от Объектов-значений
- Реализация на Python
- Примеры

---

## 1. Что такое Сущности (Entities)?

В Domain-Driven Design (DDD) **Сущность (Entity)** — это объект, который определяется не своими атрибутами, а **непрерывной идентичностью** (identity) и **жизненным циклом**. Сущности представляют собой ключевые объекты в доменной модели, которые имеют значение сами по себе и отслеживаются на протяжении времени.

Ключевые характеристики Сущностей:
-   **Уникальная идентичность:** Каждая Сущность имеет уникальный идентификатор, который отличает ее от всех других Сущностей того же типа, даже если все остальные атрибуты совпадают. Этот идентификатор сохраняется на протяжении всего жизненного цикла Сущности.
-   **Изменяемое состояние:** Атрибуты Сущности могут изменяться с течением времени. Например, адрес клиента (Сущность `Client`) может измениться, но это все равно будет тот же самый клиент.
-   **Жизненный цикл:** Сущности создаются, могут проходить через различные состояния и, в конечном итоге, могут быть удалены или архивированы.

Сущности часто моделируют объекты реального мира или важные концепции в домене, такие как `Пользователь`, `Заказ`, `Продукт`, `Счет`.

## 2. Идентичность и жизненный цикл

### Идентичность (Identity)

Идентичность — это то, что делает Сущность уникальной и отличимой. Она не зависит от атрибутов Сущности.
-   **Способы определения идентичности:**
    -   **Уникальный идентификатор (ID):** Наиболее распространенный способ. Это может быть UUID, числовой идентификатор из базы данных, или любой другой уникальный ключ, присваиваемый при создании Сущности.
    -   **Естественные ключи:** Иногда идентичность может быть основана на комбинации атрибутов, которые естественным образом уникальны в домене (например, номер паспорта для человека). Однако использование искусственных ID часто предпочтительнее для гибкости.

Сравнение Сущностей производится по их идентификаторам, а не по значениям атрибутов. Две Сущности с одинаковыми ID считаются одной и той же Сущностью, даже если их атрибуты различаются.

### Жизненный цикл (Lifecycle)

Жизненный цикл Сущности охватывает период от ее создания до момента, когда она перестает быть актуальной или удаляется.
-   **Создание:** Сущность создается с начальным состоянием и уникальным идентификатором. Фабрики (Factories) или конструкторы Агрегатов часто отвечают за создание Сущностей.
-   **Изменение состояния:** В течение своей жизни Сущность может претерпевать изменения своих атрибутов в результате выполнения бизнес-операций.
-   **Загрузка и сохранение:** Сущности обычно загружаются из хранилища (например, базы данных) и сохраняются обратно после изменений. За это отвечают Репозитории.
-   **Удаление/Архивация:** Когда Сущность больше не нужна, она может быть удалена или переведена в архивное состояние.

## 3. Отличие от Объектов-значений (Value Objects)

Сущности и Объекты-значения (Value Objects) — два фундаментальных строительных блока в DDD, но они имеют ключевые различия:

| Характеристика      | Сущность (Entity)                                  | Объект-значение (Value Object)                      |
| :------------------ | :------------------------------------------------- | :-------------------------------------------------- |
| **Определение**     | Определяется идентичностью                         | Определяется значениями своих атрибутов             |
| **Идентичность**    | Имеет уникальный ID, сохраняющийся со временем    | Не имеет собственной идентичности                   |
| **Сравнение**       | Сравниваются по ID                                 | Сравниваются по значениям всех атрибутов (структурно) |
| **Изменяемость**    | Обычно изменяемы (mutable)                         | Неизменяемы (immutable)                             |
| **Жизненный цикл**  | Имеет жизненный цикл (создание, изменение, удаление) | Обычно не имеет сложного жизненного цикла          |
| **Примеры**         | `Пользователь`, `Заказ`, `Автомобиль`              | `Адрес`, `Цвет`, `Диапазон дат`, `Деньги`           |

**Когда использовать Сущность:**
-   Когда объект имеет собственную историю и его идентичность важна независимо от атрибутов.
-   Когда состояние объекта может меняться со временем, но он остается тем же самым объектом.

**Когда использовать Объект-значение:**
-   Когда объект описывает характеристику или свойство другого объекта.
-   Когда важны только значения атрибутов, а не то, какой это конкретно экземпляр.
-   Когда требуется неизменяемость и простота.

## 4. Реализация на Python

В Python Сущности обычно реализуются как классы.

```python
import uuid

class User:
    def __init__(self, user_id: uuid.UUID, username: str, email: str):
        if not isinstance(user_id, uuid.UUID):
            raise TypeError("user_id must be a UUID")
        if not username:
            raise ValueError("Username cannot be empty")
        # ... другие проверки ...

        self._id: uuid.UUID = user_id
        self._username: str = username
        self._email: str = email
        self._is_active: bool = True # Пример изменяемого атрибута

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    def change_email(self, new_email: str):
        # Здесь могут быть бизнес-правила для смены email
        if not new_email: # Упрощенный пример
            raise ValueError("Email cannot be empty")
        self._email = new_email
        print(f"Email for user {self.id} changed to {new_email}")

    def deactivate(self):
        self._is_active = False
        print(f"User {self.id} deactivated.")

    # Сущности сравниваются по идентичности
    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

```

**Ключевые моменты реализации:**
-   **Идентификатор (`_id`):** Хранится как атрибут. Часто используется `uuid.UUID` для генерации уникальных ID.
-   **Свойства (`@property`):** Предоставляют доступ к атрибутам, возможно, с логикой чтения.
-   **Методы изменения состояния:** (`change_email`, `deactivate`) инкапсулируют логику изменения атрибутов и обеспечивают соблюдение инвариантов.
-   **`__eq__` и `__hash__`:** Переопределены для сравнения Сущностей по их идентификаторам. Это критически важно.
-   **Инкапсуляция:** Атрибуты часто делаются "приватными" (например, с префиксом `_`), а доступ к ним и их изменение происходит через публичные методы и свойства.

## 5. Примеры

### Пример 1: `Product`

```python
import uuid
from decimal import Decimal

class Product:
    def __init__(self, product_id: uuid.UUID, name: str, price: Decimal):
        self._id: uuid.UUID = product_id
        self._name: str = name
        self._price: Decimal = price # Цена может меняться
        self._stock_quantity: int = 0

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value:
            raise ValueError("Product name cannot be empty.")
        self._name = value

    @property
    def price(self) -> Decimal:
        return self._price

    def update_price(self, new_price: Decimal):
        if new_price <= Decimal("0"):
            raise ValueError("Price must be positive.")
        self._price = new_price
        print(f"Price for product {self.name} updated to {self.price}")

    def add_stock(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive.")
        self._stock_quantity += quantity

    def remove_stock(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity to remove must be positive.")
        if self._stock_quantity < quantity:
            raise ValueError("Not enough stock.")
        self._stock_quantity -= quantity

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

# Использование:
product_id_1 = uuid.uuid4()
product1 = Product(product_id=product_id_1, name="Laptop Pro", price=Decimal("1200.00"))
product1.add_stock(10)

product_id_2 = uuid.uuid4()
product2 = Product(product_id=product_id_2, name="Wireless Mouse", price=Decimal("25.00"))

# product1 и product2 - разные сущности
print(product1)
print(product2)

# Если бы мы создали еще один объект с тем же ID, что и product1,
# он бы считался той же сущностью:
same_product1_ref = Product(product_id=product_id_1, name="Laptop Pro X", price=Decimal("1250.00"))
print(f"product1 == same_product1_ref: {product1 == same_product1_ref}") # True, т.к. ID совпадают

product1.update_price(Decimal("1150.00")) # Состояние изменилось, но это тот же продукт
```
