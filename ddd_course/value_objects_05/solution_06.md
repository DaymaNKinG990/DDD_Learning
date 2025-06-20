# Решение упражнения по модулю "Объекты-значения (Value Objects)"

## Задание: Разработка Объекта-значения `Color` и `ColorPalette`

Ниже представлен пример реализации классов `Color` и `ColorPalette` на Python в соответствии с требованиями упражнения.

### Код решения

```python
from __future__ import annotations

import re
from typing import Tuple, Type, TypeVar

_TColor = TypeVar("_TColor", bound="Color")
_TColorPalette = TypeVar("_TColorPalette", bound="ColorPalette")


class Color:
    """
    Объект-значение, представляющий цвет в формате RGB.

    Атрибуты:
        red (int): Компонента красного цвета (0-255).
        green (int): Компонента зеленого цвета (0-255).
        blue (int): Компонента синего цвета (0-255).
    """

    def __init__(self, red: int, green: int, blue: int):
        """
        Инициализирует объект Color.

        Args:
            red: Значение красного компонента (0-255).
            green: Значение зеленого компонента (0-255).
            blue: Значение синего компонента (0-255).

        Raises:
            ValueError: Если значения компонентов выходят за пределы диапазона 0-255.
        """
        for component_name, value in [("red", red), ("green", green), ("blue", blue)]:
            if not (0 <= value <= 255):
                raise ValueError(
                    f"{component_name.capitalize()} component must be "
                    f"between 0 and 255, got {value}"
                )
        self._red = red
        self._green = green
        self._blue = blue

    @property
    def red(self) -> int:
        return self._red

    @property
    def green(self) -> int:
        return self._green

    @property
    def blue(self) -> int:
        return self._blue

    def to_hex(self) -> str:
        """
        Возвращает HEX-представление цвета.

        Returns:
            Строка HEX-кода цвета (например, "#FF00AA").
        """
        return f"#{self._red:02X}{self._green:02X}{self._blue:02X}"

    @classmethod
    def from_hex(cls: Type[_TColor], hex_string: str) -> _TColor:
        """
        Создает объект Color из HEX-строки.

        Args:
            hex_string: Строка HEX-кода (например, "#FF00AA" или "FF00AA").

        Returns:
            Экземпляр Color.

        Raises:
            ValueError: Если HEX-строка имеет неверный формат.
        """
        hex_string = hex_string.lstrip("#")
        if not re.fullmatch(r"[0-9a-fA-F]{6}", hex_string):
            raise ValueError(
                f"Invalid HEX string format: '{hex_string}'. "
                f"Must be 6 hex characters."
            )
        return cls(
            int(hex_string[0:2], 16),
            int(hex_string[2:4], 16),
            int(hex_string[4:6], 16),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return (
            self._red == other._red
            and self._green == other._green
            and self._blue == other._blue
        )

    def __hash__(self) -> int:
        return hash((self._red, self._green, self._blue))

    def __repr__(self) -> str:
        return f"Color(red={self._red}, green={self._green}, blue={self._blue})"


class ColorPalette:
    """
    Объект-значение, представляющий именованную палитру цветов.

    Атрибуты:
        name (str): Название палитры.
        colors (Tuple[Color, ...]): Кортеж цветов, входящих в палитру.
    """

    def __init__(self, name: str, colors: Tuple[Color, ...]):
        """
        Инициализирует объект ColorPalette.

        Args:
            name: Название палитры.
            colors: Кортеж объектов Color.

        Raises:
            ValueError: Если имя пустое или кортеж цветов пуст,
                        или содержит не Color объекты.
        """
        if not name:
            raise ValueError("Palette name cannot be empty.")
        if not colors:
            raise ValueError("ColorPalette must contain at least one color.")
        if not all(isinstance(color, Color) for color in colors):
            raise ValueError("All items in colors tuple must be Color objects.")

        self._name = name
        self._colors = colors  # Кортеж уже неизменяем

    @property
    def name(self) -> str:
        return self._name

    @property
    def colors(self) -> Tuple[Color, ...]:
        return self._colors

    def add_color(self: _TColorPalette, color: Color) -> _TColorPalette:
        """
        Создает новую палитру, добавляя указанный цвет к существующим.

        Args:
            color: Объект Color для добавления.

        Returns:
            Новый экземпляр ColorPalette с добавленным цветом.
        """
        if not isinstance(color, Color):
            raise TypeError("Can only add Color objects to the palette.")
        # Создаем новый кортеж, чтобы сохранить неизменяемость
        new_colors = self._colors + (color,)
        return self.__class__(name=self._name, colors=new_colors)

    def get_colors_hex(self) -> Tuple[str, ...]:
        """
        Возвращает кортеж HEX-представлений всех цветов в палитре.

        Returns:
            Кортеж строк с HEX-кодами цветов.
        """
        return tuple(color.to_hex() for color in self._colors)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ColorPalette):
            return NotImplemented
        return self._name == other._name and self._colors == other._colors

    def __hash__(self) -> int:
        return hash((self._name, self._colors))

    def __repr__(self) -> str:
        return f"ColorPalette(name='{self._name}', colors={self._colors})"


# Примеры использования:
if __name__ == "__main__":
    # --- Color ---
    print("--- Color Examples ---")
    try:
        red_color = Color(255, 0, 0)
        print(f"Red color: {red_color}, HEX: {red_color.to_hex()}")

        blue_color = Color.from_hex("#0000FF")
        print(f"Blue color from HEX: {blue_color}")

        another_red = Color(255, 0, 0)
        print(f"red_color == another_red: {red_color == another_red}")  # True

        color_set = {red_color, blue_color, another_red}
        print(f"Color set: {color_set}") # Должно быть два уникальных цвета

        # Пример неверного значения
        # invalid_color = Color(300, 0, 0) # Вызовет ValueError
    except ValueError as e:
        print(f"Error creating color: {e}")
    except TypeError as e:
        print(f"Type error with color: {e}")


    # --- ColorPalette ---
    print("\n--- ColorPalette Examples ---")
    try:
        primary_colors = (
            Color(255, 0, 0),    # Red
            Color(0, 255, 0),    # Green
            Color(0, 0, 255),    # Blue
        )
        primary_palette = ColorPalette("Primary Colors", primary_colors)
        print(f"Primary Palette: {primary_palette}")
        print(f"Primary Palette HEX: {primary_palette.get_colors_hex()}")

        # Добавление цвета (создание новой палитры)
        yellow_color = Color(255, 255, 0)
        extended_palette = primary_palette.add_color(yellow_color)
        print(f"Extended Palette: {extended_palette}")
        print(f"Original Primary Palette (unchanged): {primary_palette}")

        # Сравнение палитр
        same_primary_palette = ColorPalette("Primary Colors", primary_colors)
        print(f"primary_palette == same_primary_palette: {primary_palette == same_primary_palette}") # True

        # Использование в качестве ключей словаря
        palettes_info = {
            primary_palette: "Standard primary colors",
            extended_palette: "Primary colors plus yellow"
        }
        print(f"Info for primary_palette: {palettes_info[same_primary_palette]}")

        # Пример неверного создания
        # empty_palette = ColorPalette("Empty", ()) # Вызовет ValueError
        # mixed_palette = ColorPalette("Mixed", (Color(0,0,0), "not a color")) # Вызовет ValueError

    except ValueError as e:
        print(f"Error with palette: {e}")
    except TypeError as e:
        print(f"Type error with palette: {e}")
