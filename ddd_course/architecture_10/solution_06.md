# Решение упражнения: Проектирование системы "Мини-Блог"

Это решение демонстрирует проектирование системы "Мини-Блог" с использованием Шестиугольной архитектуры и CQRS.

## Часть 1: Шестиугольная Архитектура

### 1. Доменное Ядро (Domain Core)

**Агрегаты:**

*   **`Author` (Автор):**
    *   `id`: `AuthorId` (VO) - Идентификатор автора.
    *   `name`: `string` - Имя автора.
    *   `email`: `Email` (VO) - Email автора (с валидацией).
    *   `password_hash`: `string` - Хеш пароля (упрощенно).
    *   *Поведение:*
        *   `register(name, email, password)`: Создает нового автора.
        *   `change_name(new_name)`
        *   `change_email(new_email)`

*   **`Post` (Пост):**
    *   `id`: `PostId` (VO) - Идентификатор поста.
    *   `author_id`: `AuthorId` (VO) - Ссылка на автора.
    *   `title`: `string` - Заголовок поста.
    *   `content`: `string` - Содержимое поста.
    *   `created_at`: `datetime` - Дата создания.
    *   `updated_at`: `datetime` - Дата последнего обновления.
    *   `status`: `PostStatus` (Enum: DRAFT, PUBLISHED, ARCHIVED) - Статус поста (для примера, можно расширить).
    *   *Поведение:*
        *   `create(author_id, title, content)`: Создает новый пост.
        *   `edit(title, content)`: Редактирует пост, обновляет `updated_at`.
        *   `publish()`: Публикует пост.
        *   `archive()`: Архивирует пост.

**Объекты-Значения (Value Objects):**

*   `AuthorId`: Уникальный идентификатор автора (например, UUID).
*   `PostId`: Уникальный идентификатор поста (например, UUID).
*   `Email`: Адрес электронной почты с валидацией формата.

**Доменные Сервисы:**

*   В данном простом примере явные доменные сервисы могут не понадобиться, так как основная логика инкапсулирована в агрегатах. Если бы была сложная логика координации между несколькими агрегатами (например, проверка уникальности заголовка поста в рамках всех постов автора перед созданием), мог бы появиться `PostUniquenessValidator` доменный сервис.

**Основные бизнес-правила:**

*   Автор должен иметь уникальный email.
*   Заголовок поста не может быть пустым.
*   Содержимое поста не может быть пустым.
*   Редактировать и удалять пост может только его автор (проверка на уровне Сервиса Приложения или входящего порта).
*   При редактировании поста обновляется `updated_at`.

### 2. Порты (Ports)

**Входящие порты (Driving/Input Ports - Application Services Interfaces):**

Определяют контракты для сценариев использования системы.

*   `IAuthorRegistrationService`:
    *   `register_author(name: str, email: str, password: str) -> AuthorDTO`
*   `IPostManagementService`:
    *   `create_post(author_id: str, title: str, content: str) -> PostDTO`
    *   `edit_post(post_id: str, author_id: str, title: str, content: str) -> PostDTO`
    *   `delete_post(post_id: str, author_id: str) -> None`
    *   `publish_post(post_id: str, author_id: str) -> PostDTO`
    *   `archive_post(post_id: str, author_id: str) -> PostDTO`

*(Примечание: DTO (Data Transfer Objects) будут определены ниже, они используются для передачи данных через границы слоев)*

**Исходящие порты (Driven/Output Ports - Repository Interfaces, etc.):**

Определяют контракты для взаимодействия с инфраструктурой.

*   `IAuthorRepository`:
    *   `save(author: Author) -> None`
    *   `find_by_id(author_id: AuthorId) -> Optional[Author]`
    *   `find_by_email(email: Email) -> Optional[Author]`
*   `IPostRepository`:
    *   `save(post: Post) -> None`
    *   `find_by_id(post_id: PostId) -> Optional[Post]`
    *   `delete(post_id: PostId) -> None`
    *   `find_all_by_author_id(author_id: AuthorId) -> List[Post]` (Может быть частью read-модели, но для простоты здесь)

### 3. Адаптеры (Adapters)

**Входящие адаптеры (Driving/Input Adapters):**

Реализуют взаимодействие с внешним миром, вызывая входящие порты (Сервисы Приложения).

*   **REST API Адаптер (например, с использованием FastAPI/Flask):**
    *   `AuthorsController`:
        *   `POST /authors` -> вызывает `IAuthorRegistrationService.register_author`
    *   `PostsController`:
        *   `POST /posts` -> вызывает `IPostManagementService.create_post`
        *   `PUT /posts/{post_id}` -> вызывает `IPostManagementService.edit_post`
        *   `DELETE /posts/{post_id}` -> вызывает `IPostManagementService.delete_post`
        *   `POST /posts/{post_id}/publish` -> вызывает `IPostManagementService.publish_post`
*   **CLI Адаптер:**
    *   Команды типа `blog-cli register-author --name "..." --email "..."`
    *   Команды типа `blog-cli create-post --author-id "..." --title "..."`

**Исходящие адаптеры (Driven/Output Adapters):**

Конкретные реализации исходящих портов.

*   **Адаптеры Репозиториев:**
    *   `SQLAlchemyAuthorRepository(IAuthorRepository)`: Реализация для PostgreSQL/MySQL с использованием SQLAlchemy.
    *   `SQLAlchemyPostRepository(IPostRepository)`
    *   `InMemoryAuthorRepository(IAuthorRepository)`: In-memory реализация для тестов.
    *   `InMemoryPostRepository(IPostRepository)`
*   **Адаптеры для внешних сервисов (если бы были):**
    *   `EmailNotificationAdapter(INotificationService)`: Для отправки email (например, после регистрации).

### 4. Схематичная диаграмма Шестиугольной Архитектуры

```
+--------------------------------------------------------------------------+
| Внешний мир (Пользователи, Другие системы)                               |
+--------------------------------------------------------------------------+
       |                                      ^
       | (HTTP, CLI, ...)                     | (События, Уведомления)
       v                                      |
+-----------------------+            +------------------------+
| Входящие Адаптеры     |            | Исходящие Адаптеры     |
| (REST Controllers,    |            | (SQLAlchemy Repos,     |
|  CLI Commands)        |            |  Email Service Impl)   |
+-----------------------+            +------------------------+
       |      ^                                |      ^
       |      | (Вызовы методов)               |      | (Вызовы методов)
       v      |                                v      |
+--------------------------------------------------------------------------+
| Порты (Интерфейсы)                                                       |
|--------------------------------------------------------------------------|
| Входящие Порты (Application Service Interfaces)                          |
|   - IAuthorRegistrationService                                           |
|   - IPostManagementService                                               |
|--------------------------------------------------------------------------|
| Исходящие Порты (Repository Interfaces, Notification Service Interface)  |
|   - IAuthorRepository                                                    |
|   - IPostRepository                                                      |
+--------------------------------------------------------------------------+
       |      ^                                |      ^
       |      | (Реализация интерфейсов)       |      | (Реализация интерфейсов)
       v      |                                v      |
+--------------------------------------------------------------------------+
| Ядро Приложения (Application Core)                                       |
|--------------------------------------------------------------------------|
| Сервисы Приложения (Application Services)                                |
|   - AuthorRegistrationService (реализует IAuthorRegistrationService)     |
|   - PostManagementService (реализует IPostManagementService)             |
|       (используют Доменные Объекты и Репозитории через порты)            |
|--------------------------------------------------------------------------|
| Доменное Ядро (Domain Core)                                              |
|   - Агрегаты: Author, Post                                               |
|   - Объекты-Значения: AuthorId, PostId, Email                            |
|   - Доменные Сервисы (если есть)                                         |
|   - Бизнес-логика, инварианты                                            |
+--------------------------------------------------------------------------+
```
*Стрелки показывают направление зависимостей: внешние слои зависят от внутренних.*

## Часть 2: Применение CQRS

### 1. Разделение на Команды и Запросы

**Команды (Commands - изменяют состояние):**

*   `RegisterAuthorCommand(name, email, password)`
*   `CreatePostCommand(author_id, title, content)`
*   `EditPostCommand(post_id, author_id, title, content)`
*   `DeletePostCommand(post_id, author_id)`
*   `PublishPostCommand(post_id, author_id)`
*   `ArchivePostCommand(post_id, author_id)`

**Обработчики Команд (Command Handlers):**

Это, по сути, будут методы Сервисов Приложения из Шестиугольной архитектуры, но с явным фокусом на обработку команды.

*   `AuthorRegistrationService.handle_register_author(command: RegisterAuthorCommand)`
*   `PostManagementService.handle_create_post(command: CreatePostCommand)`
*   ... и так далее.

**Запросы (Queries - читают состояние, не изменяя его):**

*   `GetAuthorByIdQuery(author_id)`
*   `GetPostByIdQuery(post_id)`
*   `GetAllPostsQuery(page, per_page, author_id_filter=None)`
*   `GetPostsByAuthorQuery(author_id, page, per_page)`

**Обработчики Запросов (Query Handlers) / Read Services:**

*   `AuthorQueryService.get_author_by_id(query: GetAuthorByIdQuery) -> Optional[AuthorDetailsDTO]`
*   `PostQueryService.get_post_by_id(query: GetPostByIdQuery) -> Optional[PostDetailsDTO]`
*   `PostQueryService.get_all_posts(query: GetAllPostsQuery) -> PaginatedResult[PostSummaryDTO]`

### 2. Модели для Команд и Запросов

**DTO (Data Transfer Objects):**

Для передачи данных между слоями и для представления результатов запросов.

*   `AuthorDTO(id, name, email)`
*   `PostDTO(id, author_id, title, content, created_at, updated_at, status)`
*   `AuthorDetailsDTO(id, name, email, registration_date)` (может включать больше деталей для чтения)
*   `PostSummaryDTO(id, title, author_name, created_at, preview_content)` (для списков)
*   `PostDetailsDTO(id, title, content, author_name, author_email, created_at, updated_at, status)` (для полного просмотра поста)
*   `PaginatedResult[T](items: List[T], total_items: int, page: int, per_page: int)`

**Командная сторона (Write Side):**

*   **Агрегаты:** `Author`, `Post` (как определены в Части 1). Они содержат всю логику изменения состояния.
*   **Репозитории (Write):** `IAuthorRepository`, `IPostRepository` (как определены в Части 1). Они отвечают за сохранение и загрузку агрегатов для выполнения команд.
    *   `SQLAlchemyAuthorWriteRepository(IAuthorRepository)`
    *   `SQLAlchemyPostWriteRepository(IPostRepository)`

**Запросная сторона (Read Side):**

*   **Read Models (Модели для чтения):**
    *   Это могут быть специализированные DTO (`PostSummaryDTO`, `PostDetailsDTO`) или даже отдельные таблицы/представления в базе данных, оптимизированные для чтения.
    *   Например, `PostSummaryDTO` может быть результатом JOIN таблиц `posts` и `authors` для быстрого получения имени автора.
*   **Механизмы обновления Read Models:**
    1.  **Прямое обновление при сохранении агрегата:** После успешного выполнения команды и сохранения агрегата, Сервис Приложения (или обработчик команды) может также обновить соответствующую Read Model. Это просто, но может замедлить запись.
    2.  **Через Доменные События:**
        *   Агрегат при изменении публикует событие (например, `PostCreatedEvent`, `PostEditedEvent`).
        *   Подписчики на эти события (Event Handlers) обновляют Read Models. Это обеспечивает лучшую развязку, но добавляет асинхронность и сложность управления транзакциями (если Read Model в той же БД).
    3.  **Периодическая синхронизация/ETL:** Для сложных Read Models или отдельных баз данных для чтения, данные могут периодически извлекаться из Write-базы и трансформироваться. Менее актуально для данного простого примера.
    *   *Для "Мини-Блога" можно начать с прямого обновления или использования доменных событий для обновления DTO-подобных структур, хранимых, например, в NoSQL базе данных (Redis, Elasticsearch) для быстрого чтения, или денормализованных таблиц в SQL.*
*   **Репозитории/Сервисы для чтения (Read):**
    *   `IPostReadRepository` (или `IPostQueryService`):
        *   `get_details_by_id(post_id) -> Optional[PostDetailsDTO]`
        *   `get_all_summaries(page, per_page) -> PaginatedResult[PostSummaryDTO]`
    *   Пример реализации: `SQLPostReadRepository` будет выполнять оптимизированные SQL-запросы (возможно, с JOIN'ами) напрямую в DTO, минуя загрузку полных агрегатов.

### 3. Преимущества CQRS в данном контексте

*   **Оптимизация моделей:** Возможность иметь разные модели для записи (полные агрегаты с поведением) и для чтения (плоские DTO, оптимизированные для отображения).
*   **Производительность:** Read-модели могут быть денормализованы и храниться в специализированных хранилищах (например, кэш, поисковый движок), что ускоряет запросы. Write-операции не замедляются сложными запросами на чтение.
*   **Масштабируемость:** Read и Write части системы могут масштабироваться независимо. Например, если чтений гораздо больше, чем записей, можно увеличить количество read-реплик.
*   **Разделение ответственностей:** Код для изменения состояния и код для чтения состояния четко разделены, что упрощает понимание и поддержку.
*   **Гибкость:** Можно использовать разные технологии для хранения write-моделей (например, реляционная БД) и read-моделей (например, NoSQL, полнотекстовый поиск).

## Часть 3: (Опционально) Event Sourcing

Event Sourcing (ES) мог бы быть полезен для агрегата `Post`, если бы требовалась полная история его изменений или возможность восстановить любое его состояние в прошлом.

*   **Применимость:**
    *   Для `Post`: Каждое изменение (создание, редактирование, публикация, архивация) сохранялось бы как событие (`PostCreated`, `PostTitleChanged`, `PostContentChanged`, `PostPublished`, `PostArchived`). Текущее состояние поста восстанавливалось бы путем проигрывания всех его событий.
*   **Преимущества:**
    *   **Полный аудиторский след:** Вся история изменений доступна.
    *   **Временные запросы:** Возможность узнать состояние агрегата на любую точку времени.
    *   **Отладка:** Легче понять, как система пришла в определенное состояние.
    *   **Гибкость в построении Read Models:** Read Models (проекции) можно строить и перестраивать на основе потока событий.
*   **Сложности:**
    *   **Более сложная реализация:** Требуется инфраструктура для хранения и обработки событий (Event Store).
    *   **Версионирование событий:** Схемы событий могут меняться со временем.
    *   **Восстановление состояния:** Проигрывание большого количества событий для восстановления агрегата может быть медленным (требуются снимки состояния - snapshots).
    *   **Консистентность запросов:** Read Models обновляются асинхронно, что приводит к eventual consistency.

Для "Мини-Блога" Event Sourcing, вероятно, был бы избыточен на начальном этапе, но мог бы стать полезным при усложнении требований к аудиту или аналитике поведения пользователей.

## Заключение

Применение Шестиугольной архитектуры обеспечивает хорошую изоляцию доменной логики и тестируемость. CQRS дополнительно позволяет оптимизировать операции чтения и записи, повышая производительность и масштабируемость. Выбор конкретных технологий для адаптеров и хранилищ зависит от специфических требований проекта.
