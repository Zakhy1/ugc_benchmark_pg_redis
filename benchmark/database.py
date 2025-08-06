"""
Абстрактные интерфейсы для работы с основной базой данных.
"""

import os
import uuid
from abc import ABC, abstractmethod
from typing import List

import asyncpg

from entities import (
    Bookmark,
    Like,
    Movie,
    MovieStats,
    Review,
    ReviewLike,
    ReviewStats,
    User,
)


class AbstractDatabaseConnection(ABC):
    """
    Абстрактный интерфейс для соединения с БД.
    """

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass


class AbstractDatabaseRepository(ABC):
    """
    Абстрактный интерфейс репозитория для основной БД.
    Определяет методы для создания/чтения/обновления/удаления данных.
    """

    def __init__(self, connection: AbstractDatabaseConnection):
        self.connection = connection

    # --- Users ---
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_random_user_id(self) -> uuid.UUID | None:
        pass

    # --- Movies ---
    @abstractmethod
    async def create_movie(self, movie: Movie) -> Movie:
        pass

    @abstractmethod
    async def get_random_movie_id(self) -> uuid.UUID | None:
        pass

    # --- Likes ---
    @abstractmethod
    async def add_or_update_like(self, like: Like) -> Like:
        pass

    @abstractmethod
    async def remove_like(self, user_id: uuid.UUID, movie_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def get_movie_stats(self, movie_id: uuid.UUID) -> MovieStats:
        pass

    # --- Reviews ---
    @abstractmethod
    async def create_review(self, review: Review) -> Review:
        pass

    @abstractmethod
    async def add_or_update_review_like(self, review_like: ReviewLike) -> ReviewLike:
        pass

    @abstractmethod
    async def remove_review_like(
        self, user_id: uuid.UUID, review_id: uuid.UUID
    ) -> bool:
        pass

    @abstractmethod
    async def get_review_stats(self, review_id: uuid.UUID) -> ReviewStats:
        pass

    # --- Bookmarks ---
    @abstractmethod
    async def add_bookmark(self, bookmark: Bookmark) -> bool:
        pass  # True if added

    @abstractmethod
    async def remove_bookmark(self, user_id: uuid.UUID, movie_id: uuid.UUID) -> bool:
        pass

    # --- Data Generation Helpers ---
    @abstractmethod
    async def bulk_insert_users(self, users: List[User]):
        pass

    @abstractmethod
    async def bulk_insert_movies(self, movies: List[Movie]):
        pass

    @abstractmethod
    async def bulk_insert_likes(self, likes: List[Like]):
        pass

    @abstractmethod
    async def bulk_insert_bookmarks(self, bookmarks: List[Bookmark]):
        pass

    @abstractmethod
    async def bulk_insert_reviews(self, reviews: List[Review]):
        pass

    @abstractmethod
    async def bulk_insert_review_likes(self, review_likes: List[ReviewLike]):
        pass


class PostgresConnection(AbstractDatabaseConnection):
    def __init__(self):
        self.dsn = {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "database": os.getenv("POSTGRES_DB"),
            "host": os.getenv("POSTGRES_HOST"),
        }
        self.conn = None

    async def connect(self):
        self.conn = await asyncpg.connect(**self.dsn)
        return self.conn

    async def close(self):
        if self.conn is not None:
            await self.conn.close()


class PostgresRepository(AbstractDatabaseRepository):
    # --- Movie Stats ---
    async def get_movie_stats_row(self, movie_id: uuid.UUID):
        query = "SELECT * FROM movie_stats WHERE movie_id = $1"
        return await self.connection.conn.fetchrow(query, str(movie_id))

    async def update_movie_stats(
        self,
        movie_id: uuid.UUID,
        total_likes: int,
        total_dislikes: int,
        avg_rating: float,
        total_reviews: int,
    ):
        query = (
            "INSERT INTO movie_stats (movie_id, total_likes, total_dislikes, avg_rating, total_reviews) "
            "VALUES ($1, $2, $3, $4, $5) "
            "ON CONFLICT (movie_id) DO UPDATE SET "
            "total_likes = $2, total_dislikes = $3, avg_rating = $4, total_reviews = $5"
        )
        await self.connection.conn.execute(
            query, str(movie_id), total_likes, total_dislikes, avg_rating, total_reviews
        )

    # --- Review Stats ---
    async def get_review_stats_row(self, review_id: uuid.UUID):
        query = "SELECT * FROM review_stats WHERE review_id = $1"
        return await self.connection.conn.fetchrow(query, str(review_id))

    async def update_review_stats(
        self,
        review_id: uuid.UUID,
        total_likes: int,
        total_dislikes: int,
        avg_rating: float,
        total_ratings: int,
    ):
        query = (
            "INSERT INTO review_stats (review_id, total_likes, total_dislikes, avg_rating, total_ratings) "
            "VALUES ($1, $2, $3, $4, $5) "
            "ON CONFLICT (review_id) DO UPDATE SET "
            "total_likes = $2, total_dislikes = $3, avg_rating = $4, total_ratings = $5"
        )
        await self.connection.conn.execute(
            query,
            str(review_id),
            total_likes,
            total_dislikes,
            avg_rating,
            total_ratings,
        )

    # --- Получение списков ---
    async def get_user_likes_from_db(self, user_id: uuid.UUID):
        query = "SELECT * FROM likes WHERE user_id = $1"
        rows = await self.connection.conn.fetch(query, str(user_id))
        return [
            Like(
                user_id=r["user_id"],
                movie_id=r["movie_id"],
                rating=r["rating"],
                timestamp=r["timestamp"],
            )
            for r in rows
        ]

    async def get_user_bookmarks_from_db(self, user_id: uuid.UUID):
        query = "SELECT * FROM bookmarks WHERE user_id = $1"
        rows = await self.connection.conn.fetch(query, str(user_id))
        return [
            Bookmark(
                user_id=r["user_id"], movie_id=r["movie_id"], timestamp=r["timestamp"]
            )
            for r in rows
        ]

    async def get_movie_reviews(self, movie_id: uuid.UUID):
        query = "SELECT * FROM reviews WHERE movie_id = $1"
        rows = await self.connection.conn.fetch(query, str(movie_id))
        return [
            Review(
                id=r["id"],
                movie_id=r["movie_id"],
                user_id=r["user_id"],
                text=r["text"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    async def get_review_likes(self, review_id: uuid.UUID):
        query = "SELECT * FROM review_likes WHERE review_id = $1"
        rows = await self.connection.conn.fetch(query, str(review_id))
        return [
            ReviewLike(
                user_id=r["user_id"],
                review_id=r["review_id"],
                rating=r["rating"],
                timestamp=r["timestamp"],
            )
            for r in rows
        ]

    async def create_user(self, user: User) -> User:
        query = "INSERT INTO users (id, name) VALUES ($1, $2) RETURNING id, name"
        row = await self.connection.conn.fetchrow(query, str(user.id), user.name)
        return User(id=row["id"], name=row["name"])

    async def get_random_user_id(self) -> uuid.UUID | None:
        query = "SELECT id FROM users ORDER BY random() LIMIT 1"
        row = await self.connection.conn.fetchrow(query)
        if row:
            return row["id"]
        return None

    # --- Movies ---

    async def create_movie(self, movie: Movie) -> Movie:
        query = "INSERT INTO movies (id, title) VALUES ($1, $2) RETURNING id, title"
        row = await self.connection.conn.fetchrow(query, str(movie.id), movie.title)
        return Movie(id=row["id"], title=row["title"])

    async def get_random_movie_id(self) -> uuid.UUID | None:
        query = "SELECT id FROM movies ORDER BY random() LIMIT 1"
        row = await self.connection.conn.fetchrow(query)
        if row:
            return row["id"]
        return None

    # --- Likes ---

    async def add_or_update_like(self, like: Like) -> Like:
        query = (
            "INSERT INTO likes (user_id, movie_id, rating, timestamp) "
            "VALUES ($1, $2, $3, $4) "
            "ON CONFLICT (user_id, movie_id) "
            "DO UPDATE SET rating = EXCLUDED.rating, timestamp = EXCLUDED.timestamp "
            "RETURNING user_id, movie_id, rating, timestamp"
        )
        row = await self.connection.conn.fetchrow(
            query, str(like.user_id), str(like.movie_id), like.rating, like.timestamp
        )
        return Like(
            user_id=row["user_id"],
            movie_id=row["movie_id"],
            rating=row["rating"],
            timestamp=row["timestamp"],
        )

    async def remove_like(self, user_id: uuid.UUID, movie_id: uuid.UUID) -> bool:
        query = "DELETE FROM likes WHERE user_id = $1 AND movie_id = $2"
        result = await self.connection.conn.execute(query, str(user_id), str(movie_id))
        return result.startswith("DELETE")

    async def get_movie_stats(self, movie_id: uuid.UUID) -> MovieStats:
        query = (
            "SELECT "
            "COUNT(*) FILTER (WHERE rating >= 6) AS total_likes, "
            "COUNT(*) FILTER (WHERE rating < 6) AS total_dislikes, "
            "AVG(rating) AS avg_rating, "
            "COUNT(*) AS total_reviews "
            "FROM likes WHERE movie_id = $1"
        )
        row = await self.connection.conn.fetchrow(query, str(movie_id))
        return MovieStats(
            total_likes=row["total_likes"],
            total_dislikes=row["total_dislikes"],
            avg_rating=row["avg_rating"],
            total_reviews=row["total_reviews"],
        )

    # --- Reviews ---

    async def create_review(self, review: Review) -> Review:
        query = (
            "INSERT INTO reviews (id, movie_id, user_id, text, created_at) "
            "VALUES ($1, $2, $3, $4, $5) "
            "RETURNING id, movie_id, user_id, text, created_at"
        )
        row = await self.connection.conn.fetchrow(
            query,
            str(review.id),
            str(review.movie_id),
            str(review.user_id),
            review.text,
            review.created_at,
        )
        return Review(
            id=row["id"],
            movie_id=row["movie_id"],
            user_id=row["user_id"],
            text=row["text"],
            created_at=row["created_at"],
        )

    async def add_or_update_review_like(self, review_like: ReviewLike) -> ReviewLike:
        query = (
            "INSERT INTO review_likes (user_id, review_id, rating, timestamp) "
            "VALUES ($1, $2, $3, $4) "
            "ON CONFLICT (user_id, review_id) "
            "DO UPDATE SET rating = EXCLUDED.rating, timestamp = EXCLUDED.timestamp "
            "RETURNING user_id, review_id, rating, timestamp"
        )
        row = await self.connection.conn.fetchrow(
            query,
            str(review_like.user_id),
            str(review_like.review_id),
            review_like.rating,
            review_like.timestamp,
        )
        return ReviewLike(
            user_id=row["user_id"],
            review_id=row["review_id"],
            rating=row["rating"],
            timestamp=row["timestamp"],
        )

    async def remove_review_like(
        self, user_id: uuid.UUID, review_id: uuid.UUID
    ) -> bool:
        query = "DELETE FROM review_likes WHERE user_id = $1 AND review_id = $2"
        result = await self.connection.conn.execute(query, str(user_id), str(review_id))
        return result.startswith("DELETE")

    async def get_review_stats(self, review_id: uuid.UUID) -> ReviewStats:
        query = (
            "SELECT "
            "COUNT(*) FILTER (WHERE rating >= 6) AS total_likes, "
            "COUNT(*) FILTER (WHERE rating < 6) AS total_dislikes, "
            "AVG(rating) AS avg_rating, "
            "COUNT(*) AS total_ratings "
            "FROM review_likes WHERE review_id = $1"
        )
        row = await self.connection.conn.fetchrow(query, str(review_id))
        return ReviewStats(
            total_likes=row["total_likes"],
            total_dislikes=row["total_dislikes"],
            avg_rating=row["avg_rating"],
            total_ratings=row["total_ratings"],
        )

    # --- Bookmarks ---

    async def add_bookmark(self, bookmark: Bookmark) -> bool:
        query = (
            "INSERT INTO bookmarks (user_id, movie_id, timestamp) "
            "VALUES ($1, $2, $3) "
            "ON CONFLICT (user_id, movie_id) DO NOTHING"
        )
        result = await self.connection.conn.execute(
            query, str(bookmark.user_id), str(bookmark.movie_id), bookmark.timestamp
        )
        return result.startswith("INSERT")

    async def remove_bookmark(self, user_id: uuid.UUID, movie_id: uuid.UUID) -> bool:
        query = "DELETE FROM bookmarks WHERE user_id = $1 AND movie_id = $2"
        result = await self.connection.conn.execute(query, str(user_id), str(movie_id))
        return result.startswith("DELETE")

    # --- Data Generation Helpers ---

    async def bulk_insert_users(self, users: List[User]):
        if not users:
            return
        query = (
            "INSERT INTO users (id, name) VALUES ($1, $2) ON CONFLICT (id) DO NOTHING"
        )
        await self.connection.conn.executemany(
            query, [(str(u.id), u.name) for u in users]
        )

    async def bulk_insert_movies(self, movies: List[Movie]):
        if not movies:
            return
        query = (
            "INSERT INTO movies (id, title) VALUES ($1, $2) ON CONFLICT (id) DO NOTHING"
        )
        await self.connection.conn.executemany(
            query, [(str(m.id), m.title) for m in movies]
        )

    async def bulk_insert_likes(self, likes: List[Like]):
        if not likes:
            return
        query = "INSERT INTO likes (user_id, movie_id, rating, timestamp) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id, movie_id) DO NOTHING"
        await self.connection.conn.executemany(
            query,
            [(str(l.user_id), str(l.movie_id), l.rating, l.timestamp) for l in likes],
        )

    async def bulk_insert_bookmarks(self, bookmarks: List[Bookmark]):
        if not bookmarks:
            return
        query = "INSERT INTO bookmarks (user_id, movie_id, timestamp) VALUES ($1, $2, $3) ON CONFLICT (user_id, movie_id) DO NOTHING"
        await self.connection.conn.executemany(
            query, [(str(b.user_id), str(b.movie_id), b.timestamp) for b in bookmarks]
        )

    async def bulk_insert_reviews(self, reviews: List[Review]):
        if not reviews:
            return
        query = "INSERT INTO reviews (id, movie_id, user_id, text, created_at) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (id) DO NOTHING"
        await self.connection.conn.executemany(
            query,
            [
                (str(r.id), str(r.movie_id), str(r.user_id), r.text, r.created_at)
                for r in reviews
            ],
        )

    async def bulk_insert_review_likes(self, review_likes: List[ReviewLike]):
        if not review_likes:
            return
        query = "INSERT INTO review_likes (user_id, review_id, rating, timestamp) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id, review_id) DO NOTHING"
        await self.connection.conn.executemany(
            query,
            [
                (str(rl.user_id), str(rl.review_id), rl.rating, rl.timestamp)
                for rl in review_likes
            ],
        )
