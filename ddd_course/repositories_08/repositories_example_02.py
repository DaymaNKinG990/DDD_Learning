"""
Примеры кода для модуля "Репозитории (Repositories)".

Демонстрирует концепцию Репозитория с использованием простой сущности User
и реализации InMemoryUserRepository.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, Generic, List, Optional, TypeVar


# 1. Определение простой сущности и ее ID
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
    version: int = 1  # Для демонстрации оптимистичного контроля версий

    def update_email(self, new_email: str) -> "User":
        """Обновляет email пользователя и инкрементирует версию."""
        return replace(self, email=new_email, version=self.version + 1)


# 2. Определение абстрактного интерфейса Репозитория
T_ID = TypeVar("T_ID")
T_Aggregate = TypeVar("T_Aggregate")  # В нашем случае это будет User


class Repository(Generic[T_ID, T_Aggregate], ABC):
    """Абстрактный базовый класс для Репозиториев."""

    @abstractmethod
    def get_by_id(self, id: T_ID) -> Optional[T_Aggregate]:
        """Получает агрегат по его идентификатору."""
        pass

    @abstractmethod
    def save(self, aggregate: T_Aggregate) -> None:
        """Сохраняет агрегат (добавляет новый или обновляет существующий)."""
        pass

    @abstractmethod
    def delete(self, id: T_ID) -> None:
        """Удаляет агрегат по его идентификатору."""
        pass

    @abstractmethod
    def list_all(self) -> List[T_Aggregate]:
        """Возвращает список всех агрегатов."""
        pass


# 3. Реализация InMemory Репозитория для Пользователей
class InMemoryUserRepository(Repository[UserId, User]):
    """Реализация репозитория для пользователей, хранящая данные в памяти."""

    def __init__(self) -> None:
        self._users: Dict[UserId, User] = {}

    def get_by_id(self, id: UserId) -> Optional[User]:
        print(f"[Repository] Поиск пользователя с ID: {id.value}")
        return self._users.get(id)

    def save(self, user: User) -> None:
        """
        Сохраняет пользователя. Если пользователь с таким ID уже существует и его версия
        в репозитории отличается от версии сохраняемого пользователя, может возникнуть
        ошибка конкурентного доступа (здесь не реализовано, но подразумевается).
        Для простоты, мы просто перезаписываем.
        В реальном сценарии здесь была бы проверка версии для оптимистичного локинга.
        """
        print(
            f"[Repository] Сохранение: {user.username} (ID: {user.id.value}, "
            f"Version: {user.version})"
        )
        # Простая проверка на существование для демонстрации логики "add vs update"
        # В реальном репозитории это было бы сложнее, особенно с версионированием.
        if user.id in self._users and self._users[user.id].version >= user.version:
            # Это упрощенная логика. Обычно, если версии не совпадают,
            # выбрасывается исключение.
            # Если версия в БД > версии объекта, значит кто-то уже обновил.
            # Если версия в БД == версии объекта, это обновление.
            # Если версия в БД < версии объекта, это странно,
            # но может быть принудительное обновление.
            # Для простоты, если версия сохраняемого объекта не новее,
            # не делаем ничего или бросаем ошибку.
            # Здесь мы просто перезаписываем, если версия нового объекта выше или равна.
            print(
                f"[Repository] Пользователь {user.username} уже существует. Обновление."
            )
        elif user.id not in self._users:
            print(f"[Repository] Добавление нового пользователя: {user.username}")

        self._users[user.id] = user  # Сохраняем или обновляем

    def delete(self, id: UserId) -> None:
        print(f"[Repository] Удаление пользователя с ID: {id.value}")
        if id in self._users:
            del self._users[id]
            print(f"[Repository] Пользователь с ID: {id.value} удален.")
        else:
            print(f"[Repository] Пользователь с ID: {id.value} не найден для удаления.")

    def list_all(self) -> List[User]:
        print("[Repository] Получение списка всех пользователей.")
        return list(self._users.values())


# 4. Пример использования
if __name__ == "__main__":
    print("--- Демонстрация Репозиториев ---")

    # Создаем репозиторий
    user_repo = InMemoryUserRepository()

    # Создаем пользователей
    user1_id = UserId()
    user1 = User(id=user1_id, username="Alice", email="alice@example.com")

    user2_id = UserId()
    user2 = User(id=user2_id, username="Bob", email="bob@example.com")

    # Сохраняем пользователей
    print("\n--- Сохранение пользователей ---")
    user_repo.save(user1)
    user_repo.save(user2)

    # Получаем пользователя по ID
    print("\n--- Получение пользователя по ID ---")
    retrieved_user1 = user_repo.get_by_id(user1_id)
    if retrieved_user1:
        print(
            f"Найден: {retrieved_user1.username}, Email: {retrieved_user1.email}, "
            f"Version: {retrieved_user1.version}"
        )

    non_existent_id = UserId()
    retrieved_non_existent = user_repo.get_by_id(non_existent_id)
    print(
        f"Попытка найти несуществующего ({non_existent_id.value}): "
        f"{retrieved_non_existent}"
    )

    # Обновляем пользователя
    print("\n--- Обновление пользователя ---")
    if retrieved_user1:
        updated_user1 = retrieved_user1.update_email("alice.new@example.com")
        user_repo.save(updated_user1)  # Сохраняем обновленную версию

        # Проверяем обновление
        re_retrieved_user1 = user_repo.get_by_id(user1_id)
        if re_retrieved_user1:
            print(
                f"Обновленный: {re_retrieved_user1.username}, "
                f"Email: {re_retrieved_user1.email}, "
                f"Version: {re_retrieved_user1.version}"
            )

    # Список всех пользователей
    print("\n--- Список всех пользователей ---")
    all_users = user_repo.list_all()
    print(f"Всего пользователей: {len(all_users)}")
    for u in all_users:
        print(
            f"  - {u.username} (ID: {u.id.value}, Email: {u.email}, Ver: {u.version})"
        )

    # Удаляем пользователя
    print("\n--- Удаление пользователя ---")
    user_repo.delete(user2_id)
    user_repo.delete(UserId())  # Попытка удалить несуществующего

    # Проверяем список после удаления
    print("\n--- Список пользователей после удаления ---")
    all_users_after_delete = user_repo.list_all()
    print(f"Всего пользователей: {len(all_users_after_delete)}")
    for u in all_users_after_delete:
        print(f"  - {u.username} (ID: {u.id.value})")

    print("\n--- Демонстрация завершена ---")
