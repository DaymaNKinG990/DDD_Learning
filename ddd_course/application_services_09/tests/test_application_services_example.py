"""
Тесты для примеров из модуля "Сервисы приложения (Application Services)".

Проверяют UserApplicationService:
- Регистрацию пользователя.
- Изменение email пользователя.
- Получение деталей пользователя.
- Обработку ошибок и граничных случаев.
- Взаимодействие с репозиторием (с использованием моков и реальной InMemory реализации).
"""

import uuid
from unittest.mock import (  # Используем MagicMock для более гибкого мокирования
    MagicMock,
)

import pytest

from ddd_course.application_services_09.application_services_example_02 import (
    ChangeUserEmailCommand,
    InMemoryUserRepository,  # Для интеграционных тестов с реальным репозиторием
    RegisterUserCommand,
    Repository,  # Для типизации мока
    User,
    UserApplicationService,
    UserDTO,
    UserId,
    UserNotFoundException,
    UserRegistrationException,
)


@pytest.fixture
def mock_user_repo() -> MagicMock:
    """Фикстура для мокированного репозитория пользователей."""
    repo = MagicMock(spec=Repository[UserId, User])
    repo.get_by_id.return_value = None  # По умолчанию пользователь не найден
    return repo


@pytest.fixture
def real_user_repo() -> InMemoryUserRepository:
    """Фикстура для реального InMemoryUserRepository."""
    return InMemoryUserRepository()


@pytest.fixture
def user_service(mock_user_repo: MagicMock) -> UserApplicationService:
    """Фикстура для сервиса приложения с мокированным репозиторием."""
    return UserApplicationService(user_repository=mock_user_repo)


@pytest.fixture
def user_service_with_real_repo(
    real_user_repo: InMemoryUserRepository,
) -> UserApplicationService:
    """Фикстура для сервиса приложения с реальным InMemoryUserRepository."""
    return UserApplicationService(user_repository=real_user_repo)


@pytest.fixture
def sample_user_id() -> UserId:
    return UserId(value=uuid.uuid4())


@pytest.fixture
def sample_user(sample_user_id: UserId) -> User:
    return User(
        id=sample_user_id, username="testuser", email="test@example.com", version=1
    )


class TestUserApplicationService:
    """Тесты для UserApplicationService."""

    def test_register_user_success(
        self, user_service: UserApplicationService, mock_user_repo: MagicMock
    ):
        command = RegisterUserCommand(username="NewUser", email="new@example.com")

        # Мокируем list_all, если бы проверка на уникальность была активна
        # mock_user_repo.list_all.return_value = []

        user_id = user_service.register_user(command)

        assert isinstance(user_id, UserId)
        # Проверяем, что save был вызван с корректным объектом User
        # Используем call для проверки аргументов, так как user_id генерируется внутри
        assert mock_user_repo.save.call_count == 1
        saved_user_arg = mock_user_repo.save.call_args[0][0]
        assert isinstance(saved_user_arg, User)
        assert saved_user_arg.id == user_id
        assert saved_user_arg.username == "NewUser"
        assert saved_user_arg.email == "new@example.com"
        assert saved_user_arg.version == 1

    def test_register_user_empty_username(self, user_service: UserApplicationService):
        command = RegisterUserCommand(username="", email="new@example.com")
        with pytest.raises(
            UserRegistrationException,
            match="Имя пользователя и email не могут быть пустыми.",
        ):
            user_service.register_user(command)

    def test_register_user_empty_email(self, user_service: UserApplicationService):
        command = RegisterUserCommand(username="NewUser", email="")
        with pytest.raises(
            UserRegistrationException,
            match="Имя пользователя и email не могут быть пустыми.",
        ):
            user_service.register_user(command)

    # Тест на дубликат email пока не нужен, т.к. логика закомментирована в сервисе
    # def test_register_user_duplicate_email(
    #     self, user_service: UserApplicationService, mock_user_repo: MagicMock,
    #     sample_user: User
    # ):
    #     # Предположим, пользователь с таким email уже есть
    #     mock_user_repo.list_all.return_value = [sample_user]
    #     command = RegisterUserCommand(username="AnotherUser", email=sample_user.email)
    #     with pytest.raises(
    #         UserRegistrationException,
    #         match=f"Пользователь с email {sample_user.email} уже существует."
    #     ):
    #         user_service.register_user(command)

    def test_get_user_details_success(
        self,
        user_service: UserApplicationService,
        mock_user_repo: MagicMock,
        sample_user: User,
        sample_user_id: UserId,
    ):
        mock_user_repo.get_by_id.return_value = sample_user

        user_dto = user_service.get_user_details(sample_user_id)

        assert user_dto is not None
        assert isinstance(user_dto, UserDTO)
        assert user_dto.id == str(sample_user_id.value)
        assert user_dto.username == sample_user.username
        assert user_dto.email == sample_user.email
        assert user_dto.version == sample_user.version
        mock_user_repo.get_by_id.assert_called_once_with(sample_user_id)

    def test_get_user_details_not_found(
        self,
        user_service: UserApplicationService,
        mock_user_repo: MagicMock,
        sample_user_id: UserId,
    ):
        mock_user_repo.get_by_id.return_value = (
            None  # Явно указываем, что пользователь не найден
        )

        user_dto = user_service.get_user_details(sample_user_id)

        assert user_dto is None
        mock_user_repo.get_by_id.assert_called_once_with(sample_user_id)

    def test_change_user_email_success(
        self,
        user_service: UserApplicationService,
        mock_user_repo: MagicMock,
        sample_user: User,
        sample_user_id: UserId,
    ):
        mock_user_repo.get_by_id.return_value = sample_user
        new_email = "updated@example.com"
        command = ChangeUserEmailCommand(user_id=sample_user_id, new_email=new_email)

        user_service.change_user_email(command)

        mock_user_repo.get_by_id.assert_called_once_with(sample_user_id)
        # Проверяем, что save был вызван с обновленным User
        assert mock_user_repo.save.call_count == 1
        saved_user_arg = mock_user_repo.save.call_args[0][0]
        assert isinstance(saved_user_arg, User)
        assert saved_user_arg.id == sample_user_id
        assert saved_user_arg.email == new_email
        assert (
            saved_user_arg.version == sample_user.version + 1
        )  # Версия должна инкрементироваться

    def test_change_user_email_user_not_found(
        self,
        user_service: UserApplicationService,
        mock_user_repo: MagicMock,
        sample_user_id: UserId,
    ):
        mock_user_repo.get_by_id.return_value = None
        command = ChangeUserEmailCommand(
            user_id=sample_user_id, new_email="any@example.com"
        )

        with pytest.raises(
            UserNotFoundException,
            match=f"Пользователь с ID {sample_user_id.value} не найден.",
        ):
            user_service.change_user_email(command)
        # Save не должен вызываться, если пользователь не найден
        mock_user_repo.save.assert_not_called()

    def test_change_user_email_empty_email_string(
        self,
        user_service: UserApplicationService,
        mock_user_repo: MagicMock,
        sample_user: User,
        sample_user_id: UserId,
    ):
        mock_user_repo.get_by_id.return_value = sample_user
        command = ChangeUserEmailCommand(user_id=sample_user_id, new_email="")

        with pytest.raises(
            UserRegistrationException,
            match="Ошибка изменения email: Email не может быть пустым.",
        ):
            user_service.change_user_email(command)
        # Save не должен вызываться при ошибке валидации
        mock_user_repo.save.assert_not_called()

    # Интеграционные тесты с реальным InMemoryUserRepository
    def test_integration_register_and_get_user(
        self, user_service_with_real_repo: UserApplicationService
    ):
        username = "IntegratedUser"
        email = "integrated@example.com"
        register_cmd = RegisterUserCommand(username=username, email=email)

        user_id = user_service_with_real_repo.register_user(register_cmd)
        assert isinstance(user_id, UserId)

        user_details = user_service_with_real_repo.get_user_details(user_id)
        assert user_details is not None
        assert user_details.username == username
        assert user_details.email == email
        assert user_details.id == str(user_id.value)
        assert user_details.version == 1

    def test_integration_register_change_email_and_get_user(
        self,
        user_service_with_real_repo: UserApplicationService,
        real_user_repo: InMemoryUserRepository,
    ):
        # 1. Register
        username = "ChangeEmailUser"
        initial_email = "change_me@example.com"
        register_cmd = RegisterUserCommand(username=username, email=initial_email)
        user_id = user_service_with_real_repo.register_user(register_cmd)

        # 2. Change Email
        new_email = "changed@example.com"
        change_email_cmd = ChangeUserEmailCommand(user_id=user_id, new_email=new_email)
        user_service_with_real_repo.change_user_email(change_email_cmd)

        # 3. Get User and verify
        user_details = user_service_with_real_repo.get_user_details(user_id)
        assert user_details is not None
        assert user_details.email == new_email
        assert user_details.version == 2  # Версия должна увеличиться

        # Проверка напрямую в репозитории (для уверенности)
        stored_user = real_user_repo.get_by_id(user_id)
        assert stored_user is not None
        assert stored_user.email == new_email
        assert stored_user.version == 2
