# Модуль 5: Объекты-значения (Value Objects)

## Содержание

- Что такое Объекты-значения
- Неизменяемость (Immutability)
- Равенство на основе атрибутов
- Отличие от Сущностей
- Реализация на Python (например, с использованием `dataclasses`)
- Примеры

---

## 1. Что такое Объекты-значения (Value Objects)?

В Domain-Driven Design (DDD) **Объект-значение (Value Object)** — это неизменяемый объект, который представляет собой описательную характеристику или концепцию в доменной модели и определяется **значениями своих атрибутов**, а не уникальной идентичностью. У Объектов-значений нет собственного жизненного цикла в том смысле, в каком он есть у Сущностей.

Ключевые характеристики Объектов-значений:
-   **Определяются атрибутами:** Два Объекта-значения считаются равными, если все их атрибуты равны.
-   **Неизменяемость (Immutability):** После создания Объект-значение не может быть изменен. Если требуется другое значение, создается новый экземпляр.
-   **Отсутствие идентичности:** У Объектов-значений нет уникального идентификатора, который бы отличал один экземпляр от другого, если их атрибуты совпадают.
-   **Самодостаточность и валидация:** Часто инкапсулируют логику валидации своих значений при создании.
-   **Повышают выразительность модели:** Позволяют создавать более богатые и понятные типы данных, отражающие концепции предметной области (например, `Money`, `Address`, `DateRange`).

Примеры Объектов-значений: `Деньги` (сумма и валюта), `Адрес` (улица, город, почтовый индекс), `Цвет`, `Процент`, `Координаты`.

## 2. Неизменяемость (Immutability)

Неизменяемость — это фундаментальное свойство Объектов-значений. Это означает, что после того, как объект создан, его внутреннее состояние (значения атрибутов) не может быть изменено.

**Преимущества неизменяемости:**
-   **Предсказуемость и безопасность:** Поскольку состояние объекта не меняется, его можно безопасно передавать по ссылке между различными частями системы, не опасаясь неожиданных модификаций. Это особенно важно в многопоточных приложениях.
-   **Простота:** Неизменяемые объекты проще для понимания и отладки, так как их состояние фиксировано.
-   **Кэширование:** Неизменяемые объекты хорошо подходят для кэширования.
-   **Использование в качестве ключей словарей:** Если Объект-значение корректно реализует `__hash__`, его можно использовать как ключ в словаре или элемент множества.

Если вам нужно "изменить" Объект-значение, вы на самом деле создаете новый экземпляр с измененными значениями. Например, если у вас есть объект `Money(100, "USD")` и вы хотите добавить к нему `Money(50, "USD")`, результатом будет новый объект `Money(150, "USD")`, а исходный останется неизменным.

## 3. Равенство на основе атрибутов

Объекты-значения сравниваются на основе значений всех своих атрибутов. Два экземпляра считаются равными, если все их соответствующие атрибуты равны. Это называется структурным равенством.

Например, два объекта `Address("ул. Ленина", "1", "Москва")` будут равны, даже если это два разных экземпляра в памяти, потому что все их атрибуты (улица, дом, город) совпадают.

Для этого в Python необходимо корректно переопределить методы `__eq__` (для сравнения) и `__hash__` (чтобы объекты можно было использовать в коллекциях, таких как множества и ключи словарей).

## 4. Отличие от Сущностей (Entities)

Хотя и Сущности, и Объекты-значения являются строительными блоками модели, они служат разным целям:

| Характеристика      | Объект-значение (Value Object)                      | Сущность (Entity)                                  |
| :------------------ | :-------------------------------------------------- | :------------------------------------------------- |
| **Определение**     | Определяется значениями своих атрибутов             | Определяется идентичностью                         |
| **Идентичность**    | Не имеет собственной идентичности                   | Имеет уникальный ID, сохраняющийся со временем    |
| **Сравнение**       | Сравниваются по значениям всех атрибутов (структурно) | Сравниваются по ID                                 |
| **Изменяемость**    | Неизменяемы (immutable)                             | Обычно изменяемы (mutable)                         |
| **Жизненный цикл**  | Обычно не имеет сложного жизненного цикла          | Имеет жизненный цикл (создание, изменение, удаление) |
| **Основная роль**   | Описывает характеристику, меру, атрибут             | Представляет уникальный, отслеживаемый объект      |

**Когда использовать Объект-значение:**
-   Когда вы моделируете концепцию, которая описывается своими атрибутами, и идентичность не важна.
-   Когда вам нужна неизменяемость и безопасная передача данных.
-   Для представления таких вещей, как количество, дата, диапазон, цвет, адрес и т.д.

## 5. Реализация на Python

В Python Объекты-значения удобно реализовывать с использованием `dataclasses` (начиная с Python 3.7), так как они автоматически генерируют методы `__init__`, `__repr__`, `__eq__` и другие на основе атрибутов. Важно установить `frozen=True` для обеспечения неизменяемости.

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True) # frozen=True делает объект неизменяемым
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        # Валидация может быть добавлена здесь
        if self.amount < Decimal("0"):
            raise ValueError("Amount cannot be negative.")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code (e.g., USD).")

    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies.")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Decimal | int) -> 'Money':
        if not isinstance(factor, (Decimal, int)):
            return NotImplemented
        return Money(self.amount * Decimal(factor), self.currency)

# Пример использования
price1 = Money(Decimal("100.00"), "USD")
price2 = Money(Decimal("100.00"), "USD")
price3 = Money(Decimal("50.00"), "USD")
tax = Money(Decimal("10.00"), "USD")

print(f"price1 == price2: {price1 == price2}")  # True, т.к. атрибуты равны
print(f"price1 == price3: {price1 == price3}")  # False

total_price = price1 + tax
print(f"Total price: {total_price}") # Money(amount=Decimal('110.00'), currency='USD')

# Попытка изменить атрибут вызовет ошибку FrozenInstanceError
# price1.amount = Decimal("200.00") # dataclasses.FrozenInstanceError: cannot assign to field 'amount'
```

**Ключевые моменты реализации:**
-   **`@dataclass(frozen=True)`:** Обеспечивает неизменяемость и автоматическую генерацию `__eq__`, `__hash__`, `__repr__` и т.д.
-   **Типизация атрибутов:** Четко определяет типы данных для каждого атрибута.
-   **Валидация в `__post_init__`:** Позволяет проверить корректность значений при создании объекта.
-   **Методы-операции:** Могут быть добавлены методы, которые выполняют операции с Объектом-значением и возвращают новый экземпляр (например, `__add__` для `Money`). Они не изменяют исходный объект.

## 6. Примеры

### Пример 1: `Address`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country: str

    def __post_init__(self):
        if not self.street:
            raise ValueError("Street cannot be empty.")
        if not self.city:
            raise ValueError("City cannot be empty.")
        # ... другие проверки ...

    def formatted_address(self) -> str:
        return f"{self.street}, {self.city}, {self.postal_code}, {self.country}"

# Использование
addr1 = Address(street="123 Main St", city="Anytown", postal_code="12345", country="USA")
addr2 = Address(street="123 Main St", city="Anytown", postal_code="12345", country="USA")
addr3 = Address(street="456 Oak Ave", city="Otherville", postal_code="67890", country="USA")

print(f"addr1 == addr2: {addr1 == addr2}") # True
print(f"addr1 == addr3: {addr1 == addr3}") # False
print(addr1.formatted_address())
```

### Пример 2: `DateRange`

```python
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class DateRange:
    start_date: date
    end_date: date

    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date.")

    def contains(self, d: date) -> bool:
        return self.start_date <= d <= self.end_date

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1

# Использование
vacation = DateRange(date(2024, 7, 20), date(2024, 7, 30))
event_date = date(2024, 7, 25)
another_date = date(2024, 8, 1)

print(f"Vacation duration: {vacation.duration_days} days")
print(f"Event date in vacation: {vacation.contains(event_date)}") # True
print(f"Another date in vacation: {vacation.contains(another_date)}") # False
```

Объекты-значения помогают создавать более выразительные, надежные и понятные доменные модели, инкапсулируя логику и поведение, связанное с определенными значениями или характеристиками.
