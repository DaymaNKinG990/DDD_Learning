# Сквозной пример: Система управления курсами

Этот проект представляет собой сквозной пример небольшого приложения, разработанного с использованием принципов Domain-Driven Design (DDD).

## Цель

Показать, как различные строительные блоки DDD (Сущности, Объекты-значения, Агрегаты, Репозитории, Сервисы приложения, Доменные события) работают вместе в рамках единого приложения.

## Структура директорий

- **/domain**: Содержит основную бизнес-логику, агрегаты, сущности, объекты-значения и доменные события.
- **/application**: Содержит сервисы приложения, которые координируют выполнение бизнес-операций.
- **/infrastructure**: Содержит реализации интерфейсов, определенных в домене (например, репозитории), и другую техническую инфраструктуру.
- **/tests**: Содержит тесты для всех слоев приложения.
