"""
Модуль для определения абстрактной конфигурации.
Конкретные реализации будут наследовать и переопределять эти значения.
"""

from abc import ABC, abstractmethod


class AbstractBenchmarkConfig(ABC):
    """
    Абстрактный класс для конфигурации бенчмарка.
    Определяет параметры, общие для всех связок БД.
    """

    # --- Параметры генерации данных ---
    @property
    @abstractmethod
    def num_users(self) -> int:
        pass

    @property
    @abstractmethod
    def num_movies(self) -> int:
        pass

    @property
    @abstractmethod
    def likes_per_user(self) -> int:
        pass

    @property
    @abstractmethod
    def bookmarks_per_user(self) -> int:
        pass

    @property
    @abstractmethod
    def reviews_per_user(self) -> int:
        pass

    # --- Параметры тестирования ---
    @property
    @abstractmethod
    def num_iterations_per_test(self) -> int:
        """Количество итераций для каждого теста для усреднения результата."""
        pass

    @property
    @abstractmethod
    def cache_warmup_enabled(self) -> bool:
        """Нужно ли прогревать кэш перед тестами."""
        pass

    # --- Сценарии тестирования ---
    @property
    @abstractmethod
    def run_static_read_tests(self) -> bool:
        pass

    @property
    @abstractmethod
    def run_realtime_tests(self) -> bool:
        pass
