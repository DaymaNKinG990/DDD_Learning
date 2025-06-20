import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: uuid.UUID


@dataclass(frozen=True)
class CourseCreated(DomainEvent):
    name: str
    capacity: int


@dataclass(frozen=True)
class StudentEnrolled(DomainEvent):
    student_id: uuid.UUID


@dataclass(frozen=True)
class EnrollmentClosed(DomainEvent):
    pass
