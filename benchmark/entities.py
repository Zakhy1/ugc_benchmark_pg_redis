"""
Общие доменные сущности для UGC.
Эти сущности могут быть адаптированы под конкретную БД в реализациях.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: uuid.UUID
    name: str


@dataclass
class Movie:
    id: uuid.UUID
    title: str


@dataclass
class Like:
    user_id: uuid.UUID
    movie_id: uuid.UUID
    rating: int  # 0-10
    timestamp: datetime


@dataclass
class Review:
    id: uuid.UUID
    movie_id: uuid.UUID
    user_id: uuid.UUID
    text: str
    created_at: datetime


@dataclass
class ReviewLike:
    user_id: uuid.UUID
    review_id: uuid.UUID
    rating: int  # 0-10
    timestamp: datetime


@dataclass
class ReviewStats:
    total_likes: int = 0
    total_dislikes: int = 0
    avg_rating: float | None = None
    total_ratings: int = 0


@dataclass
class Bookmark:
    user_id: uuid.UUID
    movie_id: uuid.UUID
    timestamp: datetime


# --- DTOs для агрегатов и кэша ---
@dataclass
class MovieStats:
    """Агрегированные данные о фильме."""

    total_likes: int = 0
    total_dislikes: int = 0
    avg_rating: float | None = None
    total_reviews: int = 0


@dataclass
class CachedUserLikes:
    """DTO для хранения лайков пользователя в кэше."""

    user_id: uuid.UUID
    likes: dict[str, int]  # movie_id_str -> rating


@dataclass
class CachedUserBookmarks:
    """DTO для хранения закладок пользователя в кэше."""

    user_id: uuid.UUID
    bookmarks: set[str]  # set of movie_id_str
