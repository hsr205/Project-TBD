from logging import Logger

import psycopg2

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.web_scraper import WebScraper


# TODO: Add a REDIS or in-memory cache for read operations if appropriate
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

    ## ======================================================== CREATE TABLE METHODS ======================================================== ##

    def create_franchise_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Creating franchise table")
            cursor.execute(query=Constants.Queries.CREATE_FRANCHISE_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully created franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def create_player_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Creating player table")
            cursor.execute(query=Constants.Queries.CREATE_PLAYER_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully created player table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def create_player_regular_season_stats_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Creating player_regular_season_stats table")
            cursor.execute(query=Constants.Queries.CREATE_PLAYER_STATS_TABLE_QUERY_STR)
            self._logger.info("Successfully player_regular_season_stats franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def create_player_regular_season_advanced_stats_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Creating player_regular_season_advanced_stats table")
            cursor.execute(query=Constants.Queries.CREATE_PLAYER_ADVANCED_STATS_TABLE_QUERY_STR)
            self._logger.info("Successfully player_regular_season_advanced_stats franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    def get_player_dict_from_player_table(self) -> dict[int, str]:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Querying player table")

            # TODO: Find a way to do this less manually
            cursor.execute(query=Constants.Queries.QUERY_PLAYER_TABLE_FOR_ALL_NBA_PLAYERS)
            player_dict: dict[int, str] = {}
            query_result_list = cursor.fetchall()

            self._logger.info(f"Returned {len(query_result_list):,} rows")

            for element in query_result_list:

                player_id: int = element[0]
                player_name_str: str = element[1]

                if player_id not in player_dict:
                    player_dict[player_id] = player_name_str

            self._logger.info("Successfully queried player table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

        return player_dict

    ## ======================================================== INSERT INTO TABLE METHODS ======================================================== ##

    async def insert_rows_into_table(self,
                                     player_name_str: str,
                                     player_regular_season_stats_list: list[tuple],
                                     current_player_dict: dict[int, str],
                                     insert_query_str: str) -> None:
        player_id: int | None = next(
            (player_id for player_id, name in current_player_dict.items() if name == player_name_str),
            None)

        if player_id is None:
            self._logger.warning(f"No player_id found for '{player_name_str}' — skipping stats insert")
            return

        # Prepend player_id to each stats row tuple
        rows_with_player_id: list[tuple] = [(player_id, *row) for row in player_regular_season_stats_list]

        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        with self._conn.cursor() as cursor:
            self._logger.info(
                f"Inserting {len(rows_with_player_id):,} rows into table for {player_name_str}")

            cursor.executemany(query=insert_query_str, vars_list=rows_with_player_id)

            self._logger.info(
                f"Successfully inserted {len(rows_with_player_id):,} rows in into table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    async def insert_rows_into_player_table(self) -> None:
        nba_players_list: list[tuple] = await self._web_scraper.get_all_nba_players_list()

        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
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
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info(f"Inserting {len(nba_franchise_list):,} rows in franchise table")

            cursor.executemany(query=Constants.Queries.INSERT_INTO_FRANCHISE_QUERY_STR, vars_list=nba_franchise_list)

            self._logger.info(f"Successfully inserted {len(nba_franchise_list)} rows in franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    ## ======================================================== DROP TABLE METHODS ======================================================== ##

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_franchise_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Dropping franchise table")
            cursor.execute(query=Constants.Queries.DROP_FRANCHISE_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully dropped franchise table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_player_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Dropping player table")
            cursor.execute(query=Constants.Queries.DROP_PLAYER_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully dropped player table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_player_regular_season_stats_table(self) -> None:
        self._logger.info(f"Creating connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
        with self._conn.cursor() as cursor:
            self._logger.info("Dropping player_regular_season_stats table")
            cursor.execute(query=Constants.Queries.DROP_PLAYER_REGULAR_SEASON_TABLE_SCHEMA_QUERY_STR)
            self._logger.info("Successfully dropped player_regular_season_stats table")
            self._conn.commit()
        self._logger.info(f"Closing connection to database: {self._settings.db_name}")
        self._logger.info("=" * 100)
