from typing import Dict, Optional

from end_to_end_example.application.repositories import CourseRepository
from end_to_end_example.domain.course import Course
from end_to_end_example.domain.value_objects import CourseId


class InMemoryCourseRepository(CourseRepository):
    """Реализация репозитория в памяти для хранения агрегатов Course."""

    def __init__(self) -> None:
        self._courses: Dict[CourseId, Course] = {}

    def save(self, course: Course) -> None:
        """Сохраняет или обновляет курс в словаре."""
        # В реальной реализации здесь была бы логика для оптимистичной блокировки
        # на основе поля 'version'.
        print(f"Сохранение курса {course.id.value} в репозиторий...")
        self._courses[course.id] = course

    def find_by_id(self, course_id: CourseId) -> Optional[Course]:
        """Находит курс по ID."""
        print(f"Поиск курса {course_id.value} в репозитории...")
        return self._courses.get(course_id)
