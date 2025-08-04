"""
Абстрактные интерфейсы для работы с кэшем (Redis).
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, Set

from .entities import CachedUserBookmarks, CachedUserLikes, MovieStats


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
