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

    def get_result_dict_from_queried_table(self) -> dict[int, str]:
        conn: connection = self._get_connection()
        try:
            self._logger.info("Querying table from SQL database:")
            with conn.cursor() as cursor:
                # TODO: Find a way to do this less manually
                cursor.execute(query=Constants.Queries.QUERY_PLAYER_TABLE_FOR_ALL_MISSED_NBA_PLAYERS)
                query_result_list: list[tuple] = cursor.fetchall()

            self._logger.info(f"Returned {len(query_result_list):,} rows from queried table")

            player_dict: dict[int, str] = {
                element[0]: element[1] for element in query_result_list
            }
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

        return player_dict

    def get_all_regular_season_career_averages_list(self) -> tuple[list[str], list[tuple]]:

        conn: connection = self._get_connection()
        try:
            self._logger.info("Querying table from SQL database:")
            with conn.cursor() as cursor:
                # TODO: Find a way to do this less manually
                cursor.execute(query=Constants.Queries.QUERY_DATABASE_FOR_ALL_REGULAR_SEASON_CAREER_AVERAGES)
                query_result_list: list[tuple] = cursor.fetchall()
                column_names_list: list[str] = [col[0] for col in cursor.description]

            self._logger.info(f"Returned {len(query_result_list):,} rows from queried table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

        return column_names_list, query_result_list

    def get_all_regular_season_advanced_career_averages_list(self) -> tuple[list[str], list[tuple]]:

        conn: connection = self._get_connection()
        try:
            self._logger.info("Querying table from SQL database:")
            with conn.cursor() as cursor:
                # TODO: Find a way to do this less manually
                cursor.execute(
                    query=Constants.Queries.QUERY_DATABASE_FOR_SPECIFIC_REGULAR_SEASON_ADVANCED_CAREER_AVERAGES)
                query_result_list: list[tuple] = cursor.fetchall()
                column_names_list: list[str] = [col[0] for col in cursor.description]

            self._logger.info(f"Returned {len(query_result_list):,} rows from queried table")
        finally:
            self._release_connection(conn)
        self._logger.info("=" * 100)

        return column_names_list, query_result_list

    def get_immaculate_grid_query_results(self, query_elements_tuple: tuple) -> tuple[list[str], list[tuple]]:

        self._logger.info(f"query_elements_tuple = {query_elements_tuple}")

        where_clause: str = self._build_where_clause(query_elements_tuple)

        query_str: str = f"""
            SELECT *
            FROM (
                    SELECT p.player_name
                    FROM player p
                    JOIN player_regular_season_stats p_reg ON p.id = p_reg.player_id
                    WHERE {where_clause}
                    GROUP BY p.id, p.player_name
                    ORDER BY MIN(split_part(p_reg.season, '-', 1)::integer) ASC
                    LIMIT 20
                 )
            ORDER BY RANDOM() LIMIT 1;
            """

        conn: connection = self._get_connection()
        try:
            self._logger.info("Querying table from SQL database:")
            with conn.cursor() as cursor:
                cursor.execute(query_str)
                query_result_list: list[tuple] = cursor.fetchall()
                column_names_list: list[str] = [col[0] for col in cursor.description]

            self._logger.info(f"Returned {len(query_result_list):,} rows")
            self._logger.info("=" * 100)
            return column_names_list, query_result_list
        finally:
            self._release_connection(conn)

    def _build_where_clause(self, elements: tuple) -> str:
        conditions: list[str] = [e for e in elements if e.startswith(('p.', 'p_reg.')) or ' ' in e]
        teams: list[str] = [e for e in elements if e not in conditions]

        # Two-team case requires the subquery
        if len(teams) == 2:
            team_list: str = f"('{teams[0]}', '{teams[1]}')"
            return f"""p_reg.team IN {team_list}
                    AND p.id IN (
                        SELECT player_id FROM player_regular_season_stats
                        WHERE team IN {team_list}
                        GROUP BY player_id HAVING COUNT(DISTINCT team) = 2
                    )"""

        # Combine 1-team and 0-team cases into a single list joined by AND
        all_clauses: list[str] = [f"p_reg.team = '{t}'" for t in teams] + conditions
        return " AND ".join(all_clauses)

    ## ======================================================== INSERT INTO TABLE METHODS ======================================================== ##

    async def insert_rows_into_table(self,
                                     search_name: str,
                                     stats_list: list[tuple],
                                     entity_dict: dict[int, str],
                                     insert_query_str: str) -> None:
        entity_id: int | None = next(
            (entity_id for entity_id, name in entity_dict.items() if name == search_name),
            None)

        if entity_id is None:
            self._logger.warning(f"No entity_id found for '{search_name}' — skipping stats insert")
            return

        # Prepend player_id to each stats row tuple
        rows_with_entity_id: list[tuple] = [(entity_id, *row) for row in stats_list]

        conn: connection = self._get_connection()
        try:
            self._logger.info(f"Inserting {len(rows_with_entity_id):,} rows into table for {search_name}")
            with conn.cursor() as cursor:
                cursor.executemany(query=insert_query_str, vars_list=rows_with_entity_id)
                conn.commit()
            self._logger.info(f"Successfully inserted {len(rows_with_entity_id):,} rows into table")
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
