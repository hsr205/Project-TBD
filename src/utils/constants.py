class Constants:
    LOGGER_COLOR_RESET: str = "\033[0m"
    LOGGER_COLOR_WHITE: str = "\033[60m"
    LOGGER_COLOR_ORANGE: str = "\033[33m"
    LOGGER_COLOR_DARK_RED: str = "\033[31m"

    class Queries:


        CREATE_FRANCHISES_TABLE_SCHEMA_QUERY_STR:str = """
            CREATE TABLE IF NOT EXISTS franchise (
                id SERIAL PRIMARY KEY,
                franchise_name VARCHAR(100) NOT NULL,
                league_name VARCHAR(20) NOT NULL,
                year_established VARCHAR(20) NOT NULL,
                current_year VARCHAR(20) NOT NULL,
                num_years_in_operation INTEGER NOT NULL,
                num_games_played INTEGER NOT NULL,
                num_games_won INTEGER NOT NULL,
                num_games_lost INTEGER NOT NULL,
                win_percentage NUMERIC(4,4) NOT NULL,
                playoff_appearances INTEGER NOT NULL,
                division_title_wins INTEGER NOT NULL,
                conference_title_wins INTEGER NOT NULL,
                championship_title_wins INTEGER NOT NULL
            )
        """

        DROP_FRANCHISES_TABLE_SCHEMA_QUERY_STR:str = """
            DROP TABLE IF EXISTS franchise
        """
