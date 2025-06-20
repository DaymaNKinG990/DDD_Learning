"""
Модуль с тестами для системы управления задачами.
"""

from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

# Импортируем классы из решения
from ddd_course.ubiquitous_language_02.task_management_solution_06 import (
    Board,
    Comment,
    Sprint,
    Task,
    TaskDescription,
    TaskPriority,
    TaskStatus,
    TaskType,
    TeamMember,
)

# Фикстуры для тестирования


@pytest.fixture
def product_owner() -> TeamMember:
    """Создаёт экземпляр Product Owner'а."""
    return TeamMember(
        id=uuid4(), name="Анна Петрова", email="anna@example.com", role="Product Owner"
    )


@pytest.fixture
def developer() -> TeamMember:
    """Создаёт экземпляр разработчика."""
    return TeamMember(
        id=uuid4(), name="Иван Сидоров", email="ivan@example.com", role="Разработчик"
    )


@pytest.fixture
def tester() -> TeamMember:
    """Создаёт экземпляр тестировщика."""
    return TeamMember(
        id=uuid4(), name="Мария Иванова", email="maria@example.com", role="Тестировщик"
    )


@pytest.fixture
def active_sprint() -> Sprint:
    """Создаёт активный спринт."""
    current_date = datetime.now()
    return Sprint(
        id=uuid4(),
        name="Спринт 1",
        start_date=current_date - timedelta(days=1),  # Начался вчера
        end_date=current_date + timedelta(days=13),  # Закончится через 13 дней
        goal="Реализация базового функционала",
    )


@pytest.fixture
def task_description() -> TaskDescription:
    """Создаёт описание задачи."""
    return TaskDescription(
        summary="Реализовать авторизацию пользователей",
        details="Необходимо реализовать систему аутентификации и авторизации",
    )


@pytest.fixture
def task(
    product_owner: TeamMember, active_sprint: Sprint, task_description: TaskDescription
) -> Task:
    """Создаёт тестовую задачу."""
    return Task(
        id=uuid4(),
        description=task_description,
        reporter_id=product_owner.id,
        sprint_id=active_sprint.id,
        priority=TaskPriority.HIGH,
        task_type=TaskType.TASK,
        story_points=5,
    )


@pytest.fixture
def board() -> Board:
    """Создаёт тестовую доску задач."""
    return Board(id=uuid4(), name="Доска проекта", project_id=uuid4())


# Тесты для объектов-значений


def test_task_description_validation():
    """Проверяет валидацию описания задачи."""
    # Проверка на пустое описание
    with pytest.raises(ValueError):
        TaskDescription(summary="")

    # Проверка на слишком длинное описание
    with pytest.raises(ValueError):
        TaskDescription(summary="a" * 201)

    # Корректное описание
    desc = TaskDescription(summary="Краткое описание", details="Подробности")
    assert desc.summary == "Краткое описание"
    assert desc.details == "Подробности"


def test_comment_creation():
    """Проверяет создание комментария."""
    comment = Comment(id=uuid4(), author_id=uuid4(), content="Тестовый комментарий")

    assert isinstance(comment.id, UUID)
    assert isinstance(comment.author_id, UUID)
    assert comment.content == "Тестовый комментарий"
    assert isinstance(comment.created_at, datetime)

    # Проверка на пустое содержимое
    with pytest.raises(ValueError):
        Comment(id=uuid4(), author_id=uuid4(), content="")


# Тесты для сущностей


def test_team_member_creation(developer: TeamMember):
    """Проверяет создание участника команды."""
    assert isinstance(developer.id, UUID)
    assert developer.name == "Иван Сидоров"
    assert developer.role == "Разработчик"
    assert developer.is_active is True

    # Деактивация участника
    developer.deactivate()
    assert developer.is_active is False


def test_sprint_validation():
    """Проверяет валидацию дат спринта."""
    current_date = datetime.now()

    # Дата окончания раньше даты начала
    with pytest.raises(ValueError):
        Sprint(
            id=uuid4(),
            name="Невалидный спринт",
            start_date=current_date,
            end_date=current_date - timedelta(days=1),
            goal="Тест",
        )

    # Слишком длинный спринт (больше 28 дней)
    with pytest.raises(ValueError):
        Sprint(
            id=uuid4(),
            name="Слишком длинный спринт",
            start_date=current_date,
            end_date=current_date + timedelta(days=29),
            goal="Тест",
        )


def test_task_creation(task: Task, product_owner: TeamMember, active_sprint: Sprint):
    """Проверяет создание задачи."""
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.HIGH
    assert task.task_type == TaskType.TASK
    assert task.reporter_id == product_owner.id
    assert task.sprint_id == active_sprint.id
    assert task.story_points == 5
    assert len(task.comments) == 0
    assert len(task.labels) == 0


def test_task_assign(task: Task, developer: TeamMember, product_owner: TeamMember):
    """Проверяет назначение задачи исполнителю."""
    # Назначение задачи
    task.assign(developer.id, product_owner.id)

    assert task.assignee_id == developer.id
    assert len(task.comments) == 1
    assert "Задача назначена на пользователя" in task.comments[0].content

    # Проверка обновления времени
    old_updated_at = task.updated_at
    task.assign(
        developer.id, product_owner.id
    )  # Повторное назначение тому же исполнителю
    assert task.updated_at == old_updated_at  # Время не должно измениться


def test_task_status_transitions(
    task: Task, developer: TeamMember, product_owner: TeamMember
):
    """Проверяет переходы между статусами задачи."""
    # Начальный статус
    assert task.status == TaskStatus.TODO

    # Переход в "В работе"
    task.update_status(TaskStatus.IN_PROGRESS, developer.id)
    assert task.status == TaskStatus.IN_PROGRESS

    # Переход в "На проверке"
    task.update_status(TaskStatus.CODE_REVIEW, developer.id)
    assert task.status == TaskStatus.CODE_REVIEW

    # Переход в "Тестирование"
    task.update_status(TaskStatus.TESTING, developer.id)
    assert task.status == TaskStatus.TESTING

    # Переход в "Выполнено"
    task.update_status(TaskStatus.DONE, developer.id)
    assert task.status == TaskStatus.DONE

    # Проверка комментариев
    assert len(task.comments) == 4  # По одному комментарию на каждый переход


def test_task_add_comment(task: Task, developer: TeamMember):
    """Проверяет добавление комментариев к задаче."""
    initial_comment_count = len(task.comments)

    # Добавление комментария
    comment = task.add_comment("Тестовый комментарий", developer.id)

    assert len(task.comments) == initial_comment_count + 1
    assert task.comments[-1].id == comment.id
    assert task.comments[-1].content == "Тестовый комментарий"
    assert task.comments[-1].author_id == developer.id


def test_task_add_label(task: Task, developer: TeamMember):
    """Проверяет добавление меток к задаче."""
    # Добавление метки
    task.add_label("backend", developer.id)

    assert "backend" in task.labels
    assert len(task.comments) == 1
    assert "Добавлена метка: backend" in task.comments[0].content

    # Попытка добавить пустую метку
    with pytest.raises(ValueError):
        task.add_label("", developer.id)


# Тесты для агрегатов


def test_board_add_task(board: Board, task: Task):
    """Проверяет добавление задачи на доску."""
    # Добавление задачи
    board.add_task(task)

    # Проверка, что задача добавлена в колонку TODO
    assert task in board.columns[TaskStatus.TODO]
    assert len(board.columns[TaskStatus.TODO]) == 1

    # Проверка, что в других колонках пусто
    for status, tasks in board.columns.items():
        if status != TaskStatus.TODO:
            assert len(tasks) == 0


def test_board_move_task(board: Board, task: Task, developer: TeamMember):
    """Проверяет перемещение задачи между колонками доски."""
    # Добавляем задачу на доску
    board.add_task(task)

    # Перемещаем задачу в "В работе"
    result = board.move_task(task.id, TaskStatus.IN_PROGRESS, developer.id)

    assert result is True
    assert task not in board.columns[TaskStatus.TODO]
    assert task in board.columns[TaskStatus.IN_PROGRESS]
    assert task.status == TaskStatus.IN_PROGRESS

    # Проверка обновления времени
    assert task.updated_at is not None

    # Проверка комментария о смене статуса
    assert any("Статус изменён" in comment.content for comment in task.comments)


def test_board_move_nonexistent_task(board: Board, developer: TeamMember):
    """Проверяет обработку попытки перемещения несуществующей задачи."""
    non_existent_task_id = uuid4()
    result = board.move_task(non_existent_task_id, TaskStatus.IN_PROGRESS, developer.id)
    assert result is False


# Интеграционные тесты


def test_task_workflow(
    product_owner: TeamMember, developer: TeamMember, active_sprint: Sprint
):
    """Проверяет полный рабочий процесс по задаче."""
    # Создаём описание задачи
    description = TaskDescription(
        summary="Реализовать корзину покупок",
        details=(
            "Необходимо реализовать функционал корзины с добавлением/удалением товаров"
        ),
    )

    # Создаём задачу
    task = Task(
        id=uuid4(),
        description=description,
        reporter_id=product_owner.id,
        sprint_id=active_sprint.id,
        priority=TaskPriority.HIGH,
        task_type=TaskType.TASK,
        story_points=8,
    )

    # Проверяем начальное состояние
    assert task.status == TaskStatus.TODO
    assert task.assignee_id is None

    # Назначаем задачу разработчику
    task.assign(developer.id, product_owner.id)
    assert task.assignee_id == developer.id
    assert task.status == TaskStatus.TODO

    # Добавляем метки
    task.add_label("frontend", product_owner.id)
    task.add_label("ui", product_owner.id)
    assert {"frontend", "ui"}.issubset(task.labels)

    # Добавляем комментарий
    task.add_comment(
        "Убедитесь, что корзина сохраняется после перезагрузки страницы",
        product_owner.id,
    )

    # Меняем статус на "В работе"
    task.update_status(TaskStatus.IN_PROGRESS, developer.id)
    assert task.status == TaskStatus.IN_PROGRESS

    # Добавляем комментарий от разработчика
    task.add_comment("Начал реализацию", developer.id)

    # Завершаем работу над задачей
    task.update_status(TaskStatus.CODE_REVIEW, developer.id)
    assert task.status == TaskStatus.CODE_REVIEW

    # Добавляем комментарий о завершении
    task.add_comment("Готово к ревью кода", developer.id)

    # Проверяем итоговое состояние
    assert (
        len(task.comments) >= 5
    )  # Как минимум 5 комментариев (назначение, метки, смена статусов)
    # Проверяем, что updated_at не раньше created_at
    assert task.updated_at >= task.created_at


if __name__ == "__main__":
    pytest.main(["-v", "test_task_management.py"])
