import uuid

import pytest

from end_to_end_example.application.services import CourseApplicationService
from end_to_end_example.domain.value_objects import CourseId
from end_to_end_example.infrastructure.repositories import InMemoryCourseRepository


@pytest.fixture
def course_service() -> CourseApplicationService:
    """Фикстура, предоставляющая сервис приложения с чистым репозиторием."""
    return CourseApplicationService(InMemoryCourseRepository())


def test_create_course_service(course_service: CourseApplicationService):
    """Тест успешного создания курса через сервис приложения."""
    course_name = "Изучаем DDD глубоко"
    capacity = 25

    course_id_str = course_service.create_course(course_name, capacity)
    assert isinstance(course_id_str, str)

    # Проверяем, что курс действительно сохранился в репозитории
    repo = course_service.course_repo
    course_id = CourseId(value=uuid.UUID(course_id_str))
    course = repo.find_by_id(course_id)
    assert course is not None
    assert course.name.value == course_name
    assert course.capacity == capacity


def test_enroll_student_service(course_service: CourseApplicationService):
    """Тест успешной записи студента через сервис приложения."""
    # 1. Создаем курс
    course_id_str = course_service.create_course("Тестовый курс", 5)
    student_id_str = str(uuid.uuid4())

    # 2. Записываем студента
    course_service.enroll_student(course_id_str, student_id_str)

    # 3. Проверяем состояние
    repo = course_service.course_repo
    course_id = CourseId(value=uuid.UUID(course_id_str))
    course = repo.find_by_id(course_id)
    assert course is not None

    student_ids_in_course = {str(s.value) for s in course.students}
    assert student_id_str in student_ids_in_course


def test_enroll_student_fails_for_nonexistent_course(
    course_service: CourseApplicationService,
):
    """Тест: запись на несуществующий курс должна вызывать ошибку."""
    non_existent_course_id = str(uuid.uuid4())
    student_id = str(uuid.uuid4())

    with pytest.raises(ValueError, match="Курс не найден."):
        course_service.enroll_student(non_existent_course_id, student_id)
