from abc import ABC, abstractmethod
from typing import Optional

from end_to_end_example.domain.course import Course
from end_to_end_example.domain.value_objects import CourseId


class CourseRepository(ABC):
    """Абстрактный репозиторий для агрегата Course."""

    @abstractmethod
    def save(self, course: Course) -> None:
        """Сохраняет состояние агрегата."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, course_id: CourseId) -> Optional[Course]:
        """Находит агрегат по его идентификатору."""
        raise NotImplementedError
