"""
Repository pattern for users. Two implementations share one interface so
switching MONGO_URI in .env is the ONLY change needed to go from mock to
real MongoDB Atlas — no code changes required in routers/services.

Indexes (created on real Mongo via ensure_indexes()):
  - users.phone      -> unique index (one account per phone number)
  - users.role       -> index (fast role-filtered admin queries)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict
from datetime import datetime, timezone
import uuid

from app.core.config import settings
from app.models.user import UserInDB, UserRole


class UserRepository(ABC):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def create(self, phone: str, role: UserRole, name: Optional[str]) -> UserInDB:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def ensure_indexes(self) -> None:
        ...


class InMemoryUserRepository(UserRepository):
    """Dev-only fallback. Data is lost on restart — never use in production."""

    def __init__(self):
        self._by_id: Dict[str, UserInDB] = {}
        self._by_phone: Dict[str, str] = {}  # phone -> id

    async def get_by_phone(self, phone: str) -> Optional[UserInDB]:
        user_id = self._by_phone.get(phone)
        return self._by_id.get(user_id) if user_id else None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        return self._by_id.get(user_id)

    async def create(self, phone: str, role: UserRole, name: Optional[str]) -> UserInDB:
        user_id = str(uuid.uuid4())
        user = UserInDB(id=user_id, phone=phone, role=role, name=name)
        self._by_id[user_id] = user
        self._by_phone[phone] = user_id
        return user

    async def ensure_indexes(self) -> None:
        return None  # no-op for in-memory store


class MongoUserRepository(UserRepository):
    """Real MongoDB Atlas implementation using motor (async driver)."""

    def __init__(self):
        from motor.motor_asyncio import AsyncIOMotorClient
        self._client = AsyncIOMotorClient(settings.MONGO_URI)
        self._db = self._client[settings.MONGO_DB_NAME]
        self._collection = self._db["users"]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("phone", unique=True)
        await self._collection.create_index("role")

    async def get_by_phone(self, phone: str) -> Optional[UserInDB]:
        doc = await self._collection.find_one({"phone": phone})
        return self._doc_to_model(doc) if doc else None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        doc = await self._collection.find_one({"_id": user_id})
        return self._doc_to_model(doc) if doc else None

    async def create(self, phone: str, role: UserRole, name: Optional[str]) -> UserInDB:
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        doc = {
            "_id": user_id,
            "phone": phone,
            "role": role.value,
            "name": name,
            "is_active": True,
            "is_profile_complete": False,
            "created_at": now,
            "updated_at": now,
        }
        await self._collection.insert_one(doc)
        return self._doc_to_model(doc)

    @staticmethod
    def _doc_to_model(doc: dict) -> UserInDB:
        return UserInDB(
            id=doc["_id"],
            phone=doc["phone"],
            role=doc["role"],
            name=doc.get("name"),
            is_active=doc.get("is_active", True),
            is_profile_complete=doc.get("is_profile_complete", False),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )


def get_user_repository() -> UserRepository:
    if settings.USE_MOCK_DB:
        return InMemoryUserRepository()
    return MongoUserRepository()


# Singleton instance used across the app (created once at import time)
user_repository: UserRepository = get_user_repository()
