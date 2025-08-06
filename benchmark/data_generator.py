"""
Абстрактный интерфейс для генерации тестовых данных.
"""

from abc import ABC, abstractmethod

from config import AbstractBenchmarkConfig
from database import AbstractDatabaseRepository


class AbstractDataGenerator(ABC):
    """
    Абстрактный интерфейс для генератора данных.
    Использует репозиторий БД для вставки данных.
    """

    def __init__(
        self, config: AbstractBenchmarkConfig, db_repo: AbstractDatabaseRepository
    ):
        self.config = config
        self.db_repo = db_repo

    @abstractmethod
    async def generate(self):
        """
        Генерирует и вставляет тестовые данные в БД
        в соответствии с конфигурацией.
        """
        pass
