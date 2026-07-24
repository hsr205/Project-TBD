class Constants:
    LOGGER_COLOR_RESET: str = "\033[0m"
    LOGGER_COLOR_WHITE: str = "\033[60m"
    LOGGER_COLOR_ORANGE: str = "\033[33m"
    LOGGER_COLOR_DARK_RED: str = "\033[31m"

    PLAYER_STATS_TABLE_MAPPING_DICT: dict[str, list[str, int]] = {
        "reg-season-qsiB8VY": ["table#per_game_stats", 31],
        "reg-season-adv-uBMv04w": ["table#advanced", 29],
        "playoffs-vsy03Dw": ["table#playoffs_series", 37],
    }

    class Queries:
        ## ======================================================== CREATE TABLE QUERIES ======================================================== ##

        CREATE_FRANCHISE_TABLE_SCHEMA_QUERY_STR: str = """
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

        CREATE_PLAYER_TABLE_SCHEMA_QUERY_STR: str = """
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

        # TODO: Think about connecting to franchise table
        CREATE_PLAYER_STATS_TABLE_QUERY_STR: str = """
            CREATE TABLE IF NOT EXISTS player_regular_season_stats (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL,
                season VARCHAR(20),
                age INTEGER,
                team VARCHAR(10),
                league VARCHAR(10),
                position VARCHAR(10),
                games_played INTEGER,
                games_started INTEGER,
                minutes_played_per_game DECIMAL,
                field_goals_made DECIMAL,
                field_goals_attempted DECIMAL,
                field_goal_percentage DECIMAL,
                three_pointers_made DECIMAL,
                three_pointers_attempted DECIMAL,
                three_point_percentage DECIMAL,
                two_pointers_made DECIMAL,
                two_pointers_attempted DECIMAL,
                two_point_percentage DECIMAL,
                effective_field_goal_percentage DECIMAL,
                free_throws_made DECIMAL,
                free_throws_attempted DECIMAL,
                free_throw_percentage DECIMAL,
                offensive_rebounds DECIMAL,
                defensive_rebounds DECIMAL,
                rebound_avg DECIMAL,
                assist_avg DECIMAL,
                steal_avg DECIMAL,
                block_avg DECIMAL,
                turnover_avg DECIMAL,
                personal_foul_avg DECIMAL,
                point_avg DECIMAL,
                awards VARCHAR(100),
                CONSTRAINT fk_player FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE
            )
        """

        CREATE_PLAYER_ADVANCED_STATS_TABLE_QUERY_STR: str = """
            CREATE TABLE IF NOT EXISTS player_regular_season_advanced_stats (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL,
                season VARCHAR(20),
                age INTEGER,
                team VARCHAR(10),
                league VARCHAR(10),
                position VARCHAR(10),
                games_played INTEGER,
                games_started INTEGER,
                minutes_played INTEGER,
                per DECIMAL,
                ts_pct DECIMAL,
                three_point_attempt_rate DECIMAL,
                free_throw_rate DECIMAL,
                orb_pct DECIMAL,
                drb_pct DECIMAL,
                trb_pct DECIMAL,
                ast_pct DECIMAL,
                stl_pct DECIMAL,
                blk_pct DECIMAL,
                tov_pct DECIMAL,
                usg_pct DECIMAL,
                ows DECIMAL,
                dws DECIMAL,
                ws DECIMAL,
                ws_per_48 DECIMAL,
                obpm DECIMAL,
                dbpm DECIMAL,
                bpm DECIMAL,
                vorp DECIMAL,
                awards VARCHAR(100),
                CONSTRAINT fk_player_adv FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE
            )
        """

        CREATE_PLAYER_PLAYOFF_SERIES_STATS_TABLE_QUERY_STR: str = """
            CREATE TABLE IF NOT EXISTS player_playoff_series_stats (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL,
                season VARCHAR(20),
                age INTEGER,
                team VARCHAR(10),
                league VARCHAR(10),
                round VARCHAR(10),
                opponent VARCHAR(10),
                series_result VARCHAR(20),
                games INTEGER,
                mp_per_g DECIMAL,
                pts_per_g DECIMAL,
                trb_per_g DECIMAL,
                ast_per_g DECIMAL,
                stl_per_g DECIMAL,
                blk_per_g DECIMAL,
                fg INTEGER,
                fga INTEGER,
                fg_pct DECIMAL,
                fg3 INTEGER,
                fg3a INTEGER,
                fg3_pct DECIMAL,
                fg2 INTEGER,
                fg2a INTEGER,
                fg2_pct DECIMAL,
                efg_pct DECIMAL,
                ft INTEGER,
                fta INTEGER,
                ft_pct DECIMAL,
                orb INTEGER,
                drb INTEGER,
                trb INTEGER,
                ast INTEGER,
                stl INTEGER,
                blk INTEGER,
                tov INTEGER,
                pf INTEGER,
                pts INTEGER,
                awards VARCHAR(100),
                CONSTRAINT fk_player_playoff FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE
            )
        """

        ## ======================================================== INSERT TABLE QUERIES ======================================================== ##

        INSERT_INTO_PLAYER_REGULAR_SEASON_ADVANCED_STATS_TABLE_STR: str = """
            INSERT INTO player_regular_season_advanced_stats (
                player_id,
                season,
                age,
                team,
                league,
                position,
                games_played,
                games_started,
                minutes_played,
                per,
                ts_pct,
                three_point_attempt_rate,
                free_throw_rate,
                orb_pct,
                drb_pct,
                trb_pct,
                ast_pct,
                stl_pct,
                blk_pct,
                tov_pct,
                usg_pct,
                ows,
                dws,
                ws,
                ws_per_48,
                obpm,
                dbpm,
                bpm,
                vorp,
                awards
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        INSERT_INTO_PLAYER_REGULAR_SEASON_STATS_TABLE_STR: str = """
            INSERT INTO player_regular_season_stats (
                player_id,
                season,
                age,
                team,
                league,
                position,
                games_played,
                games_started,
                minutes_played_per_game,
                field_goals_made,
                field_goals_attempted,
                field_goal_percentage,
                three_pointers_made,
                three_pointers_attempted,
                three_point_percentage,
                two_pointers_made,
                two_pointers_attempted,
                two_point_percentage,
                effective_field_goal_percentage,
                free_throws_made,
                free_throws_attempted,
                free_throw_percentage,
                offensive_rebounds,
                defensive_rebounds,
                rebound_avg,
                assist_avg,
                steal_avg,
                block_avg,
                turnover_avg,
                personal_foul_avg,
                point_avg,
                awards
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        INSERT_INTO_FRANCHISE_QUERY_STR: str = """
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

        INSERT_INTO_PLAYER_QUERY_STR: str = """
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

        INSERT_INTO_PLAYER_PLAYOFF_SERIES_STATS_TABLE_STR: str = """
            INSERT INTO player_playoff_series_stats (
                player_id,
                season,
                age,
                team,
                league,
                round,
                opponent,
                series_result,
                games,
                mp_per_g,
                pts_per_g,
                trb_per_g,
                ast_per_g,
                stl_per_g,
                blk_per_g,
                fg,
                fga,
                fg_pct,
                fg3,
                fg3a,
                fg3_pct,
                fg2,
                fg2a,
                fg2_pct,
                efg_pct,
                ft,
                fta,
                ft_pct,
                orb,
                drb,
                trb,
                ast,
                stl,
                blk,
                tov,
                pf,
                pts,
                awards
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        ## ======================================================== DROP TABLE QUERIES ======================================================== ##

        DROP_FRANCHISE_TABLE_SCHEMA_QUERY_STR: str = """
            DROP TABLE IF EXISTS franchise
        """

        DROP_PLAYER_TABLE_SCHEMA_QUERY_STR: str = """
            DROP TABLE IF EXISTS player
        """

        DROP_PLAYER_REGULAR_SEASON_TABLE_SCHEMA_QUERY_STR: str = """
             DROP TABLE IF EXISTS player_regular_season_stats CASCADE
         """

        DROP_PLAYER_REGULAR_SEASON_ADVANCED_TABLE_SCHEMA_QUERY_STR: str = """
             DROP TABLE IF EXISTS player_regular_season_advanced_stats CASCADE
         """

        DROP_PLAYER_PLAYER_PLAYOFF_SERIES_TABLE_SCHEMA_QUERY_STR: str = """
             DROP TABLE IF EXISTS player_playoff_series_stats CASCADE
         """

        ## ======================================================== FREQUENT QUERIES ======================================================== ##

        QUERY_PLAYER_TABLE_FOR_CURRENT_PLAYERS: str = """
            SELECT id, player_name
            FROM player
            WHERE year_retired = EXTRACT(YEAR FROM CURRENT_DATE);
        """

        QUERY_PLAYER_TABLE_FOR_RETIRED_PLAYERS: str = """
            SELECT id, player_name
            FROM player
            WHERE year_retired < EXTRACT(YEAR FROM CURRENT_DATE);
        """
