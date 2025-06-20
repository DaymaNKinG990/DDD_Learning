# Упражнение по модулю "Объекты-значения (Value Objects)"

## Задание: Разработка Объекта-значения `Color` и `ColorPalette`

В этом упражнении вам предстоит разработать два Объекта-значения: `Color` для представления цвета в формате RGB и `ColorPalette` для представления набора из нескольких цветов.

### Часть 1: Объект-значение `Color`

Разработайте Объект-значение `Color`.

**Требования к `Color`:**
1.  **Атрибуты:**
    *   `red`: целое число, значение от 0 до 255.
    *   `green`: целое число, значение от 0 до 255.
    *   `blue`: целое число, значение от 0 до 255.
2.  **Неизменяемость (Immutability):**
    *   После создания объекта `Color` его атрибуты (`red`, `green`, `blue`) не должны изменяться.
3.  **Самовалидация (Self-validation):**
    *   При создании объекта `Color` (в конструкторе `__init__`) должна выполняться проверка, что значения `red`, `green` и `blue` находятся в допустимом диапазоне (0-255). В случае некорректных значений должно выбрасываться исключение `ValueError`.
4.  **Сравнение по значению:**
    *   Реализуйте методы `__eq__` и `__hash__` так, чтобы два объекта `Color` считались равными, если их значения `red`, `green` и `blue` совпадают. Это также позволит использовать объекты `Color` в хешируемых коллекциях (например, `set` или в качестве ключей `dict`).
5.  **Представление:**
    *   Реализуйте метод `__repr__` для удобного строкового представления объекта (например, `Color(r=255, g=0, b=0)`).
6.  **Фабричный метод для HEX (необязательно, но рекомендуется):**
    *   Реализуйте статический или классовый метод `from_hex(hex_string: str) -> Color`, который принимает строку HEX-кода цвета (например, `#FF0000` или `FF0000`) и возвращает экземпляр `Color`. Должна быть проверка корректности HEX-строки.
7.  **Метод для получения HEX-представления:**
    *   Реализуйте метод `to_hex() -> str`, который возвращает HEX-представление цвета (например, `#FF0000`).

### Часть 2: Объект-значение `ColorPalette`

Разработайте Объект-значение `ColorPalette`, который представляет собой фиксированный набор цветов.

**Требования к `ColorPalette`:**
1.  **Атрибуты:**
    *   `name`: строка, название палитры (например, "Основные цвета", "Пастельные тона").
    *   `colors`: кортеж (tuple) объектов `Color`. Использование кортежа подчеркивает неизменяемость набора цветов в палитре.
2.  **Неизменяемость (Immutability):**
    *   Палитра должна быть неизменяемой после создания. Название и набор цветов не должны меняться.
3.  **Самовалидация (Self-validation):**
    *   При создании `ColorPalette` убедитесь, что имя не пустое и список `colors` содержит только объекты типа `Color`. Можно также добавить ограничение на минимальное/максимальное количество цветов в палитре, если это имеет смысл для вашего домена (например, палитра должна содержать хотя бы один цвет).
4.  **Сравнение по значению:**
    *   Реализуйте методы `__eq__` и `__hash__` для `ColorPalette`. Две палитры считаются равными, если у них совпадают названия и наборы цветов.
5.  **Представление:**
    *   Реализуйте метод `__repr__` (например, `ColorPalette(name='Основные цвета', colors=(Color(r=255, g=0, b=0), ...))`).
6.  **Полезные методы (необязательно):**
    *   Метод `add_color(self, color: Color) -> 'ColorPalette'` – возвращает *новый* экземпляр `ColorPalette` с добавленным цветом (демонстрируя работу с неизменяемыми объектами).
    *   Метод `get_colors_hex() -> tuple[str, ...]` – возвращает кортеж HEX-представлений всех цветов в палитре.

### Что нужно предоставить:
-   Код на Python с реализацией классов `Color` и `ColorPalette`.
-   Краткие примеры использования ваших классов, демонстрирующие их основные возможности (создание, сравнение, вызов методов).

### Критерии оценки:
-   Корректность реализации всех требований.
-   Соблюдение принципа неизменяемости.
-   Наличие и корректность валидации данных.
-   Правильная реализация методов `__eq__` и `__hash__`.
-   Читаемость и чистота кода (соответствие PEP 8, наличие type hints и docstrings будет плюсом).

Удачи!
