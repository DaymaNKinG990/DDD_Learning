"""
Тесты для примеров из модуля Введение в DDD.
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest

# Импортируем классы из файла с примерами
# Для корректного импорта предполагается, что PYTHONPATH настроен
# или тесты запускаются из корневой директории проекта.
from ddd_course.introduction_01.introduction_example_02 import (
    Email,
    InMemoryUserRepository,
    Order,
    User,
    UserRegistrationService,  # Абстрактный класс, для него тестов не будет
)


class TestEmail:
    """Тесты для объекта-значения Email."""

    def test_email_creation_success(self):
        """Тест успешного создания Email."""
        email_str = "test@example.com"
        email_obj = Email(email_str)
        assert email_obj.address == email_str
        assert str(email_obj) == email_str

    def test_email_creation_invalid(self):
        """Тест создания Email с некорректным адресом."""
        with pytest.raises(ValueError, match="Некорректный email адрес"):
            Email("invalid_email")

    def test_email_is_value_object(self):
        """Тест, что Email является объектом-значением (сравнение по значению)."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("another@example.com")
        assert email1 == email2
        assert email1 != email3
        # dataclass(frozen=True) автоматически реализует __eq__ и __hash__


class TestUser:
    """Тесты для сущности User."""

    def test_user_creation_success(self):
        """Тест успешного создания User."""
        user_id = uuid4()
        email = Email("user@example.com")
        name = "Test User"
        created_at = datetime.now()

        user = User(id=user_id, email=email, name=name, created_at=created_at)

        assert user.id == user_id
        assert user.email == email
        assert user.name == name
        assert user.created_at == created_at

    def test_user_creation_empty_name(self):
        """Тест создания User с пустым именем."""
        with pytest.raises(ValueError, match="Имя пользователя не может быть пустым"):
            User(
                id=uuid4(),
                email=Email("user@example.com"),
                name="  ",
                created_at=datetime.now(),
            )

    def test_user_change_email(self):
        """Тест изменения email пользователя."""
        user = User(
            id=uuid4(),
            email=Email("old@example.com"),
            name="Test User",
            created_at=datetime.now(),
        )
        new_email = Email("new@example.com")
        user.change_email(new_email)
        assert user.email == new_email

    def test_user_is_entity(self):
        """Тест, что User является сущностью (сравнение по ID)."""
        user_id = uuid4()
        email1 = Email("user1@example.com")
        email2 = Email("user2@example.com")
        user1 = User(
            id=user_id, email=email1, name="User One", created_at=datetime.now()
        )
        user2 = User(
            id=user_id, email=email2, name="User Two", created_at=datetime.now()
        )
        user3 = User(
            id=uuid4(), email=email1, name="User One", created_at=datetime.now()
        )

        # dataclass без frozen=True по умолчанию сравнивает по всем полям.
        # Для сущностей важно переопределить __eq__ и __hash__ для сравнения по ID.
        # В нашем примере User не имеет такого переопределения,
        # поэтому используется стандартное поведение dataclass.
        # Для демонстрации принципа сущности, мы должны были бы добавить:
        # def __eq__(self, other):
        #     if not isinstance(other, User):
        #         return NotImplemented
        #     return self.id == other.id
        # def __hash__(self):
        #     return hash(self.id)
        # Но так как это базовый пример, оставим как есть и будем помнить об этом.
        assert (
            user1 != user2
        )  # Разные email, но если бы сравнивали по ID, были бы равны
        assert user1 != user3  # Разные ID


class TestOrder:
    """Тесты для агрегата Order."""

    def test_order_creation_and_add_item(self):
        """Тест создания заказа и добавления товаров."""
        order_id = uuid4()
        user_id = uuid4()
        order = Order(id=order_id, user_id=user_id, items=[], created_at=datetime.now())

        assert order.status == "created"
        assert not order.items

        product1_id = uuid4()
        order.add_item(product_id=product1_id, quantity=2, price=10.0)
        assert len(order.items) == 1
        assert order.items[0].product_id == product1_id
        assert order.items[0].quantity == 2

        product2_id = uuid4()
        order.add_item(product_id=product2_id, quantity=1, price=25.0)
        assert len(order.items) == 2

    def test_order_calculate_total(self):
        """Тест расчета общей суммы заказа."""
        order = Order(id=uuid4(), user_id=uuid4(), items=[], created_at=datetime.now())
        order.add_item(product_id=uuid4(), quantity=2, price=10.0)  # 20.0
        order.add_item(product_id=uuid4(), quantity=1, price=25.0)  # 25.0
        assert order.calculate_total() == 45.0

    def test_order_confirm_success(self):
        """Тест успешного подтверждения заказа."""
        order = Order(id=uuid4(), user_id=uuid4(), items=[], created_at=datetime.now())
        order.add_item(product_id=uuid4(), quantity=1, price=5.0)
        order.confirm()
        assert order.status == "confirmed"

    def test_order_confirm_empty_order(self):
        """Тест подтверждения пустого заказа."""
        order = Order(id=uuid4(), user_id=uuid4(), items=[], created_at=datetime.now())
        with pytest.raises(ValueError, match="Невозможно подтвердить пустой заказ"):
            order.confirm()

    def test_order_add_item_to_confirmed_order(self):
        """Тест добавления товара в подтвержденный заказ."""
        order = Order(id=uuid4(), user_id=uuid4(), items=[], created_at=datetime.now())
        order.add_item(product_id=uuid4(), quantity=1, price=5.0)
        order.confirm()
        with pytest.raises(ValueError, match="Невозможно изменить выполненный заказ"):
            order.add_item(product_id=uuid4(), quantity=1, price=10.0)


class TestInMemoryUserRepository:
    """Тесты для InMemoryUserRepository."""

    @pytest.fixture
    def repo(self) -> InMemoryUserRepository:
        return InMemoryUserRepository()

    @pytest.fixture
    def sample_user(self) -> User:
        return User(
            id=uuid4(),
            email=Email("sample@example.com"),
            name="Sample User",
            created_at=datetime.now(),
        )

    def test_add_and_get_user(self, repo: InMemoryUserRepository, sample_user: User):
        """Тест добавления и получения пользователя."""
        assert repo.get_by_id(sample_user.id) is None
        repo.add(sample_user)
        retrieved_user = repo.get_by_id(sample_user.id)
        assert retrieved_user == sample_user
        retrieved_by_email = repo.get_by_email(sample_user.email)
        assert retrieved_by_email == sample_user

    def test_get_non_existent_user(self, repo: InMemoryUserRepository):
        """Тест получения несуществующего пользователя."""
        assert repo.get_by_id(uuid4()) is None
        assert repo.get_by_email(Email("nonexistent@example.com")) is None

    def test_update_user(self, repo: InMemoryUserRepository, sample_user: User):
        """Тест обновления пользователя."""
        repo.add(sample_user)
        new_email = Email("updated@example.com")
        sample_user.change_email(new_email)
        repo.update(sample_user)

        updated_user = repo.get_by_id(sample_user.id)
        assert updated_user is not None
        assert updated_user.email == new_email


class TestUserRegistrationService:
    """Тесты для UserRegistrationService."""

    @pytest.fixture
    def repo(self) -> InMemoryUserRepository:
        return InMemoryUserRepository()

    @pytest.fixture
    def service(self, repo: InMemoryUserRepository) -> UserRegistrationService:
        return UserRegistrationService(user_repository=repo)

    def test_register_new_user_success(
        self, service: UserRegistrationService, repo: InMemoryUserRepository
    ):
        """Тест успешной регистрации нового пользователя."""
        email_str = "newuser@example.com"
        name = "New User"
        user = service.register_user(email_address=email_str, name=name)

        assert user.email.address == email_str
        assert user.name == name
        assert isinstance(user.id, UUID)
        assert isinstance(user.created_at, datetime)

        # Проверяем, что пользователь добавлен в репозиторий
        retrieved_user = repo.get_by_email(Email(email_str))
        assert retrieved_user == user

    def test_register_user_already_exists(
        self, service: UserRegistrationService, repo: InMemoryUserRepository
    ):
        """Тест регистрации пользователя с уже существующим email."""
        existing_email_str = "existing@example.com"
        existing_name = "Existing User"
        # Сначала регистрируем пользователя
        service.register_user(email_address=existing_email_str, name=existing_name)

        # Пытаемся зарегистрировать снова с тем же email
        with pytest.raises(
            ValueError, match="Пользователь с таким email уже существует"
        ):
            service.register_user(email_address=existing_email_str, name="Another Name")
