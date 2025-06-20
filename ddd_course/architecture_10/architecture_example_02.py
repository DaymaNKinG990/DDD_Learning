"""
Примеры кода для модуля "Архитектура".

Демонстрирует концепцию слоистой архитектуры в DDD на упрощенном примере:
- Domain Layer: Сущности, Объекты-Значения, интерфейсы Репозиториев.
- Application Layer: Сервисы Приложения, DTO, координация.
- Infrastructure Layer: Конкретные реализации Репозиториев, внешние сервисы.
- Presentation Layer (simulated): Точка входа, взаимодействие с Application Layer.

Основное внимание уделяется разделению ответственности и направлению зависимостей.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional


# ==============================================================================
# 0. Общие исключения (могут быть в отдельном модуле)
# ==============================================================================
class EntityNotFoundException(Exception):
    """Базовое исключение для не найденных сущностей."""

    pass


class ValidationException(Exception):
    """Базовое исключение для ошибок валидации."""

    pass


# ==============================================================================
# 1. DOMAIN LAYER (Слой Домена)
# ==============================================================================
# Ответственность: Бизнес-логика, правила, состояние домена.
# Не зависит от других слоев.


@dataclass(frozen=True)
class UserId:
    """Идентификатор пользователя (Value Object)."""

    value: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class User:
    """Сущность Пользователь."""

    id: UserId
    username: str
    email: str
    is_active: bool = True

    def deactivate(self) -> None:
        """Деактивирует пользователя."""
        if not self.is_active:
            # Пример простого инварианта
            print(f"[Domain] Пользователь {self.username} уже неактивен.")
            return
        self.is_active = False
        print(f"[Domain] Пользователь {self.username} деактивирован.")

    def change_email(self, new_email: str) -> None:
        """Изменяет email пользователя."""
        if not new_email or "@" not in new_email:
            raise ValidationException("Некорректный формат email.")
        self.email = new_email
        print(f"[Domain] Email пользователя {self.username} изменен на {new_email}.")


class UserRepository(ABC):
    """Абстрактный интерфейс Репозитория для Пользователей."""

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass


# Доменный сервис (пример, если бы была сложная логика, не принадлежащая User)
# class UserRegistrationValidator:
#     def is_username_unique(
#         self, username: str, user_repository: UserRepository
#     ) -> bool:
#         # ... логика проверки уникальности ...
#         return user_repository.find_by_username(username) is None

# ==============================================================================
# 2. APPLICATION LAYER (Слой Приложения)
# ==============================================================================
# Ответственность: Координация сценариев использования (use cases).
# Зависит от Domain Layer (интерфейсы, сущности).
# Не зависит от Infrastructure (кроме интерфейсов, которые реализует Infrastructure)
# и Presentation.


@dataclass(frozen=True)
class RegisterUserCommand:
    """Команда для регистрации пользователя (DTO)."""

    username: str
    email: str


@dataclass(frozen=True)
class UserDetailsDTO:
    """DTO для представления деталей пользователя."""

    id: str
    username: str
    email: str
    is_active: bool


class UserApplicationService:
    """Сервис приложения для управления пользователями."""

    def __init__(self, user_repository: UserRepository):
        # Зависимость от ИНТЕРФЕЙСА репозитория (Domain Layer)
        self._user_repository = user_repository
        # self._email_service = email_service # Зависимость от интерфейса EmailService

    def register_user(self, command: RegisterUserCommand) -> UserId:
        print(f"[AppService] Попытка регистрации: {command.username}")
        if not command.username or not command.email:
            raise ValidationException("Имя пользователя и email обязательны.")

        existing_user = self._user_repository.find_by_email(command.email)
        if existing_user:
            raise ValidationException(
                f"Пользователь с email {command.email} уже существует."
            )

        user_id = UserId()
        new_user = User(id=user_id, username=command.username, email=command.email)
        self._user_repository.save(new_user)
        print(
            f"[AppService] Пользователь {command.username} "
            f"зарегистрирован с ID: {user_id.value}"
        )
        # self._email_service.send_welcome_email(new_user.email) # Вызов др. сервиса
        return user_id

    def get_user_details(self, user_id_str: str) -> Optional[UserDetailsDTO]:
        print(f"[AppService] Запрос деталей для ID: {user_id_str}")
        try:
            user_id = UserId(value=uuid.UUID(user_id_str))
        except ValueError:
            raise ValidationException("Некорректный формат ID пользователя.")

        user = self._user_repository.get_by_id(user_id)
        if not user:
            return None

        return UserDetailsDTO(
            id=str(user.id.value),
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )

    def deactivate_user(self, user_id_str: str) -> None:
        print(f"[AppService] Попытка деактивации пользователя ID: {user_id_str}")
        try:
            user_id = UserId(value=uuid.UUID(user_id_str))
        except ValueError:
            raise ValidationException("Некорректный формат ID пользователя.")

        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException(
                f"Пользователь с ID {user_id_str} не найден для деактивации."
            )

        user.deactivate()  # Вызов метода доменной сущности
        self._user_repository.save(user)  # Сохранение измененного состояния
        print(
            f"[AppService] Пользователь {user.username} успешно помечен как неактивный."
        )


# ==============================================================================
# 3. INFRASTRUCTURE LAYER (Инфраструктурный Слой)
# ==============================================================================
# Ответственность: Реализация технических деталей (БД, внешние сервисы).
# Зависит от Domain Layer (реализует его интерфейсы).


class InMemoryUserRepository(UserRepository):
    """Конкретная реализация UserRepository, хранящая данные в памяти."""

    def __init__(self) -> None:
        self._users: Dict[UserId, User] = {}
        print("[Infra] InMemoryUserRepository инициализирован.")

    def get_by_id(self, user_id: UserId) -> Optional[User]:
        print(f"[InfraRepo] Поиск пользователя по ID: {user_id.value}")
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        print(f"[InfraRepo] Сохранение: {user.username} (ID: {user.id.value})")
        self._users[user.id] = user

    def find_by_email(self, email: str) -> Optional[User]:
        print(f"[InfraRepo] Поиск пользователя по email: {email}")
        for user in self._users.values():
            if user.email == email:
                return user
        return None


# class SmtpEmailService: # Реализация интерфейса EmailService
#     def send_welcome_email(self, email_address: str):
#         print(f"[InfraEmail] Отправка приветственного письма на {email_address}")

# ==============================================================================
# 4. PRESENTATION LAYER / UI (Слой Представления - симуляция)
# ==============================================================================
# Ответственность: Взаимодействие с пользователем/внешней системой.
# Зависит от Application Layer.


class UserController:
    """Симуляция контроллера, обрабатывающего HTTP-запросы."""

    def __init__(self, user_service: UserApplicationService):
        self._user_service = user_service
        print("[UI] UserController инициализирован.")

    def handle_register_user_request(self, username: str, email: str):
        print(f"\n[UI] Запрос на регистрацию: username='{username}', email='{email}'")
        command = RegisterUserCommand(username=username, email=email)
        try:
            user_id = self._user_service.register_user(command)
            print(f"[UI] Ответ: Успешно зарегистрирован. User ID: {user_id.value}")
            return {"status": "success", "user_id": str(user_id.value)}
        except (ValidationException, EntityNotFoundException) as e:
            print(f"[UI] Ответ: Ошибка регистрации - {e}")
            return {"status": "error", "message": str(e)}

    def handle_get_user_details_request(self, user_id_str: str):
        print(f"\n[UI] Запрос на получение деталей: ID='{user_id_str}'")
        try:
            user_dto = self._user_service.get_user_details(user_id_str)
            if user_dto:
                print(f"[UI] Ответ: {user_dto}")
                return {"status": "success", "data": user_dto.__dict__}
            else:
                print("[UI] Ответ: Пользователь не найден.")
                return {"status": "not_found"}
        except (ValidationException, EntityNotFoundException) as e:
            print(f"[UI] Ответ: Ошибка - {e}")
            return {"status": "error", "message": str(e)}

    def handle_deactivate_user_request(self, user_id_str: str):
        print(f"\n[UI] Получен запрос на деактивацию пользователя: ID='{user_id_str}'")
        try:
            self._user_service.deactivate_user(user_id_str)
            print(f"[UI] Ответ: Пользователь {user_id_str} деактивирован.")
            return {"status": "success"}
        except (ValidationException, EntityNotFoundException) as e:
            print(f"[UI] Ответ: Ошибка деактивации - {e}")
            return {"status": "error", "message": str(e)}


# ==============================================================================
# Composition Root / Main execution (Точка сборки и запуска)
# ==============================================================================
if __name__ == "__main__":
    print("--- Демонстрация Слоистой Архитектуры ---")

    # 1. Создание зависимостей (Dependency Injection вручную)
    #    В реальном приложении это может делать DI-контейнер.
    print("\n--- Инициализация компонентов ---")
    user_repository_impl = InMemoryUserRepository()  # Из Infrastructure Layer
    # email_service_impl = SmtpEmailService()      # Из Infrastructure Layer

    user_app_service = UserApplicationService(  # Из Application Layer
        user_repository=user_repository_impl
        # email_service=email_service_impl
    )

    user_controller = UserController(user_app_service)  # Из Presentation Layer

    # 2. Симуляция HTTP-запросов к контроллеру

    # Успешная регистрация
    response1 = user_controller.handle_register_user_request(
        "AliceSmith", "alice@example.com"
    )
    alice_id_str = response1.get("user_id")

    # Попытка регистрации с тем же email
    user_controller.handle_register_user_request("AliceClone", "alice@example.com")

    # Регистрация второго пользователя
    response2 = user_controller.handle_register_user_request(
        "BobJohnson", "bob@example.com"
    )
    bob_id_str = response2.get("user_id")

    # Получение деталей Alice
    if alice_id_str:
        user_controller.handle_get_user_details_request(alice_id_str)

    # Получение деталей несуществующего пользователя
    user_controller.handle_get_user_details_request(str(uuid.uuid4()))

    # Получение деталей с неверным ID
    user_controller.handle_get_user_details_request("invalid-uuid-format")

    # Деактивация Alice
    if alice_id_str:
        user_controller.handle_deactivate_user_request(alice_id_str)
        # Повторный запрос деталей Alice, чтобы увидеть изменения
        user_controller.handle_get_user_details_request(alice_id_str)
        # Попытка деактивировать Alice еще раз
        user_controller.handle_deactivate_user_request(alice_id_str)

    # Попытка деактивировать несуществующего пользователя
    user_controller.handle_deactivate_user_request(str(uuid.uuid4()))

    print("\n--- Демонстрация завершена ---")
