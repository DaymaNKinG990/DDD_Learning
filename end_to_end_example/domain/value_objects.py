import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CourseId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class StudentId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class CourseName:
    value: str

    def __post_init__(self):
        if not 3 <= len(self.value) <= 100:
            raise ValueError("Название курса должно содержать от 3 до 100 символов.")
