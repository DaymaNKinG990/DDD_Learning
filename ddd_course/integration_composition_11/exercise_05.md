# Упражнение: Проектирование Карты Контекстов и Интеграции для Системы "Онлайн-Университет"

## Контекст Задачи

Представьте, что вы проектируете архитектуру для новой платформы "Онлайн-Университет". Платформа должна поддерживать различные аспекты деятельности современного онлайн-образовательного учреждения.

**Основные функциональные блоки (потенциальные Ограниченные Контексты):**

1.  **Приемная Кампания (Admissions):**
    *   Обработка заявок от абитуриентов.
    *   Проведение онлайн-тестирования или оценка портфолио.
    *   Принятие решений о зачислении.
    *   Формирование личных дел зачисленных студентов.

2.  **Управление Курсами (Course Management):**
    *   Создание и редактирование учебных курсов (описание, программа, материалы).
    *   Назначение преподавателей на курсы.
    *   Управление каталогом курсов.

3.  **Обучение Студентов (Student Learning):**
    *   Запись студентов на курсы.
    *   Доступ к учебным материалам.
    *   Сдача заданий и тестов.
    *   Отслеживание прогресса обучения.
    *   Взаимодействие с преподавателями и другими студентами (форумы, чаты).

4.  **Управление Преподавателями (Faculty Management):**
    *   Учет преподавательского состава.
    *   Назначение нагрузки.
    *   Оценка работы преподавателей (возможно, на основе отзывов студентов).

5.  **Финансы и Оплата (Billing & Payments):**
    *   Выставление счетов за обучение.
    *   Обработка платежей (возможно, через интеграцию с внешними платежными системами).
    *   Управление стипендиями и грантами.

6.  **Сертификация и Выпуск (Certification & Graduation):**
    *   Проверка выполнения учебного плана студентом.
    *   Выдача цифровых сертификатов или дипломов.
    *   Ведение реестра выпускников.

## Задание

1.  **Определите Ограниченные Контексты:**
    *   На основе описанных функциональных блоков, предложите свое видение Ограниченных Контекстов для системы "Онлайн-Университет". Дайте каждому контексту четкое имя и кратко опишите его основную ответственность и ключевые понятия (часть Единого Языка). Вы можете объединять или разделять предложенные блоки, если считаете это целесообразным.

2.  **Создайте Карту Контекстов (Context Map):**
    *   Для определенных вами Ограниченных Контекстов нарисуйте Карту Контекстов (можно использовать текстовое описание или псевдографику).
    *   Для каждой пары взаимодействующих контекстов укажите тип взаимоотношения (например, Партнерство, Клиент-Поставщик, Общее Ядро, Антикоррупционный Слой, Конформист и т.д.). Обоснуйте свой выбор для как минимум 3-4 ключевых взаимосвязей.

3.  **Детализируйте Интеграцию для Двух Взаимосвязей:**
    *   Выберите две наиболее интересные или важные, на ваш взгляд, взаимосвязи между Ограниченными Контекстами из вашей Карты Контекстов.
    *   Для каждой из этих двух взаимосвязей:
        *   Опишите, какие данные или функциональность передаются между контекстами.
        *   Предложите технический способ интеграции (например, синхронный REST API вызов, асинхронный обмен сообщениями через брокер, использование Общего Ядра).
        *   Если вы выбрали ACL, опишите, какие функции он будет выполнять.
        *   Если используется Опубликованный Язык, приведите примеры структур данных (DTO или сообщений).

4.  **Композиция UI (Краткое Обсуждение):**
    *   Кратко опишите, как бы вы подошли к вопросу интеграции пользовательских интерфейсов для различных частей системы "Онлайн-Университет". Какой подход к композиции UI (например, монолитный фронтенд, микрофронтенды, гиперссылки) вы бы рассмотрели и почему?

## Критерии Оценки

*   Четкость определения Ограниченных Контекстов и их ответственности.
*   Логичность и обоснованность построенной Карты Контекстов и выбранных паттернов взаимоотношений.
*   Глубина проработки деталей интеграции для выбранных взаимосвязей.
*   Понимание преимуществ и недостатков различных подходов к интеграции и композиции.
*   Способность применять теоретические знания модуля к практическому заданию.

## Формат Сдачи

Представьте ваше решение в виде текстового документа (Markdown). Для Карты Контекстов можно использовать псевдографику или детальное текстовое описание связей.
