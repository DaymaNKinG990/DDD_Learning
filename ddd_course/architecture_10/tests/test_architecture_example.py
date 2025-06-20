"""
Тесты для примеров из модуля "Архитектура".

Тестируют взаимодействие слоев, как показано в architecture_example_02.py:
- Юнит-тесты для UserApplicationService с мокированным UserRepository.
- Интеграционные тесты для UserController, использующие реальные UserApplicationService
  и InMemoryUserRepository.
"""

import uuid
from unittest.mock import MagicMock

import pytest

from ddd_course.architecture_10.architecture_example_02 import (
    EntityNotFoundException,
    InMemoryUserRepository,
    RegisterUserCommand,
    User,
    UserApplicationService,
    UserController,
    UserDetailsDTO,
    UserId,
    UserRepository,
    ValidationException,
)

# ==============================================================================
# Фикстуры
# ==============================================================================


@pytest.fixture
def mock_user_repository() -> MagicMock:
    """Фикстура для мокированного UserRepository."""
    return MagicMock(spec=UserRepository)


@pytest.fixture
def user_app_service(mock_user_repository: MagicMock) -> UserApplicationService:
    """Фикстура для UserApplicationService с мокированным репозиторием."""
    return UserApplicationService(user_repository=mock_user_repository)


@pytest.fixture
def real_user_repository() -> InMemoryUserRepository:
    """Фикстура для реального InMemoryUserRepository."""
    return InMemoryUserRepository()


@pytest.fixture
def user_app_service_with_real_repo(
    real_user_repository: InMemoryUserRepository,
) -> UserApplicationService:
    """Фикстура для UserApplicationService с реальным репозиторием."""
    return UserApplicationService(user_repository=real_user_repository)


@pytest.fixture
def user_controller(
    user_app_service_with_real_repo: UserApplicationService,
) -> UserController:
    """Фикстура для UserController с реальными зависимостями."""
    return UserController(user_service=user_app_service_with_real_repo)


@pytest.fixture
def sample_user_id() -> UserId:
    return UserId()


@pytest.fixture
def sample_user(sample_user_id: UserId) -> User:
    return User(id=sample_user_id, username="testuser", email="test@example.com")


# ==============================================================================
# Юнит-тесты для UserApplicationService
# ==============================================================================


class TestUserApplicationService:
    def test_register_user_success(
        self, user_app_service: UserApplicationService, mock_user_repository: MagicMock
    ):
        """Тест успешной регистрации пользователя."""
        command = RegisterUserCommand(username="newuser", email="new@example.com")
        mock_user_repository.find_by_email.return_value = None  # Email не занят

        user_id = user_app_service.register_user(command)

        assert isinstance(user_id, UserId)
        mock_user_repository.find_by_email.assert_called_once_with("new@example.com")
        mock_user_repository.save.assert_called_once()
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.username == "newuser"
        assert saved_user.email == "new@example.com"
        assert saved_user.id == user_id

    def test_register_user_email_exists(
        self,
        user_app_service: UserApplicationService,
        mock_user_repository: MagicMock,
        sample_user: User,
    ):
        """Тест регистрации пользователя, если email уже существует."""
        command = RegisterUserCommand(username="anotheruser", email=sample_user.email)
        mock_user_repository.find_by_email.return_value = sample_user  # Email занят

        with pytest.raises(
            ValidationException,
            match=f"Пользователь с email {sample_user.email} уже существует.",
        ):
            user_app_service.register_user(command)

        mock_user_repository.find_by_email.assert_called_once_with(sample_user.email)
        mock_user_repository.save.assert_not_called()

    def test_register_user_invalid_input(
        self, user_app_service: UserApplicationService
    ):
        """Тест регистрации с невалидными данными."""
        command = RegisterUserCommand(username="", email="test@example.com")
        with pytest.raises(
            ValidationException, match="Имя пользователя и email обязательны."
        ):
            user_app_service.register_user(command)

    def test_get_user_details_success(
        self,
        user_app_service: UserApplicationService,
        mock_user_repository: MagicMock,
        sample_user: User,
    ):
        """Тест успешного получения деталей пользователя."""
        mock_user_repository.get_by_id.return_value = sample_user
        user_id_str = str(sample_user.id.value)

        dto = user_app_service.get_user_details(user_id_str)

        assert isinstance(dto, UserDetailsDTO)
        assert dto.id == user_id_str
        assert dto.username == sample_user.username
        assert dto.email == sample_user.email
        assert dto.is_active == sample_user.is_active
        mock_user_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_get_user_details_not_found(
        self, user_app_service: UserApplicationService, mock_user_repository: MagicMock
    ):
        """Тест получения деталей несуществующего пользователя."""
        unknown_id = UserId()
        mock_user_repository.get_by_id.return_value = None

        dto = user_app_service.get_user_details(str(unknown_id.value))

        assert dto is None
        mock_user_repository.get_by_id.assert_called_once_with(unknown_id)

    def test_get_user_details_invalid_id_format(
        self, user_app_service: UserApplicationService
    ):
        """Тест получения деталей с невалидным форматом ID."""
        with pytest.raises(
            ValidationException, match="Некорректный формат ID пользователя."
        ):
            user_app_service.get_user_details("invalid-uuid")

    def test_deactivate_user_success(
        self,
        user_app_service: UserApplicationService,
        mock_user_repository: MagicMock,
        sample_user: User,
    ):
        """Тест успешной деактивации пользователя."""
        initial_user_state = User(
            id=sample_user.id,
            username=sample_user.username,
            email=sample_user.email,
            is_active=True,
        )
        mock_user_repository.get_by_id.return_value = initial_user_state
        user_id_str = str(initial_user_state.id.value)

        user_app_service.deactivate_user(user_id_str)

        mock_user_repository.get_by_id.assert_called_once_with(initial_user_state.id)
        assert not initial_user_state.is_active  # Проверяем, что состояние изменилось
        mock_user_repository.save.assert_called_once_with(initial_user_state)

    def test_deactivate_user_not_found(
        self, user_app_service: UserApplicationService, mock_user_repository: MagicMock
    ):
        """Тест деактивации несуществующего пользователя."""
        unknown_id = UserId()
        unknown_id_str = str(unknown_id.value)
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(
            EntityNotFoundException,
            match=f"Пользователь с ID {unknown_id_str} не найден для деактивации.",
        ):
            user_app_service.deactivate_user(unknown_id_str)

        mock_user_repository.get_by_id.assert_called_once_with(unknown_id)
        mock_user_repository.save.assert_not_called()

    def test_deactivate_user_invalid_id_format(
        self, user_app_service: UserApplicationService
    ):
        """Тест деактивации с невалидным форматом ID."""
        with pytest.raises(
            ValidationException, match="Некорректный формат ID пользователя."
        ):
            user_app_service.deactivate_user("invalid-uuid")


# ==============================================================================
# Интеграционные тесты для UserController (с реальными зависимостями)
# ==============================================================================


class TestUserControllerIntegration:
    def test_full_user_lifecycle(
        self,
        user_controller: UserController,
        real_user_repository: InMemoryUserRepository,
    ):
        """Тест полного жизненного цикла пользователя через контроллер."""
        username = "FullLifecycleUser"
        email = "lifecycle@example.com"

        # 1. Регистрация
        register_response = user_controller.handle_register_user_request(
            username, email
        )
        assert register_response["status"] == "success"
        user_id_str = register_response["user_id"]
        assert uuid.UUID(user_id_str)  # Проверка, что ID - валидный UUID

        # Проверка, что пользователь сохранен в репозитории
        user_id_obj = UserId(value=uuid.UUID(user_id_str))
        saved_user = real_user_repository.get_by_id(user_id_obj)
        assert saved_user is not None
        assert saved_user.username == username
        assert saved_user.email == email
        assert saved_user.is_active

        # 2. Получение деталей
        details_response = user_controller.handle_get_user_details_request(user_id_str)
        assert details_response["status"] == "success"
        user_data = details_response["data"]
        assert user_data["id"] == user_id_str
        assert user_data["username"] == username
        assert user_data["email"] == email
        assert user_data["is_active"]

        # 3. Деактивация
        deactivate_response = user_controller.handle_deactivate_user_request(
            user_id_str
        )
        assert deactivate_response["status"] == "success"

        # Проверка, что пользователь деактивирован в репозитории
        deactivated_user = real_user_repository.get_by_id(user_id_obj)
        assert deactivated_user is not None
        assert not deactivated_user.is_active

        # Повторное получение деталей для проверки статуса
        details_after_deactivation = user_controller.handle_get_user_details_request(
            user_id_str
        )
        assert details_after_deactivation["status"] == "success"
        assert not details_after_deactivation["data"]["is_active"]

    def test_register_user_duplicate_email_controller(
        self, user_controller: UserController
    ):
        """Тест попытки регистрации с дублирующимся email через контроллер."""
        username1 = "UserOne"
        username2 = "UserTwo"
        email = "duplicate.controller@example.com"

        # Первая регистрация - успешная
        response1 = user_controller.handle_register_user_request(username1, email)
        assert response1["status"] == "success"

        # Вторая регистрация с тем же email - ошибка
        response2 = user_controller.handle_register_user_request(username2, email)
        assert response2["status"] == "error"
        assert f"Пользователь с email {email} уже существует" in response2["message"]

    def test_get_non_existent_user_controller(self, user_controller: UserController):
        """Тест запроса деталей несуществующего пользователя через контроллер."""
        non_existent_id = str(uuid.uuid4())
        response = user_controller.handle_get_user_details_request(non_existent_id)
        assert response["status"] == "not_found"

    def test_deactivate_non_existent_user_controller(
        self, user_controller: UserController
    ):
        """Тест попытки деактивации несуществующего пользователя через контроллер."""
        non_existent_id = str(uuid.uuid4())
        response = user_controller.handle_deactivate_user_request(non_existent_id)
        assert response["status"] == "error"
        assert (
            f"Пользователь с ID {non_existent_id} не найден для деактивации"
            in response["message"]
        )

    def test_invalid_uuid_format_controller(self, user_controller: UserController):
        """Тест запросов с невалидным форматом UUID через контроллер."""
        invalid_id = "not-a-uuid"

        # Получение деталей
        details_response = user_controller.handle_get_user_details_request(invalid_id)
        assert details_response["status"] == "error"
        assert "Некорректный формат ID пользователя" in details_response["message"]

        # Деактивация
        deactivate_response = user_controller.handle_deactivate_user_request(invalid_id)
        assert deactivate_response["status"] == "error"
        assert "Некорректный формат ID пользователя" in deactivate_response["message"]
