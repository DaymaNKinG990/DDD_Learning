# Практическое задание: Разработка Ubiquitous Language

В этом задании вы примените принципы Ubiquitous Language на практике, разработав модель для системы управления задачами (Task Management System).

## Контекст

Вы разрабатываете систему управления задачами для команды разработчиков. В системе будут следующие основные концепции:

1. **Задача (Task)** - единица работы, которую нужно выполнить
2. **Исполнитель (Assignee)** - член команды, ответственный за выполнение задачи
3. **Спринт (Sprint)** - временной интервал (обычно 1-4 недели), в течение которого выполняется набор задач
4. **Доска задач (Board)** - визуальное представление задач, сгруппированных по статусам
5. **Комментарий (Comment)** - примечание к задаче

## Задание 1: Разработка глоссария

Создайте глоссарий терминов для системы управления задачами. Для каждого термина укажите:

1. Название термина
2. Определение
3. Пример использования
4. Связанные термины

Пример:

| Термин | Определение | Пример | Связанные термины |
|--------|------------|--------|------------------|
| Задача | Единица работы, которую нужно выполнить | "Исправить баг с авторизацией" | Исполнитель, Спринт, Статус |

## Задание 2: Моделирование на Python

Напишите классы на Python, которые отражают предметную область системы управления задачами. Убедитесь, что:

1. Имена классов, методов и переменных соответствуют Ubiquitous Language
2. Код хорошо документирован с использованием docstrings
3. Учтены основные бизнес-правила (например, задача не может быть без исполнителя)

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

# Ваш код здесь
# 1. Определите необходимые перечисления (например, статусы задач)
# 2. Создайте классы для сущностей и объектов-значений
# 3. Реализуйте основные методы
```

## Задание 3: Реализация бизнес-логики

Реализуйте следующие сценарии:

1. Создание новой задачи
2. Назначение исполнителя на задачу
3. Перемещение задачи по доске (изменение статуса)
4. Добавление комментария к задаче
5. Завершение спринта и перенос незавершённых задач в следующий спринт

## Задание 4: Тестирование

Напишите unit-тесты для проверки корректности работы бизнес-логики. Убедитесь, что:

1. Тесты используют термины из Ubiquitous Language
2. Проверяются граничные случаи и ошибочные сценарии
3. Тесты документированы и легко читаемы

## Критерии оценки

1. **Полнота глоссария** - все ключевые термины предметной области учтены
2. **Каство кода** - соответствие PEP 8, наличие type hints, документация
3. **Соответствие Ubiquitous Language** - имена в коде отражают термины предметной области
4. **Покрытие тестами** - все основные сценарии протестированы
5. **Обработка ошибок** - корректная обработка ошибочных ситуаций

## Дополнительное задание (по желанию)

1. Реализуйте возможность прикрепления файлов к задачам
2. Добавьте систему уведомлений о изменениях в задачах
3. Реализуйте историю изменений для задач
4. Создайте REST API для работы с системой

## Подсказки

1. Начните с разработки глоссария и обсудите его с "бизнес-экспертом" (преподавателем или коллегой)
2. Используйте принципы DDD при проектировании модели
3. Обращайте внимание на инварианты (например, задача не может быть завершена без исполнителя)
4. Документируйте принимаемые решения

Удачи в выполнении задания!
