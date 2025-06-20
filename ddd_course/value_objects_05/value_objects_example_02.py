"""
Примеры кода для модуля "Объекты-значения (Value Objects)".

Демонстрирует создание и использование Объектов-Значений, подчеркивая
их ключевые характеристики: неизменяемость, сравнение по значению и валидацию.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Money:
    """
    Представляет денежную сумму с валютой.
    Неизменяемый объект, сравнивается по значению.
    """

    amount: float
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Сумма не может быть отрицательной.")
        if (
            not self.currency
            or len(self.currency) != 3
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise ValueError(
                "Код валюты должен состоять из 3 заглавных букв (например, RUB, USD)."
            )

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Нельзя складывать деньги в разных валютах.")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Нельзя вычитать деньги в разных валютах.")
        return Money(self.amount - other.amount, self.currency)


@dataclass(frozen=True)
class Address:
    """
    Представляет почтовый адрес.
    Неизменяемый объект, сравнивается по значению.
    """

    street: str
    city: str
    postal_code: str
    country: str = "Россия"

    def __post_init__(self):
        if not self.street:
            raise ValueError("Улица не может быть пустой.")
        if not self.city:
            raise ValueError("Город не может быть пустым.")
        if (
            not self.postal_code
            or not self.postal_code.isdigit()
            or len(self.postal_code) != 6
        ):
            raise ValueError("Почтовый индекс должен состоять из 6 цифр.")
        if not self.country:
            raise ValueError("Страна не может быть пустой.")

    def __str__(self) -> str:
        return f"{self.postal_code}, {self.country}, г. {self.city}, ул. {self.street}"


@dataclass(frozen=True)
class Color:
    """
    Представляет цвет в формате RGB.
    Неизменяемый объект, сравнивается по значению.
    Компоненты должны быть в диапазоне [0, 255].
    """

    red: int
    green: int
    blue: int

    def __post_init__(self):
        if not (
            0 <= self.red <= 255 and 0 <= self.green <= 255 and 0 <= self.blue <= 255
        ):
            raise ValueError(
                "Значения компонентов RGB должны быть в диапазоне от 0 до 255."
            )

    def to_hex(self) -> str:
        """Возвращает HEX-представление цвета."""
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        """Создает объект Color из HEX-строки."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6 or not all(
            c in "0123456789abcdefABCDEF" for c in hex_color
        ):
            raise ValueError(
                "Некорректный HEX-формат цвета. Ожидается #RRGGBB или RRGGBB."
            )
        return cls(
            red=int(hex_color[0:2], 16),
            green=int(hex_color[2:4], 16),
            blue=int(hex_color[4:6], 16),
        )


@dataclass(frozen=True)
class DateRange:
    """
    Представляет диапазон дат.
    Неизменяемый объект, сравнивается по значению.
    Начальная дата не должна быть позже конечной.
    """

    start_date: date
    end_date: date

    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Начальная дата не может быть позже конечной даты.")

    def __contains__(self, item: date) -> bool:
        if not isinstance(item, date):
            return False
        return self.start_date <= item <= self.end_date

    @property
    def duration_days(self) -> int:
        """Возвращает длительность диапазона в днях."""
        return (self.end_date - self.start_date).days + 1  # Включая обе даты


if __name__ == "__main__":
    print("--- Демонстрация Объектов-Значений ---")

    # Money
    print("\n--- Money ---")
    try:
        price1 = Money(100.50, "RUB")
        price2 = Money(50.25, "RUB")
        price3 = Money(100.50, "RUB")
        price_usd = Money(10.00, "USD")

        print(f"Цена 1: {price1}")
        print(f"Цена 2: {price2}")
        print(f"Цена 1 == Цена 3: {price1 == price3}")
        print(f"Цена 1 == Цена 2: {price1 == price2}")

        total_price = price1 + price2
        print(f"Сумма (price1 + price2): {total_price}")

        # price1.amount = 200 # Ошибка! AttributeError: can't set attribute
        # (frozen=True)
        # price1 + price_usd # Ошибка! ValueError: Нельзя складывать деньги
        # в разных валютах.
        # Money(-10, "RUB") # Ошибка! ValueError: Сумма не может быть отрицательной.
        # Money(10, "RU") # Ошибка! ValueError: Код валюты должен состоять
        # из 3 заглавных букв.
    except (ValueError, AttributeError) as e:
        print(f"Ошибка при работе с Money: {e}")

    # Address
    print("\n--- Address ---")
    try:
        addr1 = Address("Ленина", "Москва", "101000")
        addr2 = Address("Ленина", "Москва", "101000", country="Россия")
        addr3 = Address("Мира", "Санкт-Петербург", "190000")

        print(f"Адрес 1: {addr1}")
        print(f"Адрес 2: {addr2}")
        print(f"Адрес 1 == Адрес 2: {addr1 == addr2}")
        print(f"Адрес 1 == Адрес 3: {addr1 == addr3}")
        # Address("", "Москва", "101000") # Ошибка! ValueError:
        # Улица не может быть пустой.
        # Address("Ленина", "Москва", "10100") # Ошибка! ValueError:
        # Почтовый индекс должен состоять из 6 цифр.
    except (ValueError, AttributeError) as e:
        print(f"Ошибка при работе с Address: {e}")

    # Color
    print("\n--- Color ---")
    try:
        red_color = Color(255, 0, 0)
        green_color = Color.from_hex("#00FF00")
        another_red = Color(255, 0, 0)

        print(f"Красный: {red_color}, HEX: {red_color.to_hex()}")
        print(f"Зеленый (из HEX): {green_color}, HEX: {green_color.to_hex()}")
        print(f"Красный == Другой красный: {red_color == another_red}")
        print(f"Красный == Зеленый: {red_color == green_color}")
        # Color(256, 0, 0) # Ошибка! ValueError: Значения компонентов RGB
        # должны быть в диапазоне от 0 до 255.
        # Color.from_hex("#12345") # Ошибка! ValueError: Некорректный HEX-формат цвета.
    except (ValueError, AttributeError) as e:
        print(f"Ошибка при работе с Color: {e}")

    # DateRange
    print("\n--- DateRange ---")
    try:
        today = date.today()
        tomorrow = date(
            today.year, today.month, today.day + 1 if today.day < 28 else 1
        )  # Упрощенно
        next_week_start = tomorrow
        next_week_end = date(
            next_week_start.year,
            next_week_start.month,
            next_week_start.day + 6 if next_week_start.day < 22 else 28,
        )  # Упрощенно

        range1 = DateRange(today, tomorrow)
        range2 = DateRange(today, tomorrow)
        range3 = DateRange(next_week_start, next_week_end)

        print(
            f"Диапазон 1: с {range1.start_date} по {range1.end_date}, "
            f"длительность: {range1.duration_days} дней"
        )
        print(f"Диапазон 1 == Диапазон 2: {range1 == range2}")
        print(f"Сегодня ({today}) в Диапазоне 1: {today in range1}")
        print(f"Завтра ({tomorrow}) в Диапазоне 1: {tomorrow in range1}")
        # DateRange(tomorrow, today) # Ошибка! ValueError: Начальная дата не
        # может быть позже конечной даты.
    except (ValueError, AttributeError) as e:
        print(f"Ошибка при работе с DateRange: {e}")
