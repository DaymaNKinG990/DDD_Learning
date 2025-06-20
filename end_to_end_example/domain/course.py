from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from end_to_end_example.domain.events import (
    CourseCreated,
    DomainEvent,
    EnrollmentClosed,
    StudentEnrolled,
)
from end_to_end_example.domain.value_objects import CourseId, CourseName, StudentId


@dataclass
class Course:
    """Агрегат 'Курс'."""

    id: CourseId
    name: CourseName
    capacity: int
    _students: Set[StudentId] = field(default_factory=set, init=False)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    version: int = 0

    @staticmethod
    def create(name: CourseName, capacity: int) -> Course:
        if capacity <= 0:
            raise ValueError("Вместимость курса должна быть положительной.")

        course_id = CourseId()
        course = Course(id=course_id, name=name, capacity=capacity)
        course._add_event(
            CourseCreated(
                aggregate_id=course.id.value,
                name=course.name.value,
                capacity=course.capacity,
            )
        )
        course.version = 1
        return course

    @property
    def students(self) -> Set[StudentId]:
        return set(self._students)

    def pull_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def _add_event(self, event: DomainEvent):
        self._events.append(event)
        self._increment_version()

    def _increment_version(self):
        self.version += 1

    def enroll_student(self, student_id: StudentId):
        if len(self._students) >= self.capacity:
            raise ValueError("Курс уже заполнен.")
        if student_id in self._students:
            # Идемпотентность: повторная запись не вызывает ошибку
            return

        self._students.add(student_id)
        self._add_event(
            StudentEnrolled(aggregate_id=self.id.value, student_id=student_id.value)
        )

        if len(self._students) == self.capacity:
            self._add_event(EnrollmentClosed(aggregate_id=self.id.value))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Course):
            return NotImplemented
        return self.id == other.id
