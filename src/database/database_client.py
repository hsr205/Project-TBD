from logging import Logger

import psycopg2

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants


class DatabaseClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._conn = psycopg2.connect(
            host=self._settings.db_host,
            port=self._settings.db_port,
            dbname=self._settings.db_name,
            user=self._settings.db_user
        )
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    def create_franchises_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info("Creating franchises table")
            cursor.execute(query=Constants.Queries.CREATE_FRANCHISES_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully created franchises table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def drop_franchises_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info("Dropping franchises table")
            cursor.execute(query=Constants.Queries.DROP_FRANCHISES_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully dropped franchises table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
