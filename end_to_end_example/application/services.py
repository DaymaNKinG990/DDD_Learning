import uuid

from end_to_end_example.application.repositories import CourseRepository
from end_to_end_example.domain.course import Course
from end_to_end_example.domain.value_objects import CourseId, CourseName, StudentId


class CourseApplicationService:
    """Сервис приложения для управления курсами."""

    def __init__(self, course_repo: CourseRepository):
        self.course_repo = course_repo
        # В реальном приложении здесь также может быть диспетчер событий.

    def create_course(self, name: str, capacity: int) -> str:
        """Создает новый курс."""
        course_name = CourseName(name)
        course = Course.create(name=course_name, capacity=capacity)
        self.course_repo.save(course)
        # Здесь можно было бы опубликовать события из course.pull_domain_events()
        return str(course.id.value)

    def enroll_student(self, course_id_str: str, student_id_str: str):
        """Записывает студента на курс."""
        try:
            course_uuid = uuid.UUID(course_id_str)
            student_uuid = uuid.UUID(student_id_str)
        except ValueError:
            raise ValueError("Некорректный формат ID.")

        course_id = CourseId(value=course_uuid)
        student_id = StudentId(value=student_uuid)

        course = self.course_repo.find_by_id(course_id)
        if not course:
            raise ValueError("Курс не найден.")

        course.enroll_student(student_id)
        self.course_repo.save(course)
        # Здесь также можно опубликовать события
