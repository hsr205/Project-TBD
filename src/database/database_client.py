from logging import Logger

from psycopg2.extensions import connection
from psycopg2.pool import SimpleConnectionPool

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.web_scraper import WebScraper


# TODO: Add a REDIS or in-memory cache for read operations if appropriate
class DatabaseClient:

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._web_scraper: WebScraper = WebScraper(settings=self._settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

        self._pool: SimpleConnectionPool = SimpleConnectionPool(
            minconn=Constants.POOL_MIN_CONNECTIONS,
            maxconn=Constants.POOL_MAX_CONNECTIONS,
            host=self._settings.db_host,
            port=self._settings.db_port,
            dbname=self._settings.db_name,
            user=self._settings.db_user
        )
        self._logger.info(
            f"Connection pool created — MIN: {Constants.POOL_MIN_CONNECTIONS}, MAX: {Constants.POOL_MAX_CONNECTIONS}"
        )

    def _get_connection(self) -> connection:
        return self._pool.getconn()

    def _release_connection(self, conn: connection) -> None:
        self._pool.putconn(conn)

    def close_pool(self) -> None:
        """Close all connections in the pool. Call when the application shuts down."""
        self._pool.closeall()
        self._logger.info("Connection pool closed")
        self._logger.info("=" * 100)

    ## ======================================================== CREATE TABLE METHODS ======================================================== ##

    def create_franchise_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Creating franchise table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.CREATE_FRANCHISE_TABLE_SCHEMA_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully created franchise table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    def create_player_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Creating player table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.CREATE_PLAYER_TABLE_SCHEMA_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully created player table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    def create_player_regular_season_stats_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Creating player_regular_season_stats table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.CREATE_PLAYER_STATS_TABLE_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully created player_regular_season_stats table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    def create_player_regular_season_advanced_stats_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Creating player_regular_season_advanced_stats table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.CREATE_PLAYER_ADVANCED_STATS_TABLE_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully created player_regular_season_advanced_stats table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    def get_franchise_dict_from_franchise_table(self) -> dict[int, str]:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Querying player table")
            with conn.cursor() as cursor:
                # TODO: Find a way to do this less manually
                cursor.execute(query=Constants.Queries.QUERY_FRANCHISE_TABLE_FOR_CURRENT_FRANCHISES)
                query_result_list = cursor.fetchall()

            self._logger.info(f"Returned {len(query_result_list):,} rows")

            franchise_dict: dict[int, str] = {
                element[0]: element[1] for element in query_result_list
            }

            self._logger.info("Successfully queried player table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

        return franchise_dict

    def get_player_dict_from_player_table(self) -> dict[int, str]:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Querying player table")
            with conn.cursor() as cursor:
                # TODO: Find a way to do this less manually
                cursor.execute(query=Constants.Queries.QUERY_PLAYER_TABLE_FOR_ALL_NBA_PLAYERS)
                query_result_list = cursor.fetchall()

            self._logger.info(f"Returned {len(query_result_list):,} rows")

            player_dict: dict[int, str] = {
                element[0]: element[1] for element in query_result_list
            }

            self._logger.info("Successfully queried player table")
        finally:
            self._release_connection(conn)
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

        conn: connection = self._get_connection()
        try:
            self._logger.info(f"Inserting {len(rows_with_player_id):,} rows into table for {player_name_str}")
            with conn.cursor() as cursor:
                cursor.executemany(query=insert_query_str, vars_list=rows_with_player_id)
                conn.commit()
            self._logger.info(f"Successfully inserted {len(rows_with_player_id):,} rows into table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    async def insert_rows_into_franchise_per_season_stats_table(self, franchise_name_str: str, stats_list: list[tuple]) -> None:

        conn: connection = self._get_connection()
        try:
            self._logger.info(f"Inserting {len(stats_list):,} rows into table for {franchise_name_str}")
            with conn.cursor() as cursor:
                cursor.executemany(query=Constants.Queries.INSERT_INTO_FRANCHISE_PER_SEASON_STATS_TABLE_STR,
                                   vars_list=stats_list)
                conn.commit()
            self._logger.info(f"Successfully inserted {len(stats_list):,} rows into table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    async def insert_rows_into_player_table(self) -> None:
        nba_players_list: list[tuple] = await self._web_scraper.get_all_nba_players_list()

        conn: connection = self._get_connection()
        try:
            self._logger.info(f"Inserting {len(nba_players_list):,} rows in player table")
            with conn.cursor() as cursor:
                cursor.executemany(query=Constants.Queries.INSERT_INTO_PLAYER_QUERY_STR, vars_list=nba_players_list)
                conn.commit()
            self._logger.info(f"Successfully inserted {len(nba_players_list):,} rows in player table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    async def insert_rows_into_franchise_table(self) -> None:
        nba_franchise_list: list[tuple] = await self._web_scraper.get_nba_franchise_list()

        conn: connection = self._get_connection()
        try:
            self._logger.info(f"Inserting {len(nba_franchise_list):,} rows in franchise table")
            with conn.cursor() as cursor:
                cursor.executemany(query=Constants.Queries.INSERT_INTO_FRANCHISE_TABLE_QUERY_STR,
                                   vars_list=nba_franchise_list)
                conn.commit()
            self._logger.info(f"Successfully inserted {len(nba_franchise_list):,} rows in franchise table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    ## ======================================================== DROP TABLE METHODS ======================================================== ##

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_franchise_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Dropping franchise table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.DROP_FRANCHISE_TABLE_SCHEMA_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully dropped franchise table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_player_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Dropping player table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.DROP_PLAYER_TABLE_SCHEMA_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully dropped player table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

    # TODO: Determine if multiple 'drop' method are necessary, potentially condense into one method
    def drop_player_regular_season_stats_table(self) -> None:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Dropping player_regular_season_stats table")
            with conn.cursor() as cursor:
                cursor.execute(query=Constants.Queries.DROP_PLAYER_REGULAR_SEASON_TABLE_SCHEMA_QUERY_STR)
                conn.commit()
            self._logger.info("Successfully dropped player_regular_season_stats table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)
