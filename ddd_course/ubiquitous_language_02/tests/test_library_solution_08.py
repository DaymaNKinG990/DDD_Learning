"""
Тесты для решения упражнения по системе управления библиотекой.
"""

from datetime import date, timedelta
from typing import Type
from uuid import UUID, uuid4

import pytest

# Импортируем классы из файла с решением
from ddd_course.ubiquitous_language_02.library_solution_08 import (
    ISBN,
    Book,
    Checkout,
    CheckoutStatus,
    Email,  # Добавляем импорт Email, если он используется
    LibraryService,
    Patron,
    PatronStatus,
)

# Если Email определен в library_solution_08.py только в блоке
# if __name__ == '__main__':
# то для тестов его нужно либо вынести на уровень модуля,
# либо определить здесь мок-версию.
# Для простоты, если он не вынесен, можно определить здесь:
try:
    from ddd_course.ubiquitous_language_02.library_solution_08 import Email
except ImportError:

    @pytest.fixture
    def Email() -> Type:  # type: ignore
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class MockEmail:
            address: str

        return MockEmail


@pytest.fixture
def sample_isbn() -> ISBN:
    return ISBN(value="978-3-16-148410-0")


@pytest.fixture
def sample_book(sample_isbn: ISBN) -> Book:
    return Book(
        title="Sample Book for Testing",
        authors=["Author Test"],
        isbn=sample_isbn,
        publication_year=2024,
        total_copies=3,
        available_copies=3,
    )


@pytest.fixture
def another_book() -> Book:
    return Book(title="Another Test Book", total_copies=1, available_copies=1)


@pytest.fixture
def unavailable_book() -> Book:
    return Book(title="Unavailable Book", total_copies=1, available_copies=0)


@pytest.fixture
def active_patron(Email) -> Patron:  # type: ignore
    return Patron(
        first_name="Active",
        last_name="Patron",
        email=Email("active@example.com"),
        status=PatronStatus.ACTIVE,
    )


@pytest.fixture
def blocked_patron(Email) -> Patron:  # type: ignore
    return Patron(
        first_name="Blocked",
        last_name="Patron",
        email=Email("blocked@example.com"),
        status=PatronStatus.BLOCKED,
    )


@pytest.fixture
def library_service(
    sample_book: Book,
    active_patron: Patron,
    another_book: Book,
    unavailable_book: Book,
    blocked_patron: Patron,
) -> LibraryService:
    return LibraryService(
        books=[sample_book, another_book, unavailable_book],
        patrons=[active_patron, blocked_patron],
        checkouts=[],
    )


class TestBook:
    def test_book_creation(self, sample_book: Book, sample_isbn: ISBN):
        assert sample_book.title == "Sample Book for Testing"
        assert sample_book.authors == ["Author Test"]
        assert sample_book.isbn == sample_isbn
        assert sample_book.publication_year == 2024
        assert sample_book.total_copies == 3
        assert sample_book.available_copies == 3
        assert isinstance(sample_book.id, UUID)

    def test_book_creation_invalid_copies(self):
        with pytest.raises(ValueError):
            Book(title="Test", total_copies=1, available_copies=2)
        with pytest.raises(ValueError):
            Book(title="Test", total_copies=-1)

    def test_book_can_checkout(self, sample_book: Book, unavailable_book: Book):
        assert sample_book.can_checkout() is True
        assert unavailable_book.can_checkout() is False

    def test_book_checkout(self, sample_book: Book):
        sample_book.checkout()
        assert sample_book.available_copies == 2
        sample_book.checkout()
        assert sample_book.available_copies == 1

    def test_book_checkout_unavailable(self, unavailable_book: Book):
        with pytest.raises(ValueError, match="Нет доступных экземпляров для выдачи"):
            unavailable_book.checkout()

    def test_book_return_copy(self, sample_book: Book):
        sample_book.checkout()  # available = 2
        sample_book.return_copy()  # available = 3
        assert sample_book.available_copies == 3
        # Test returning when all copies are already in
        # (should not increase beyond total)
        sample_book.return_copy()
        assert sample_book.available_copies == 3


class TestPatron:
    def test_patron_creation(self, active_patron: Patron, Email):  # type: ignore
        assert active_patron.first_name == "Active"
        assert active_patron.last_name == "Patron"
        assert active_patron.email == Email("active@example.com")
        assert active_patron.status == PatronStatus.ACTIVE
        assert active_patron.full_name == "Active Patron"

    def test_patron_can_borrow(self, active_patron: Patron, blocked_patron: Patron):
        assert active_patron.can_borrow() is True
        assert blocked_patron.can_borrow() is False


class TestCheckout:
    def test_checkout_creation(self, sample_book: Book, active_patron: Patron):
        checkout = Checkout(book_id=sample_book.id, patron_id=active_patron.id)
        assert checkout.book_id == sample_book.id
        assert checkout.patron_id == active_patron.id
        assert checkout.checkout_date == date.today()
        assert checkout.due_date == date.today() + timedelta(weeks=2)
        assert checkout.status == CheckoutStatus.ACTIVE

    def test_checkout_mark_as_returned(self, sample_book: Book, active_patron: Patron):
        checkout = Checkout(book_id=sample_book.id, patron_id=active_patron.id)
        checkout.mark_as_returned()
        assert checkout.return_date == date.today()
        assert checkout.status == CheckoutStatus.COMPLETED

    def test_checkout_check_if_overdue(self, sample_book: Book, active_patron: Patron):
        checkout = Checkout(book_id=sample_book.id, patron_id=active_patron.id)
        # Simulate overdue
        checkout.due_date = date.today() - timedelta(days=1)
        checkout.check_if_overdue()
        assert checkout.status == CheckoutStatus.OVERDUE

        # Simulate not overdue
        checkout.status = CheckoutStatus.ACTIVE
        checkout.due_date = date.today() + timedelta(days=1)
        checkout.check_if_overdue()
        assert checkout.status == CheckoutStatus.ACTIVE


class TestLibraryService:
    def test_checkout_book_success(
        self, library_service: LibraryService, sample_book: Book, active_patron: Patron
    ):
        checkout = library_service.checkout_book(sample_book.id, active_patron.id)
        assert checkout.book_id == sample_book.id
        assert checkout.patron_id == active_patron.id
        assert sample_book.available_copies == 2  # Was 3
        assert checkout.id in library_service._checkouts

    def test_checkout_book_unavailable(
        self,
        library_service: LibraryService,
        unavailable_book: Book,
        active_patron: Patron,
    ):
        with pytest.raises(
            ValueError, match=f"Книга '{unavailable_book.title}' недоступна для выдачи"
        ):
            library_service.checkout_book(unavailable_book.id, active_patron.id)

    def test_checkout_book_patron_blocked(
        self, library_service: LibraryService, sample_book: Book, blocked_patron: Patron
    ):
        with pytest.raises(
            ValueError,
            match=f"Читатель {blocked_patron.full_name} заблокирован и не может "
            f"брать книги",
        ):
            library_service.checkout_book(sample_book.id, blocked_patron.id)

    def test_checkout_book_not_found(
        self, library_service: LibraryService, active_patron: Patron
    ):
        non_existent_book_id = uuid4()
        with pytest.raises(
            ValueError, match=f"Книга с ID {non_existent_book_id} не найдена"
        ):
            library_service.checkout_book(non_existent_book_id, active_patron.id)

    def test_return_book_success(
        self, library_service: LibraryService, sample_book: Book, active_patron: Patron
    ):
        checkout = library_service.checkout_book(sample_book.id, active_patron.id)
        assert sample_book.available_copies == 2

        library_service.return_book(checkout.id)
        assert checkout.status == CheckoutStatus.COMPLETED
        assert sample_book.available_copies == 3

    def test_return_book_already_returned(
        self, library_service: LibraryService, sample_book: Book, active_patron: Patron
    ):
        checkout = library_service.checkout_book(sample_book.id, active_patron.id)
        library_service.return_book(checkout.id)
        with pytest.raises(ValueError, match="Эта книга уже была возвращена"):
            library_service.return_book(checkout.id)

    def test_return_book_checkout_not_found(self, library_service: LibraryService):
        non_existent_checkout_id = uuid4()
        with pytest.raises(
            ValueError,
            match=f"Запись о выдаче с ID {non_existent_checkout_id} не найдена",
        ):
            library_service.return_book(non_existent_checkout_id)

    def test_integration_multiple_checkouts_and_returns(
        self,
        library_service: LibraryService,
        sample_book: Book,
        another_book: Book,
        active_patron: Patron,
    ):
        # Patron checks out sample_book
        checkout1 = library_service.checkout_book(sample_book.id, active_patron.id)
        assert sample_book.available_copies == 2

        # Patron checks out another_book
        checkout2 = library_service.checkout_book(another_book.id, active_patron.id)
        assert another_book.available_copies == 0

        # Patron returns sample_book
        library_service.return_book(checkout1.id)
        assert sample_book.available_copies == 3
        assert checkout1.status == CheckoutStatus.COMPLETED

        # Patron returns another_book
        library_service.return_book(checkout2.id)
        assert another_book.available_copies == 1
        assert checkout2.status == CheckoutStatus.COMPLETED
