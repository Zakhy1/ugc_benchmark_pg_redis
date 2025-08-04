"""
Абстрактный класс для запуска бенчмарка.
Определяет общий процесс инициализации, прогрева, выполнения тестов и завершения.
"""
import logging
from abc import ABC, abstractmethod
from .config import AbstractBenchmarkConfig
from .database import AbstractDatabaseConnection, AbstractDatabaseRepository
from .cache import AbstractCacheConnection, AbstractCacheRepository
from .data_generator import AbstractDataGenerator
from .benchmark_cases import (
    benchmark_user_likes_list,
    benchmark_movie_stats,
    benchmark_user_bookmarks_list,
    benchmark_realtime_like_add_and_read
)

logger = logging.getLogger(__name__)


class AbstractBenchmarkRunner(ABC):
    """
    Абстрактный класс для запуска бенчмарка.
    Подклассы должны предоставить конкретные реализации зависимостей.
    """

    def __init__(self, config: AbstractBenchmarkConfig):
        self.config = config
        self.db_connection: AbstractDatabaseConnection | None = None
        self.db_repo: AbstractDatabaseRepository | None = None
        self.cache_connection: AbstractCacheConnection | None = None
        self.cache_repo: AbstractCacheRepository | None = None
        self.data_generator: AbstractDataGenerator | None = None

    @abstractmethod
    async def _setup_dependencies(self):
        """
        Абстрактный метод для инициализации всех зависимостей:
        - self.db_connection
        - self.db_repo
        - self.cache_connection
        - self.cache_repo
        - self.data_generator
        """
        pass

    async def run(self):
        """
        Основной метод для запуска всего бенчмарка.
        """
        logger.info("=== ЗАПУСК БЕНЧМАРКА ===")
        try:
            await self._setup_dependencies()
            await self._connect()
            await self._generate_data_if_needed()
            await self._warm_up_cache_if_enabled()
            await self._run_benchmarks()
        finally:
            await self._teardown()

    async def _connect(self):
        """Подключение к БД и кэшу."""
        logger.info("Подключение к базе данных...")
        await self.db_connection.connect()
        logger.info("Подключение к кэшу...")
        if self.cache_connection:
            await self.cache_connection.connect()
        logger.info("Подключения установлены.")

    async def _generate_data_if_needed(self):
        """Генерация данных, если БД пуста или по требованию."""
        # Здесь можно добавить логику проверки, есть ли данные
        # Пока что просто запускаем генератор
        logger.info("Генерация тестовых данных...")
        await self.data_generator.generate()
        logger.info("Генерация данных завершена.")

    async def _warm_up_cache_if_enabled(self):
        """Прогрев кэша, если это включено в конфигурации."""
        if not self.config.cache_warmup_enabled or not self.cache_repo:
            logger.info("Прогрев кэша пропущен.")
            return
        logger.info("Прогрев кэша...")
        # Логика прогрева будет зависеть от реализации
        # Например, выбрать случайного пользователя и закешировать его данные
        # Это может быть частью конкретного репозитория кэша
        # await self._do_cache_warmup()
        logger.info("Прогрев кэша завершен (заглушка).")

    async def _run_benchmarks(self):
        """Запуск всех настроенных тестов."""
        logger.info("=== ЗАПУСК ТЕСТОВ ===")

        # Получаем ID для тестов
        test_user_id = await self.db_repo.get_random_user_id()
        test_movie_id = await self.db_repo.get_random_movie_id()

        if not test_user_id or not test_movie_id:
            logger.error("Не удалось получить тестовые ID пользователей/фильмов.")
            return

        if self.config.run_static_read_tests:
            logger.info("--- Статические тесты чтения ---")
            await benchmark_user_likes_list(self.db_repo, self.cache_repo, test_user_id)
            await benchmark_user_bookmarks_list(self.db_repo, self.cache_repo, test_user_id)
            await benchmark_movie_stats(self.db_repo, self.cache_repo, test_movie_id)

        if self.config.run_realtime_tests:
            logger.info("--- Тесты реального времени ---")
            await benchmark_realtime_like_add_and_read(self.db_repo, self.cache_repo, test_user_id, test_movie_id)

        logger.info("=== ТЕСТЫ ЗАВЕРШЕНЫ ===")

    async def _teardown(self):
        """Закрытие соединений."""
        logger.info("Закрытие соединений...")
        if self.db_connection:
            await self.db_connection.close()
        if self.cache_connection:
            await self.cache_connection.close()
        logger.info("Соединения закрыты.")