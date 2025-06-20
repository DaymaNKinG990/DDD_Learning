"""
Примеры кода для модуля "Сервисы приложения (Application Services)".

Демонстрирует:
- Роль Сервисов Приложения как координаторов между внешним миром и доменом.
- Использование Data Transfer Objects (DTOs) для команд и запросов.
- Взаимодействие с Репозиторием для получения и сохранения доменных объектов.
- Обработку сценариев использования (use cases).
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, Generic, List, Optional, TypeVar

# --- Вспомогательные классы (обычно из других модулей) ---


@dataclass(frozen=True)
class UserId:
    """Идентификатор пользователя (Value Object)."""

    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class User:
    """Простая сущность Пользователь."""

    id: UserId
    username: str
    email: str
    version: int = 1

    def update_email(self, new_email: str) -> "User":
        """Обновляет email пользователя и инкрементирует версию."""
        if not new_email:
            raise ValueError("Email не может быть пустым.")
        return replace(self, email=new_email, version=self.version + 1)


T_ID = TypeVar("T_ID")
T_Entity = TypeVar("T_Entity")  # В нашем случае это будет User


class Repository(Generic[T_ID, T_Entity], ABC):
    """Абстрактный базовый класс для Репозиториев."""

    @abstractmethod
    def get_by_id(self, id: T_ID) -> Optional[T_Entity]:
        pass

    @abstractmethod
    def save(self, entity: T_Entity) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[T_Entity]:
        pass  # Для примера, не используется сервисом напрямую


class InMemoryUserRepository(Repository[UserId, User]):
    """Реализация репозитория для пользователей, хранящая данные в памяти."""

    def __init__(self) -> None:
        self._users: Dict[UserId, User] = {}

    def get_by_id(self, id: UserId) -> Optional[User]:
        # print(f"[Repo] Поиск User ID: {id.value}")
        return self._users.get(id)

    def save(self, user: User) -> None:
        # print(f"[Repo] Сохранение User: {user.username}, Version: {user.version}")
        self._users[user.id] = user

    def list_all(self) -> List[User]:
        return list(self._users.values())


# --- Исключения, специфичные для сервиса ---
class UserNotFoundException(Exception):
    """Исключение: пользователь не найден."""

    def __init__(self, user_id: UserId):
        super().__init__(f"Пользователь с ID {user_id.value} не найден.")
        self.user_id = user_id


class UserRegistrationException(Exception):
    """Исключение при регистрации пользователя."""

    pass


# --- Data Transfer Objects (DTOs) ---


@dataclass(frozen=True)
class RegisterUserCommand:
    """Команда для регистрации нового пользователя."""

    username: str
    email: str


@dataclass(frozen=True)
class ChangeUserEmailCommand:
    """Команда для изменения email пользователя."""

    user_id: UserId
    new_email: str


@dataclass(frozen=True)
class UserDTO:
    """DTO для представления данных пользователя."""

    id: str  # Представляем UUID как строку для внешних систем
    username: str
    email: str
    version: int


# --- Сервис Приложения ---


class UserApplicationService:
    """Сервис приложения для управления пользователями."""

    def __init__(self, user_repository: Repository[UserId, User]):
        self._user_repository = user_repository

    def register_user(self, command: RegisterUserCommand) -> UserId:
        """Регистрирует нового пользователя."""
        print(f"[AppService] Регистрация: {command.username}, {command.email}")
        if not command.username or not command.email:
            raise UserRegistrationException(
                "Имя пользователя и email не могут быть пустыми."
            )

        # В реальном приложении здесь могла бы быть проверка на уникальность
        # for user_in_db in self._user_repository.list_all():
        #     if user_in_db.email == command.email:
        #         raise UserRegistrationException(
        #             f"Пользователь с email {command.email} уже существует."
        #         )

        user_id = UserId()
        new_user = User(id=user_id, username=command.username, email=command.email)
        self._user_repository.save(new_user)
        print(
            f"[AppService] Пользователь {command.username} "
            f"зарегистрирован с ID: {user_id.value}"
        )
        return user_id

    def change_user_email(self, command: ChangeUserEmailCommand) -> None:
        """Изменяет email существующего пользователя."""
        print(
            f"[AppService] Изменение email для {command.user_id.value} "
            f"на {command.new_email}"
        )
        user = self._user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundException(command.user_id)

        try:
            updated_user = user.update_email(command.new_email)
        except ValueError as e:
            raise UserRegistrationException(f"Ошибка изменения email: {e}")

        self._user_repository.save(updated_user)
        print(f"[AppService] Email для {user.username} (ID: {user.id.value}) обновлен.")

    def get_user_details(self, user_id: UserId) -> Optional[UserDTO]:
        """Получает детали пользователя в виде DTO."""
        print(f"[AppService] Запрос деталей пользователя: {user_id.value}")
        user = self._user_repository.get_by_id(user_id)
        if not user:
            return None

        return UserDTO(
            id=str(user.id.value),
            username=user.username,
            email=user.email,
            version=user.version,
        )


# --- Демонстрация использования ---

if __name__ == "__main__":
    print("--- Демонстрация Сервисов Приложения ---")

    # 1. Инициализация зависимостей
    user_repo = InMemoryUserRepository()
    user_service = UserApplicationService(user_repository=user_repo)

    # 2. Регистрация нового пользователя
    print("\n--- Регистрация пользователя ---")
    alice_id: Optional[UserId] = None
    register_cmd = RegisterUserCommand(
        username="AliceWonder", email="alice@example.com"
    )
    try:
        alice_id = user_service.register_user(register_cmd)
        print(f"Alice зарегистрирована с ID: {alice_id.value}")

        # Попытка зарегистрировать с пустыми данными
        try:
            user_service.register_user(RegisterUserCommand("", ""))
        except UserRegistrationException as e:
            print(f"Ошибка регистрации: {e}")

    except UserRegistrationException as e:
        print(f"Не удалось зарегистрировать Alice: {e}")
        # alice_id уже None, дополнительное присваивание не требуется

    # 3. Получение деталей пользователя
    print("\n--- Получение деталей пользователя ---")
    if alice_id:
        alice_details = user_service.get_user_details(alice_id)
        if alice_details:
            print(
                f"Детали Alice: ID={alice_details.id}, "
                f"Имя={alice_details.username}, Email={alice_details.email}, "
                f"Версия={alice_details.version}"
            )

    non_existent_id = UserId()
    non_existent_details = user_service.get_user_details(non_existent_id)
    print(
        f"Детали несуществующего пользователя ({non_existent_id.value}): "
        f"{non_existent_details}"
    )

    # 4. Изменение email пользователя
    print("\n--- Изменение email пользователя ---")
    if alice_id:
        change_email_cmd = ChangeUserEmailCommand(
            user_id=alice_id, new_email="alice.updated@example.com"
        )
        try:
            user_service.change_user_email(change_email_cmd)
            updated_alice_details = user_service.get_user_details(alice_id)
            if updated_alice_details:
                print(
                    f"Обновленные детали Alice: Email={updated_alice_details.email}, "
                    f"Версия={updated_alice_details.version}"
                )

            # Попытка изменить email несуществующего пользователя
            try:
                user_service.change_user_email(
                    ChangeUserEmailCommand(
                        user_id=non_existent_id, new_email="any@example.com"
                    )
                )
            except UserNotFoundException as e:
                print(f"Ошибка изменения email: {e}")

            # Попытка установить пустой email
            try:
                user_service.change_user_email(
                    ChangeUserEmailCommand(user_id=alice_id, new_email="")
                )
            except UserRegistrationException as e:
                print(f"Ошибка изменения email: {e}")

        except (UserNotFoundException, UserRegistrationException) as e:
            print(f"Не удалось изменить email Alice: {e}")

    print("\n--- Демонстрация завершена ---")
