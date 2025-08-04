"""
Абстрактные интерфейсы для работы с основной базой данных.
"""
from abc import ABC, abstractmethod
from typing import List
import uuid
from .entities import User, Movie, Like, Review, ReviewLike, ReviewStats, Bookmark, MovieStats


class AbstractDatabaseConnection(ABC):
    """
    Абстрактный интерфейс для соединения с БД.
    """

    @abstractmethod
    async def connect(self): pass

    @abstractmethod
    async def close(self): pass


class AbstractDatabaseRepository(ABC):
    """
    Абстрактный интерфейс репозитория для основной БД.
    Определяет методы для создания/чтения/обновления/удаления данных.
    """

    def __init__(self, connection: AbstractDatabaseConnection):
        self.connection = connection

    # --- Users ---
    @abstractmethod
    async def create_user(self, user: User) -> User: pass

    @abstractmethod
    async def get_random_user_id(self) -> uuid.UUID | None: pass

    # --- Movies ---
    @abstractmethod
    async def create_movie(self, movie: Movie) -> Movie: pass

    @abstractmethod
    async def get_random_movie_id(self) -> uuid.UUID | None: pass

    # --- Likes ---
    @abstractmethod
    async def add_or_update_like(self, like: Like) -> Like: pass

    @abstractmethod
    async def remove_like(self, user_id: uuid.UUID, movie_id: uuid.UUID) -> bool: pass

    @abstractmethod
    async def get_movie_stats(self, movie_id: uuid.UUID) -> MovieStats: pass

    # --- Reviews ---
    @abstractmethod
    async def create_review(self, review: Review) -> Review: pass

    @abstractmethod
    async def add_or_update_review_like(self, review_like: ReviewLike) -> ReviewLike:
        pass

    @abstractmethod
    async def remove_review_like(self, user_id: uuid.UUID, review_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def get_review_stats(self, review_id: uuid.UUID) -> ReviewStats:
        pass

    # --- Bookmarks ---
    @abstractmethod
    async def add_bookmark(self, bookmark: Bookmark) -> bool: pass  # True if added

    @abstractmethod
    async def remove_bookmark(self, user_id: uuid.UUID, movie_id: uuid.UUID) -> bool: pass

    # --- Data Generation Helpers ---
    @abstractmethod
    async def bulk_insert_users(self, users: List[User]): pass

    @abstractmethod
    async def bulk_insert_movies(self, movies: List[Movie]): pass

    @abstractmethod
    async def bulk_insert_likes(self, likes: List[Like]): pass

    @abstractmethod
    async def bulk_insert_bookmarks(self, bookmarks: List[Bookmark]): pass

    @abstractmethod
    async def bulk_insert_reviews(self, reviews: List[Review]): pass

    @abstractmethod
    async def bulk_insert_review_likes(self, review_likes: List[ReviewLike]): pass