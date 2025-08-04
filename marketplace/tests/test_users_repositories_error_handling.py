"""Tests for error handling in users repositories."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DataError

from src.users.infrastructure.repositories import UserRepository
from src.users.domain.entities import User
from src.users.domain.value_objects import UserId, Email, Username
from src.users.domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidUserDataError,
)
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError


class TestUserRepositoryErrorHandling:
    """Test error handling scenarios in user repositories."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def user_repository(self, mock_session):
        """Create user repository instance."""
        return UserRepository(mock_session)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(
            id=UserId("test-user-id"),
            username=Username("testuser"),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User"
        )

    async def test_get_by_email_not_found(self, user_repository, mock_session):
        """Test getting user by email when user not found."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await user_repository.get_by_email(Email("nonexistent@example.com"))

    async def test_get_by_email_invalid_format(self, user_repository, mock_session):
        """Test getting user by email with invalid email format."""
        # Arrange
        mock_session.execute.side_effect = DataError("Invalid email format", None, None)
        
        # Act & Assert
        with pytest.raises(DataError):
            await user_repository.get_by_email(Email("invalid_email"))

    async def test_get_by_email_database_error(self, user_repository, mock_session):
        """Test getting user by email with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database connection error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.get_by_email(Email("test@example.com"))

    async def test_get_by_username_not_found(self, user_repository, mock_session):
        """Test getting user by username when user not found."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await user_repository.get_by_username(Username("nonexistentuser"))

    async def test_get_by_username_empty_username(self, user_repository, mock_session):
        """Test getting user by username with empty username."""
        # Arrange
        mock_session.execute.side_effect = ValueError("Username cannot be empty")
        
        # Act & Assert
        with pytest.raises(ValueError):
            await user_repository.get_by_username(Username(""))

    async def test_get_by_username_database_error(self, user_repository, mock_session):
        """Test getting user by username with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.get_by_username(Username("testuser"))

    async def test_save_duplicate_email(self, user_repository, mock_session, sample_user):
        """Test saving user with duplicate email."""
        # Arrange
        mock_session.add.side_effect = IntegrityError("duplicate key value violates unique constraint", None, None)
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError, match="User with this email already exists"):
            await user_repository.save(sample_user)

    async def test_save_duplicate_username(self, user_repository, mock_session, sample_user):
        """Test saving user with duplicate username."""
        # Arrange
        mock_session.add.side_effect = IntegrityError("duplicate key value violates unique constraint", None, None)
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError, match="Username already taken"):
            await user_repository.save(sample_user)

    async def test_save_invalid_user_data(self, user_repository, mock_session, sample_user):
        """Test saving user with invalid data."""
        # Arrange
        mock_session.add.side_effect = IntegrityError("check constraint", None, None)
        
        # Act & Assert
        with pytest.raises(InvalidUserDataError, match="Invalid user data"):
            await user_repository.save(sample_user)

    async def test_save_database_error(self, user_repository, mock_session, sample_user):
        """Test saving user with database error."""
        # Arrange
        mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.save(sample_user)

    async def test_save_rollback_on_error(self, user_repository, mock_session, sample_user):
        """Test rollback when save fails."""
        # Arrange
        mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.save(sample_user)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()

    async def test_update_not_found(self, user_repository, mock_session, sample_user):
        """Test updating non-existent user."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await user_repository.update(sample_user)

    async def test_update_invalid_data(self, user_repository, mock_session, sample_user):
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user
        mock_session.flush.side_effect = IntegrityError("Invalid data", None, None)
        
        # Act & Assert
        with pytest.raises(InvalidUserDataError, match="Invalid user data"):
            await user_repository.update(sample_user)

    async def test_update_email_conflict(self, user_repository, mock_session, sample_user):
        """Test updating user with email that already exists."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user
        mock_session.flush.side_effect = IntegrityError("duplicate key value", None, None)
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError, match="Email already in use"):
            await user_repository.update(sample_user)

    async def test_update_database_error(self, user_repository, mock_session, sample_user):
        """Test updating user with database error."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user
        mock_session.flush.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.update(sample_user)

    async def test_delete_not_found(self, user_repository, mock_session):
        """Test deleting non-existent user."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await user_repository.delete(UserId("non_existent_user"))

    async def test_delete_with_active_orders(self, user_repository, mock_session):
        """Test deleting user with active orders."""
        # Arrange
        user = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = user
        mock_session.delete.side_effect = IntegrityError("foreign key constraint", None, None)
        
        # Act & Assert
        with pytest.raises(InvalidOperationError, match="Cannot delete user with active orders"):
            await user_repository.delete(UserId("test_user"))

    async def test_delete_database_error(self, user_repository, mock_session):
        """Test deleting user with database error."""
        # Arrange
        user = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = user
        mock_session.delete.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.delete(UserId("test_user"))

    async def test_delete_rollback_on_error(self, user_repository, mock_session):
        """Test rollback when delete fails."""
        # Arrange
        user = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = user
        mock_session.delete.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.delete(UserId("test_user"))
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()

    async def test_get_by_id_not_found(self, user_repository, mock_session):
        """Test getting user by ID when user not found."""
        # Arrange
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await user_repository.get_by_id(UserId("non_existent_user"))

    async def test_get_by_id_invalid_format(self, user_repository, mock_session):
        """Test getting user by ID with invalid ID format."""
        # Arrange
        mock_session.execute.side_effect = DataError("Invalid ID format", None, None)
        
        # Act & Assert
        with pytest.raises(DataError):
            await user_repository.get_by_id(UserId("invalid_id_format"))

    async def test_get_by_id_database_error(self, user_repository, mock_session):
        """Test getting user by ID with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.get_by_id(UserId("test_user"))

    async def test_get_all_database_error(self, user_repository, mock_session):
        """Test getting all users with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.get_all()

    async def test_get_all_empty_result(self, user_repository, mock_session):
        """Test getting all users when no users exist."""
        # Arrange
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        result = await user_repository.get_all()
        
        # Assert
        assert result == []

    async def test_search_users_database_error(self, user_repository, mock_session):
        """Test searching users with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.search_users("test")

    async def test_search_users_invalid_query(self, user_repository, mock_session):
        """Test searching users with invalid query."""
        # Arrange
        mock_session.execute.side_effect = ValueError("Search query is too short")
        
        # Act & Assert
        with pytest.raises(ValueError):
            await user_repository.search_users("a")

    async def test_search_users_empty_result(self, user_repository, mock_session):
        """Test searching users with no results."""
        # Arrange
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        result = await user_repository.search_users("nonexistent")
        
        # Assert
        assert result == []

    async def test_count_database_error(self, user_repository, mock_session):
        """Test counting users with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.count()

    async def test_count_zero_users(self, user_repository, mock_session):
        """Test counting users when no users exist."""
        # Arrange
        mock_session.execute.return_value.scalar.return_value = 0
        
        # Act
        result = await user_repository.count()
        
        # Assert
        assert result == 0

    async def test_get_users_paginated_database_error(self, user_repository, mock_session):
        """Test getting paginated users with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.get_users_paginated(page=1, size=10)

    async def test_get_users_paginated_invalid_pagination(self, user_repository, mock_session):
        """Test getting paginated users with invalid pagination parameters."""
        # Arrange
        mock_session.execute.side_effect = ValueError("Invalid pagination parameters")
        
        # Act & Assert
        with pytest.raises(ValueError):
            await user_repository.get_users_paginated(page=-1, size=0)

    async def test_get_users_paginated_empty_result(self, user_repository, mock_session):
        """Test getting paginated users with no results."""
        # Arrange
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        result = await user_repository.get_users_paginated(page=1, size=10)
        
        # Assert
        assert result == []

    async def test_get_users_by_status_database_error(self, user_repository, mock_session):
        """Test getting users by status with database error."""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repository.get_users_by_status("active")

    async def test_get_users_by_status_invalid_status(self, user_repository, mock_session):
        """Test getting users by invalid status."""
        # Arrange
        mock_session.execute.side_effect = ValueError("Invalid status")
        
        # Act & Assert
        with pytest.raises(ValueError):
            await user_repository.get_users_by_status("invalid_status")

    async def test_get_users_by_status_empty_result(self, user_repository, mock_session):
        """Test getting users by status with no results."""
        # Arrange
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        result = await user_repository.get_users_by_status("inactive")
        
        # Assert
        assert result == [] 