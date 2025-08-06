import uuid
import random
from datetime import datetime

from tqdm import tqdm

from config import AbstractBenchmarkConfig
from data_generator import AbstractDataGenerator
from database import PostgresRepository, PostgresConnection
from cache import RedisCacheConnection, AbstractCacheRepository
from entities import User, Movie, Like, Review, ReviewLike, Bookmark
from benchmark_runner import AbstractBenchmarkRunner
from logger import setup_logger

logger = setup_logger(__name__)


class DefaultBenchmarkConfig(AbstractBenchmarkConfig):
    @property
    def num_users(self) -> int:
        return 500_000

    @property
    def num_movies(self) -> int:
        return 500_000

    @property
    def likes_per_user(self) -> int:
        return 25

    @property
    def bookmarks_per_user(self) -> int:
        return 25

    @property
    def reviews_per_user(self) -> int:
        return 25

    @property
    def num_iterations_per_test(self) -> int:
        return 5

    @property
    def cache_warmup_enabled(self) -> bool:
        return True

    @property
    def run_static_read_tests(self) -> bool:
        return True

    @property
    def run_realtime_tests(self) -> bool:
        return True


class SimpleDataGenerator(AbstractDataGenerator):
    async def generate(self):
        BATCH_SIZE = 10_000_000

        logger.info("Начало загрузки пользователей")
        for i in tqdm(
            range(0, self.config.num_users, BATCH_SIZE), desc="Users", unit="batch"
        ):
            batch = [
                User(id=uuid.uuid4(), name=f"User{j}")
                for j in range(i, min(i + BATCH_SIZE, self.config.num_users))
            ]
            await self.db_repo.bulk_insert_users(batch)
        logger.info("Пользователи загружены")

        logger.info("Начало загрузки фильмов")
        for i in tqdm(
            range(0, self.config.num_movies, BATCH_SIZE), desc="Movies", unit="batch"
        ):
            batch = [
                Movie(id=uuid.uuid4(), title=f"Movie{j}")
                for j in range(i, min(i + BATCH_SIZE, self.config.num_movies))
            ]
            await self.db_repo.bulk_insert_movies(batch)
        logger.info("Фильмы загружены")

        logger.info("Получаем ID фильмов")
        movie_ids = []
        for i in tqdm(
            range(0, self.config.num_movies, BATCH_SIZE), desc="Movie IDs", unit="batch"
        ):
            rows = await self.db_repo.connection.conn.fetch(
                "SELECT id FROM movies OFFSET $1 LIMIT $2", i, BATCH_SIZE
            )
            movie_ids.extend([row["id"] for row in rows])
        logger.info("Создаем пользовательскую активность")
        for i in tqdm(
            range(0, self.config.num_users, BATCH_SIZE),
            desc="User Activity",
            unit="batch",
        ):
            user_rows = await self.db_repo.connection.conn.fetch(
                "SELECT id FROM users OFFSET $1 LIMIT $2", i, BATCH_SIZE
            )
            for user_row in tqdm(
                user_rows,
                desc=f"User batch {i // BATCH_SIZE + 1}",
                unit="user",
                leave=False,
            ):
                user_id = user_row["id"]
                # Likes
                likes = []
                liked_movies = random.sample(
                    movie_ids, min(self.config.likes_per_user, len(movie_ids))
                )
                for movie_id in liked_movies:
                    likes.append(
                        Like(
                            user_id=user_id,
                            movie_id=movie_id,
                            rating=random.randint(0, 10),
                            timestamp=datetime.now(),
                        )
                    )
                await self.db_repo.bulk_insert_likes(likes)

                # Bookmarks
                bookmarks = []
                bookmarked_movies = random.sample(
                    movie_ids, min(self.config.bookmarks_per_user, len(movie_ids))
                )
                for movie_id in bookmarked_movies:
                    bookmarks.append(
                        Bookmark(
                            user_id=user_id, movie_id=movie_id, timestamp=datetime.now()
                        )
                    )
                await self.db_repo.bulk_insert_bookmarks(bookmarks)

                # Reviews & ReviewLikes
                reviews = []
                review_likes = []
                for _ in range(self.config.reviews_per_user):
                    movie_id = random.choice(movie_ids)
                    review = Review(
                        id=uuid.uuid4(),
                        movie_id=movie_id,
                        user_id=user_id,
                        text="Nice movie!",
                        created_at=datetime.now(),
                    )
                    reviews.append(review)
                    review_likes.append(
                        ReviewLike(
                            user_id=user_id,
                            review_id=review.id,
                            rating=random.randint(0, 10),
                            timestamp=datetime.now(),
                        )
                    )
                await self.db_repo.bulk_insert_reviews(reviews)
                await self.db_repo.bulk_insert_review_likes(review_likes)


class RedisCacheRepository(AbstractCacheRepository):
    def __init__(self, connection: RedisCacheConnection):
        super().__init__(connection)
        self.redis = None

    async def warm_up_user_likes(self, user_id, likes):
        # likes: Dict[str, int]
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.hmset_dict(f"user:{user_id}:likes", likes)

    async def warm_up_user_bookmarks(self, user_id, bookmarks):
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.sadd(f"user:{user_id}:bookmarks", *bookmarks)

    async def warm_up_movie_stats(self, movie_id, stats):
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.hmset_dict(f"movie:{movie_id}:stats", stats.__dict__)

    async def get_user_likes(self, user_id):
        await self.connection.connect()
        self.redis = self.connection.conn
        likes = await self.redis.hgetall(f"user:{user_id}:likes")
        return likes if likes else None

    async def get_user_bookmarks(self, user_id):
        await self.connection.connect()
        self.redis = self.connection.conn
        bookmarks = await self.redis.smembers(f"user:{user_id}:bookmarks")
        return bookmarks if bookmarks else None

    async def get_movie_stats(self, movie_id):
        await self.connection.connect()
        self.redis = self.connection.conn
        stats = await self.redis.hgetall(f"movie:{movie_id}:stats")
        return stats if stats else None

    async def update_user_like(self, user_id, movie_id, rating):
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.hset(f"user:{user_id}:likes", movie_id, rating)

    async def invalidate_movie_stats(self, movie_id):
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.delete(f"movie:{movie_id}:stats")

    async def invalidate_user_likes(self, user_id):
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.delete(f"user:{user_id}:likes")

    async def invalidate_user_bookmarks(self, user_id):
        await self.connection.connect()
        self.redis = self.connection.conn
        await self.redis.delete(f"user:{user_id}:bookmarks")


class BenchmarkRunner(AbstractBenchmarkRunner):
    async def _setup_dependencies(self):
        self.db_connection = PostgresConnection()
        self.db_repo = PostgresRepository(self.db_connection)
        self.cache_connection = RedisCacheConnection()
        self.cache_repo = RedisCacheRepository(self.cache_connection)
        self.data_generator = SimpleDataGenerator(self.config, self.db_repo)
