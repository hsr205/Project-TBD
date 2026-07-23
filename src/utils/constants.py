class Constants:
    LOGGER_COLOR_RESET: str = "\033[0m"
    LOGGER_COLOR_WHITE: str = "\033[60m"
    LOGGER_COLOR_ORANGE: str = "\033[33m"
    LOGGER_COLOR_DARK_RED: str = "\033[31m"

    class Queries:


        CREATE_FRANCHISE_TABLE_SCHEMA_QUERY_STR:str = """
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

        CREATE_PLAYER_TABLE_SCHEMA_QUERY_STR:str = """
            CREATE TABLE IF NOT EXISTS player (
                id SERIAL PRIMARY KEY,
                player_name VARCHAR(100) NOT NULL,
                year_debuted INTEGER NOT NULL,
                year_retired INTEGER NOT NULL,
                position VARCHAR(5),
                height VARCHAR(5),
                weight INTEGER,
                birth_date VARCHAR(100),
                colleges VARCHAR(100)
            )
        """

        INSERT_INTO_FRANCHISE_QUERY_STR:str = """
                      INSERT INTO franchise (
                        franchise_name,
                        league_name,
                        year_established,
                        current_year,
                        num_years_in_operation,
                        num_games_played,
                        num_games_won,
                        num_games_lost,
                        win_percentage,
                        playoff_appearances,
                        division_title_wins,
                        conference_title_wins,
                        championship_title_wins
                      )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

        INSERT_INTO_PLAYER_QUERY_STR:str = """
                      INSERT INTO player (
                            player_name,
                            year_debuted,
                            year_retired,
                            position,
                            height,
                            weight,
                            birth_date,
                            colleges
                      )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """

        DROP_PLAYER_TABLE_SCHEMA_QUERY_STR:str = """
            DROP TABLE IF EXISTS player
        """

        DROP_FRANCHISE_TABLE_SCHEMA_QUERY_STR:str = """
            DROP TABLE IF EXISTS franchise
        """
