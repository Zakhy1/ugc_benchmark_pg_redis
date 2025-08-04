"""
Абстрактные интерфейсы для работы с кэшем (Redis).
"""
import os
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Set

from .entities import CachedUserBookmarks, CachedUserLikes, MovieStats
import redis.asyncio as redis


class AbstractCacheConnection(ABC):
    """
    Абстрактный интерфейс для соединения с кэшем.
    """

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass


class AbstractCacheRepository(ABC):
    """
    Абстрактный интерфейс репозитория для кэша.
    Определяет методы для работы с кэшируемыми данными.
    """

    def __init__(self, connection: AbstractCacheConnection):
        self.connection = connection

    @abstractmethod
    async def warm_up_user_likes(self, user_id: uuid.UUID, likes: Dict[str, int]):
        pass

    @abstractmethod
    async def warm_up_user_bookmarks(self, user_id: uuid.UUID, bookmarks: Set[str]):
        pass

    @abstractmethod
    async def warm_up_movie_stats(self, movie_id: uuid.UUID, stats: MovieStats):
        pass

    @abstractmethod
    async def get_user_likes(self, user_id: uuid.UUID) -> CachedUserLikes | None:
        pass

    @abstractmethod
    async def get_user_bookmarks(
            self, user_id: uuid.UUID
    ) -> CachedUserBookmarks | None:
        pass

    @abstractmethod
    async def get_movie_stats(self, movie_id: uuid.UUID) -> MovieStats | None:
        pass

    @abstractmethod
    async def update_user_like(self, user_id: uuid.UUID, movie_id: str, rating: int):
        pass

    @abstractmethod
    async def invalidate_movie_stats(self, movie_id: uuid.UUID):
        pass

    @abstractmethod
    async def invalidate_user_likes(self, user_id: uuid.UUID):
        pass

    @abstractmethod
    async def invalidate_user_bookmarks(self, user_id: uuid.UUID):
        pass


class RedisCacheConnection(AbstractCacheConnection):
    """
    Абстрактный интерфейс для соединения с кэшем.
    """

    def __init__(self):
        self.conn = None
        self.dsn = {
            "host": os.getenv("REDIS_HOST"),
            "port": os.getenv("REDIS_HOST"),
            "db": os.getenv("REDIS_DB")
        }

    async def connect(self):
        self.conn = redis.Redis(**self.dsn)
        return self.conn

    async def close(self):
        self.conn.close()


class RedisCacheRepository(AbstractCacheRepository):
    @abstractmethod
    async def warm_up_user_likes(self, user_id: uuid.UUID, likes: Dict[str, int]):
        pass

    @abstractmethod
    async def warm_up_user_bookmarks(self, user_id: uuid.UUID, bookmarks: Set[str]):
        pass

    @abstractmethod
    async def warm_up_movie_stats(self, movie_id: uuid.UUID, stats: MovieStats):
        pass

    @abstractmethod
    async def get_user_likes(self, user_id: uuid.UUID) -> CachedUserLikes | None:
        pass

    @abstractmethod
    async def get_user_bookmarks(
            self, user_id: uuid.UUID
    ) -> CachedUserBookmarks | None:
        pass

    @abstractmethod
    async def get_movie_stats(self, movie_id: uuid.UUID) -> MovieStats | None:
        pass

    @abstractmethod
    async def update_user_like(self, user_id: uuid.UUID, movie_id: str, rating: int):
        pass

    @abstractmethod
    async def invalidate_movie_stats(self, movie_id: uuid.UUID):
        pass

    @abstractmethod
    async def invalidate_user_likes(self, user_id: uuid.UUID):
        pass

    @abstractmethod
    async def invalidate_user_bookmarks(self, user_id: uuid.UUID):
        pass
