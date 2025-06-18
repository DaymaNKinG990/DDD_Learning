"""
Решение практического задания по разработке системы управления задачами.

Этот модуль демонстрирует применение принципов Ubiquitous Language
в контексте системы управления задачами (Task Management System).
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional, Set, Dict, Any
from uuid import UUID, uuid4


# ============================================
# Value Objects (Объекты-значения)
# ============================================

@dataclass(frozen=True)
class TaskDescription:
    """Описание задачи.
    
    Атрибуты:
        summary: Краткое описание задачи (до 200 символов)
        details: Подробное описание (опционально)
    """
    summary: str
    details: str = ""

    def __post_init__(self):
        if not self.summary or not self.summary.strip():
            raise ValueError("Краткое описание задачи не может быть пустым")
        if len(self.summary) > 200:
            raise ValueError("Краткое описание не должно превышать 200 символов")


@dataclass(frozen=True)
class Comment:
    """Комментарий к задаче.
    
    Атрибуты:
        id: Уникальный идентификатор комментария
        author_id: Идентификатор автора
        content: Текст комментария
        created_at: Дата и время создания
    """
    id: UUID
    author_id: UUID
    content: str
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("Текст комментария не может быть пустым")


# ============================================
# Enums (Перечисления)
# ============================================

class TaskStatus(Enum):
    """Статусы задачи."""
    TODO = "К выполнению"
    IN_PROGRESS = "В работе"
    CODE_REVIEW = "На проверке"
    TESTING = "Тестирование"
    DONE = "Выполнено"


class TaskPriority(Enum):
    """Приоритеты задачи."""
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"
    CRITICAL = "Критический"


class TaskType(Enum):
    """Типы задач."""
    TASK = "Задача"
    BUG = "Ошибка"
    IMPROVEMENT = "Улучшение"
    STORY = "История"


# ============================================
# Entities (Сущности)
# ============================================

@dataclass
class TeamMember:
    """Член команды.
    
    Атрибуты:
        id: Уникальный идентификатор
        name: Имя и фамилия
        email: Адрес электронной почты
        role: Роль в команде
        is_active: Активен ли участник
    """
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool = True
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Имя участника не может быть пустым")
        if "@" not in self.email:
            raise ValueError("Некорректный email адрес")
    
    def deactivate(self) -> None:
        """Деактивировать участника команды."""
        self.is_active = False


@dataclass
class Sprint:
    """Спринт - временной интервал для выполнения набора задач.
    
    Атрибуты:
        id: Уникальный идентификатор
        name: Название спринта
        start_date: Дата начала
        end_date: Дата окончания
        is_active: Активен ли спринт
        goal: Цель спринта
    """
    id: UUID
    name: str
    start_date: datetime
    end_date: datetime
    goal: str
    is_active: bool = True
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Название спринта не может быть пустым")
        if self.start_date >= self.end_date:
            raise ValueError("Дата начала должна быть раньше даты окончания")
        if (self.end_date - self.start_date).days < 1:
            raise ValueError("Спринт должен длиться хотя бы один день")
        if (self.end_date - self.start_date).days > 28:
            raise ValueError("Максимальная длительность спринта - 4 недели")
    
    @property
    def is_completed(self) -> bool:
        """Завершён ли спринт."""
        return datetime.now() > self.end_date
    
    def complete(self) -> None:
        """Пометить спринт как завершённый."""
        self.is_active = False


@dataclass
class Task:
    """Задача в системе управления задачами.
    
    Атрибуты:
        id: Уникальный идентификатор
        description: Описание задачи
        status: Текущий статус
        priority: Приоритет
        task_type: Тип задачи
        assignee_id: Идентификатор исполнителя
        reporter_id: Идентификатор создателя
        sprint_id: Идентификатор спринта
        created_at: Дата и время создания
        updated_at: Дата и время последнего обновления
        comments: Список комментариев
        story_points: Оценка сложности в стори-поинтах
        labels: Метки задачи
    """
    id: UUID
    description: TaskDescription
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    task_type: TaskType = TaskType.TASK
    assignee_id: Optional[UUID] = None
    reporter_id: Optional[UUID] = None
    sprint_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    comments: List[Comment] = field(default_factory=list)
    story_points: Optional[int] = None
    labels: Set[str] = field(default_factory=set)
    
    def assign(self, assignee_id: UUID, current_user_id: UUID) -> None:
        """Назначить задачу исполнителю.
        
        Аргументы:
            assignee_id: Идентификатор нового исполнителя
            current_user_id: Идентификатор пользователя, выполняющего назначение
            
        Исключения:
            ValueError: Если текущий пользователь не имеет прав на назначение
        """
        # В реальном приложении здесь была бы проверка прав доступа
        self.assignee_id = assignee_id
        self.updated_at = datetime.now()
        self._add_system_comment(f"Задача назначена на пользователя {assignee_id}", current_user_id)
    
    def update_status(self, new_status: TaskStatus, user_id: UUID) -> None:
        """Обновить статус задачи.
        
        Аргументы:
            new_status: Новый статус задачи
            user_id: Идентификатор пользователя, изменяющего статус
        """
        if self.status == new_status:
            return
            
        self.status = new_status
        self.updated_at = datetime.now()
        self._add_system_comment(f"Статус изменён на '{new_status.value}'", user_id)
    
    def add_comment(self, content: str, author_id: UUID) -> Comment:
        """Добавить комментарий к задаче.
        
        Аргументы:
            content: Текст комментария
            author_id: Идентификатор автора
            
        Возвращает:
            Созданный комментарий
        """
        comment = Comment(
            id=uuid4(),
            author_id=author_id,
            content=content
        )
        self.comments.append(comment)
        self.updated_at = datetime.now()
        return comment
    
    def add_label(self, label: str, user_id: UUID) -> None:
        """Добавить метку к задаче.
        
        Аргументы:
            label: Название метки
            user_id: Идентификатор пользователя, добавляющего метку
        """
        if not label or not label.strip():
            raise ValueError("Название метки не может быть пустым")
            
        if label in self.labels:
            return
            
        self.labels.add(label.strip())
        self.updated_at = datetime.now()
        self._add_system_comment(f"Добавлена метка: {label}", user_id)
    
    def _add_system_comment(self, content: str, user_id: UUID) -> None:
        """Добавить системный комментарий.
        
        Аргументы:
            content: Текст комментария
            user_id: Идентификатор пользователя, инициировавшего действие
        """
        comment = Comment(
            id=uuid4(),
            author_id=user_id,
            content=f"[Система] {content}",
            created_at=datetime.now()
        )
        self.comments.append(comment)


# ============================================
# Aggregates (Агрегаты)
# ============================================

@dataclass
class Board:
    """Доска задач.
    
    Атрибуты:
        id: Уникальный идентификатор
        name: Название доски
        project_id: Идентификатор проекта
        columns: Словарь колонок доски (статус -> список задач)
    """
    id: UUID
    name: str
    project_id: UUID
    columns: Dict[TaskStatus, List[Task]] = field(default_factory=dict)
    
    def __post_init__(self):
        # Инициализируем колонки для всех статусов
        for status in TaskStatus:
            self.columns[status] = []
    
    def add_task(self, task: Task) -> None:
        """Добавить задачу на доску.
        
        Аргументы:
            task: Задача для добавления
        """
        if not task.status:
            task.status = TaskStatus.TODO
            
        self.columns[task.status].append(task)
    
    def move_task(self, task_id: UUID, new_status: TaskStatus, user_id: UUID) -> bool:
        """Переместить задачу в другую колонку.
        
        Аргументы:
            task_id: Идентификатор задачи
            new_status: Новый статус
            user_id: Идентификатор пользователя, выполняющего действие
            
        Возвращает:
            True, если перемещение выполнено успешно, иначе False
        """
        # Находим задачу в текущих колонках
        for status, tasks in self.columns.items():
            for i, task in enumerate(tasks):
                if str(task.id) == str(task_id):
                    # Обновляем статус задачи
                    task.update_status(new_status, user_id)
                    
                    # Удаляем из текущей колонки и добавляем в новую
                    tasks.pop(i)
                    self.columns[new_status].append(task)
                    return True
        return False


# ============================================
# Domain Services (Доменные сервисы)
# ============================================

class SprintPlanningService:
    """Сервис для управления спринтами."""
    
    def __init__(self, task_repository, sprint_repository):
        self.task_repository = task_repository
        self.sprint_repository = sprint_repository
    
    def complete_sprint(
        self, 
        sprint_id: UUID, 
        new_sprint: 'Sprint', 
        user_id: UUID
    ) -> None:
        """Завершить спринт и перенести незавершённые задачи в новый спринт.
        
        Аргументы:
            sprint_id: Идентификатор завершаемого спринта
            new_sprint: Новый спринт
            user_id: Идентификатор пользователя, выполняющего действие
        """
        # Находим текущий спринт
        current_sprint = self.sprint_repository.find_by_id(sprint_id)
        if not current_sprint:
            raise ValueError(f"Спринт с ID {sprint_id} не найден")
        
        # Находим все незавершённые задачи
        incomplete_tasks = self.task_repository.find_by_sprint_and_status_not(
            sprint_id=sprint_id,
            status=TaskStatus.DONE
        )
        
        # Переносим задачи в новый спринт
        for task in incomplete_tasks:
            task.sprint_id = new_sprint.id
            task.add_comment(
                f"Перенесено из спринта '{current_sprint.name}' в спринт '{new_sprint.name}'",
                user_id
            )
            self.task_repository.save(task)
        
        # Помечаем текущий спринт как завершённый
        current_sprint.complete()
        self.sprint_repository.save(current_sprint)
        
        # Сохраняем новый спринт
        self.sprint_repository.save(new_sprint)


# ============================================
# Repositories (Репозитории, интерфейсы)
# ============================================

class TaskRepository:
    """Репозиторий для работы с задачами."""
    
    def find_by_id(self, task_id: UUID) -> Optional[Task]:
        """Найти задачу по идентификатору."""
        raise NotImplementedError
    
    def find_by_sprint(self, sprint_id: UUID) -> List[Task]:
        """Найти все задачи в спринте."""
        raise NotImplementedError
    
    def find_by_sprint_and_status_not(
        self, 
        sprint_id: UUID, 
        status: TaskStatus
    ) -> List[Task]:
        """Найти все задачи в спринте с указанным статусом."""
        raise NotImplementedError
    
    def save(self, task: Task) -> None:
        """Сохранить задачу."""
        raise NotImplementedError


class SprintRepository:
    """Репозиторий для работы со спринтами."""
    
    def find_by_id(self, sprint_id: UUID) -> Optional[Sprint]:
        """Найти спринт по идентификатору."""
        raise NotImplementedError
    
    def find_active_sprint(self, project_id: UUID) -> Optional[Sprint]:
        """Найти активный спринт в проекте."""
        raise NotImplementedError
    
    def save(self, sprint: Sprint) -> None:
        """Сохранить спринт."""
        raise NotImplementedError


# ============================================
# Пример использования
# ============================================

def demonstrate_task_management():
    """Демонстрация работы системы управления задачами."""
    print("=== Демонстрация системы управления задачами ===\n")
    
    # Создаём участников команды
    product_owner = TeamMember(
        id=uuid4(),
        name="Анна Петрова",
        email="anna@example.com",
        role="Product Owner"
    )
    
    developer = TeamMember(
        id=uuid4(),
        name="Иван Сидоров",
        email="ivan@example.com",
        role="Разработчик"
    )
    
    # Создаём спринт
    current_date = datetime.now()
    sprint = Sprint(
        id=uuid4(),
        name="Спринт 1",
        start_date=current_date,
        end_date=current_date + timedelta(days=14),
        goal="Реализация базового функционала"
    )
    
    # Создаём задачу
    task_description = TaskDescription(
        summary="Реализовать авторизацию пользователей",
        details="Необходимо реализовать систему аутентификации и авторизации"
    )
    
    task = Task(
        id=uuid4(),
        description=task_description,
        reporter_id=product_owner.id,
        sprint_id=sprint.id,
        priority=TaskPriority.HIGH,
        task_type=TaskType.TASK,
        story_points=5
    )
    
    # Назначаем задачу разработчику
    task.assign(developer.id, product_owner.id)
    
    # Добавляем комментарий
    task.add_comment("Убедитесь, что поддерживается двухфакторная аутентификация", product_owner.id)
    
    # Изменяем статус задачи
    task.update_status(TaskStatus.IN_PROGRESS, developer.id)
    
    # Выводим информацию о задаче
    print(f"Задача: {task.description.summary}")
    print(f"Статус: {task.status.value}")
    print(f"Исполнитель: {developer.name}")
    print("Комментарии:")
    for comment in task.comments:
        print(f"- {comment.content}")
    
    # Создаём доску задач
    board = Board(
        id=uuid4(),
        name="Доска проекта",
        project_id=uuid4()
    )
    
    # Добавляем задачу на доску
    board.add_task(task)
    
    # Перемещаем задачу в колонку "В работе"
    board.move_task(task.id, TaskStatus.IN_PROGRESS, developer.id)
    
    print("\nСостояние доски:")
    for status, tasks in board.columns.items():
        print(f"\n{status.value} ({len(tasks)}):")
        for t in tasks:
            print(f"- {t.description.summary}")


if __name__ == "__main__":
    demonstrate_task_management()
