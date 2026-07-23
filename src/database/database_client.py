from logging import Logger

import psycopg2

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.web_scraper import WebScraper


class DatabaseClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._web_scraper: WebScraper = WebScraper(settings=self._settings)
        self._conn = psycopg2.connect(
            host=self._settings.db_host,
            port=self._settings.db_port,
            dbname=self._settings.db_name,
            user=self._settings.db_user
        )
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    def create_franchise_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info("Creating franchise table")
            cursor.execute(query=Constants.Queries.CREATE_FRANCHISE_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully created franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def create_player_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info("Creating player table")
            cursor.execute(query=Constants.Queries.CREATE_PLAYER_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully created player table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    async def insert_rows_into_player_table(self) -> None:
        nba_players_list: list[tuple] = await self._web_scraper.get_all_nba_players_list()

        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info(f"Inserting {len(nba_players_list):,} rows in player table")

            cursor.executemany(query=Constants.Queries.INSERT_INTO_PLAYER_QUERY_STR, vars_list=nba_players_list)

            self._logger.info(f"Successfully inserted {len(nba_players_list)} rows in player table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    async def insert_rows_into_franchise_table(self) -> None:
        nba_franchise_list: list[tuple] = await self._web_scraper.get_nba_franchise_list()

        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info(f"Inserting {len(nba_franchise_list):,} rows in franchise table")

            cursor.executemany(query=Constants.Queries.INSERT_INTO_FRANCHISE_QUERY_STR, vars_list=nba_franchise_list)

            self._logger.info(f"Successfully inserted {len(nba_franchise_list)} rows in franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_player_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info("Dropping franchise table")
            cursor.execute(query=Constants.Queries.DROP_PLAYER_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully dropped franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def drop_franchise_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info("Dropping franchise table")
            cursor.execute(query=Constants.Queries.DROP_FRANCHISE_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully dropped franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
