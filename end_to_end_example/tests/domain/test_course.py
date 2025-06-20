import pytest

from end_to_end_example.domain.course import Course
from end_to_end_example.domain.events import (
    CourseCreated,
    EnrollmentClosed,
    StudentEnrolled,
)
from end_to_end_example.domain.value_objects import CourseName, StudentId


def test_course_creation():
    """Тест успешного создания курса."""
    name = CourseName("DDD в действии")
    capacity = 10
    course = Course.create(name, capacity)

    assert course.name == name
    assert course.capacity == capacity
    assert len(course.students) == 0
    assert course.version == 1

    events = course.pull_domain_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, CourseCreated)
    assert event.aggregate_id == course.id.value
    assert event.name == "DDD в действии"
    assert event.capacity == 10


def test_course_creation_fails_with_zero_capacity():
    """Тест: создание курса с нулевой вместимостью должно вызывать ошибку."""
    with pytest.raises(
        ValueError, match="Вместимость курса должна быть положительной."
    ):
        Course.create(CourseName("Неправильный курс"), 0)


def test_student_enrollment():
    """Тест успешной записи студента на курс."""
    course = Course.create(CourseName("Python для начинающих"), 2)
    student_id = StudentId()

    course.enroll_student(student_id)

    assert student_id in course.students
    assert course.version == 2  # 1-create, 2-enroll

    events = course.pull_domain_events()
    assert len(events) == 2  # CourseCreated, StudentEnrolled
    enroll_event = events[1]
    assert isinstance(enroll_event, StudentEnrolled)
    assert enroll_event.student_id == student_id.value


def test_enrollment_fails_when_course_is_full():
    """Тест: запись на заполненный курс должна вызывать ошибку."""
    course = Course.create(CourseName("Эксклюзивный курс"), 1)
    course.enroll_student(StudentId())

    with pytest.raises(ValueError, match="Курс уже заполнен."):
        course.enroll_student(StudentId())


def test_enrollment_is_idempotent():
    """Тест: повторная запись того же студента идемпотентна."""
    course = Course.create(CourseName("Повторный курс"), 2)
    student_id = StudentId()
    course.enroll_student(student_id)

    initial_students_count = len(course.students)
    initial_version = course.version

    course.enroll_student(student_id)  # Повторная запись

    assert len(course.students) == initial_students_count
    assert course.version == initial_version  # Версия не должна меняться


def test_enrollment_closed_event_is_raised():
    """Тест: событие о закрытии записи генерируется, когда достигается лимит."""
    course = Course.create(CourseName("Последнее место"), 1)
    student_id = StudentId()

    course.enroll_student(student_id)

    events = course.pull_domain_events()
    assert len(events) == 3  # Created, Enrolled, Closed
    assert any(isinstance(e, EnrollmentClosed) for e in events)
