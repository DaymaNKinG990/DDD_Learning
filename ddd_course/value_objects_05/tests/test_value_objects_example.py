"""
Тесты для примеров Объектов-Значений из value_objects_example_02.py.
"""

from datetime import date

import pytest

from ddd_course.value_objects_05.value_objects_example_02 import (
    Address,
    Color,
    DateRange,
    Money,
)


class TestMoney:
    """Тесты для объекта-значения Money."""

    def test_money_creation_success(self):
        money = Money(100.0, "RUB")
        assert money.amount == 100.0
        assert money.currency == "RUB"
        assert str(money) == "100.00 RUB"

    def test_money_creation_invalid_amount(self):
        with pytest.raises(ValueError, match="Сумма не может быть отрицательной"):
            Money(-50.0, "USD")

    def test_money_creation_invalid_currency(self):
        with pytest.raises(
            ValueError, match="Код валюты должен состоять из 3 заглавных букв"
        ):
            Money(100.0, "US")
        with pytest.raises(
            ValueError, match="Код валюты должен состоять из 3 заглавных букв"
        ):
            Money(100.0, "rub")
        with pytest.raises(
            ValueError, match="Код валюты должен состоять из 3 заглавных букв"
        ):
            Money(100.0, "US1")

    def test_money_is_immutable(self):
        money = Money(100.0, "RUB")
        with pytest.raises(
            AttributeError
        ):  # dataclasses.FrozenInstanceError is a subclass of AttributeError
            money.amount = 200.0
        with pytest.raises(AttributeError):
            money.currency = "USD"

    def test_money_equality(self):
        money_rub1 = Money(100.0, "RUB")
        money_rub2 = Money(100.0, "RUB")
        money_rub3 = Money(200.0, "RUB")
        money_usd = Money(100.0, "USD")

        assert money_rub1 == money_rub2
        assert money_rub1 != money_rub3
        assert money_rub1 != money_usd
        assert money_rub1 != "100.0 RUB"  # Сравнение с другим типом

    def test_money_addition(self):
        money_rub1 = Money(100.0, "RUB")
        money_rub2 = Money(50.0, "RUB")
        result = money_rub1 + money_rub2
        assert result == Money(150.0, "RUB")

    def test_money_addition_different_currencies(self):
        money_rub = Money(100.0, "RUB")
        money_usd = Money(50.0, "USD")
        with pytest.raises(
            ValueError, match="Нельзя складывать деньги в разных валютах"
        ):
            _ = money_rub + money_usd

    def test_money_subtraction(self):
        money_rub1 = Money(100.0, "RUB")
        money_rub2 = Money(50.0, "RUB")
        result = money_rub1 - money_rub2
        assert result == Money(50.0, "RUB")

    def test_money_subtraction_different_currencies(self):
        money_rub = Money(100.0, "RUB")
        money_usd = Money(50.0, "USD")
        with pytest.raises(ValueError, match="Нельзя вычитать деньги в разных валютах"):
            _ = money_rub - money_usd


class TestAddress:
    """Тесты для объекта-значения Address."""

    def test_address_creation_success(self):
        addr = Address("Ленина", "Москва", "123456", "Россия")
        assert addr.street == "Ленина"
        assert addr.city == "Москва"
        assert addr.postal_code == "123456"
        assert addr.country == "Россия"
        assert str(addr) == "123456, Россия, г. Москва, ул. Ленина"

    def test_address_creation_default_country(self):
        addr = Address("Мира", "Казань", "654321")
        assert addr.country == "Россия"
        assert str(addr) == "654321, Россия, г. Казань, ул. Мира"

    @pytest.mark.parametrize(
        "street, city, postal_code, country, error_msg",
        [
            ("", "Москва", "123456", "Россия", "Улица не может быть пустой"),
            ("Ленина", "", "123456", "Россия", "Город не может быть пустым"),
            (
                "Ленина",
                "Москва",
                "12345",
                "Россия",
                "Почтовый индекс должен состоять из 6 цифр",
            ),
            (
                "Ленина",
                "Москва",
                "12345A",
                "Россия",
                "Почтовый индекс должен состоять из 6 цифр",
            ),
            (
                "Ленина",
                "Москва",
                "1234567",
                "Россия",
                "Почтовый индекс должен состоять из 6 цифр",
            ),
            ("Ленина", "Москва", "123456", "", "Страна не может быть пустой"),
        ],
    )
    def test_address_creation_invalid_data(
        self, street, city, postal_code, country, error_msg
    ):
        with pytest.raises(ValueError, match=error_msg):
            Address(street, city, postal_code, country)

    def test_address_is_immutable(self):
        addr = Address("Ленина", "Москва", "123456")
        with pytest.raises(AttributeError):
            addr.street = "Мира"

    def test_address_equality(self):
        addr1 = Address("Ленина", "Москва", "123456", "Россия")
        addr2 = Address("Ленина", "Москва", "123456", "Россия")
        addr3 = Address("Мира", "Москва", "123456", "Россия")
        addr4 = Address("Ленина", "Москва", "123456", "Беларусь")

        assert addr1 == addr2
        assert addr1 != addr3
        assert addr1 != addr4


class TestColor:
    """Тесты для объекта-значения Color."""

    def test_color_creation_success(self):
        color = Color(255, 128, 0)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 0

    @pytest.mark.parametrize(
        "r, g, b",
        [
            (-1, 0, 0),
            (0, -1, 0),
            (0, 0, -1),
            (256, 0, 0),
            (0, 256, 0),
            (0, 0, 256),
        ],
    )
    def test_color_creation_invalid_rgb_value(self, r, g, b):
        with pytest.raises(
            ValueError,
            match="Значения компонентов RGB должны быть в диапазоне от 0 до 255",
        ):
            Color(r, g, b)

    def test_color_is_immutable(self):
        color = Color(10, 20, 30)
        with pytest.raises(AttributeError):
            color.red = 40

    def test_color_equality(self):
        color1 = Color(255, 0, 0)
        color2 = Color(255, 0, 0)
        color3 = Color(0, 255, 0)

        assert color1 == color2
        assert color1 != color3

    def test_color_to_hex(self):
        assert Color(255, 0, 0).to_hex() == "#ff0000"
        assert Color(0, 255, 0).to_hex() == "#00ff00"
        assert Color(0, 0, 255).to_hex() == "#0000ff"
        assert Color(16, 32, 48).to_hex() == "#102030"  # 10, 20, 30 hex
        assert Color(12, 123, 212).to_hex() == "#0c7bd4"

    def test_color_from_hex_success(self):
        assert Color.from_hex("#FF0000") == Color(255, 0, 0)
        assert Color.from_hex("00FF00") == Color(0, 255, 0)
        assert Color.from_hex("0c7Bd4") == Color(12, 123, 212)  # case-insensitive

    @pytest.mark.parametrize(
        "hex_str", ["#12345", "12345", "#1234567", "#GG0000", "#AFK123"]
    )
    def test_color_from_hex_invalid(self, hex_str):
        with pytest.raises(ValueError, match="Некорректный HEX-формат цвета"):
            Color.from_hex(hex_str)


class TestDateRange:
    """Тесты для объекта-значения DateRange."""

    def test_daterange_creation_success(self):
        start = date(2023, 1, 1)
        end = date(2023, 1, 10)
        dr = DateRange(start, end)
        assert dr.start_date == start
        assert dr.end_date == end

    def test_daterange_creation_start_equals_end(self):
        dt = date(2023, 5, 5)
        dr = DateRange(dt, dt)
        assert dr.start_date == dt
        assert dr.end_date == dt

    def test_daterange_creation_start_after_end(self):
        start = date(2023, 1, 10)
        end = date(2023, 1, 1)
        with pytest.raises(
            ValueError, match="Начальная дата не может быть позже конечной даты"
        ):
            DateRange(start, end)

    def test_daterange_is_immutable(self):
        dr = DateRange(date(2023, 1, 1), date(2023, 1, 10))
        with pytest.raises(AttributeError):
            dr.start_date = date(2023, 1, 5)

    def test_daterange_equality(self):
        dr1 = DateRange(date(2023, 1, 1), date(2023, 1, 10))
        dr2 = DateRange(date(2023, 1, 1), date(2023, 1, 10))
        dr3 = DateRange(date(2023, 1, 1), date(2023, 1, 11))
        dr4 = DateRange(date(2023, 1, 2), date(2023, 1, 10))

        assert dr1 == dr2
        assert dr1 != dr3
        assert dr1 != dr4

    def test_daterange_contains(self):
        start = date(2023, 6, 15)
        end = date(2023, 6, 20)
        dr = DateRange(start, end)

        assert date(2023, 6, 15) in dr
        assert date(2023, 6, 18) in dr
        assert date(2023, 6, 20) in dr
        assert date(2023, 6, 14) not in dr
        assert date(2023, 6, 21) not in dr
        assert "2023-06-15" not in dr  # Check with wrong type

    def test_daterange_duration_days(self):
        assert DateRange(date(2023, 1, 1), date(2023, 1, 1)).duration_days == 1
        assert DateRange(date(2023, 1, 1), date(2023, 1, 10)).duration_days == 10
        assert (
            DateRange(date(2023, 2, 25), date(2023, 3, 2)).duration_days == 6
        )  # 25,26,27,28,1,2 (for non-leap year)


def test_placeholder():
    assert True
