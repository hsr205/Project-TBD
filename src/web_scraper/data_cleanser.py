class DataCleanser:

    def __init__(self) -> None:
        pass

    def sanitize_franchise_season_row(self, cells: list[str]) -> tuple:
        # Franchise seasons table column order (19 cols):
        # Season, Lg, Team, W, L, W/L%, Finish, SRS,
        # DUMMY (separator),
        # Pace, Rel Pace, ORtg, Rel ORtg, DRtg, Rel DRtg,
        # DUMMY (separator),
        # Playoffs, Coaches, Top WS
        return (
            self.to_str_or_none(cells[0]),      # season
            self.to_str_or_none(cells[1]),      # league
            self.to_str_or_none(cells[2]),      # team_name
            self.to_int_or_none(cells[3]),      # wins
            self.to_int_or_none(cells[4]),      # losses
            self.to_decimal_or_none(cells[5]),  # win_loss_pct
            self.to_str_or_none(cells[6]),      # finish
            self.to_decimal_or_none(cells[7]),  # srs
            # cells[8] = DUMMY separator — skipped
            self.to_decimal_or_none(cells[9]),  # pace
            self.to_decimal_or_none(cells[10]), # pace_rel
            self.to_decimal_or_none(cells[11]), # off_rtg
            self.to_decimal_or_none(cells[12]), # off_rtg_rel
            self.to_decimal_or_none(cells[13]), # def_rtg
            self.to_decimal_or_none(cells[14]), # def_rtg_rel
            # cells[15] = DUMMY separator — skipped
            self.to_str_or_none(cells[16]),     # playoffs
            self.to_str_or_none(cells[17]),     # coaches
            self.to_str_or_none(cells[18]),     # top_ws
        )

    def sanitize_playoff_series_row(self, stat_map: dict[str, str]) -> tuple:
        return (
            self.to_str_or_none(stat_map.get("year_id")),  # Basketball Reference uses 'year_id' for Season
            self.to_int_or_none(stat_map.get("age")),
            self.to_str_or_none(stat_map.get("team_name_abbr")),  # 'team_name_abbr'
            self.to_str_or_none(stat_map.get("comp_name_abbr")),  # 'comp_name_abbr'
            self.to_str_or_none(stat_map.get("ps_round")),  # 'ps_round'
            self.to_str_or_none(stat_map.get("opp_name_abbr")),  # 'opp_name_abbr'
            self.to_str_or_none(stat_map.get("series_result")),  # 'series_result'
            self.to_int_or_none(stat_map.get("games")),  # 'games'

            # Per Game
            self.to_decimal_or_none(stat_map.get("mp_per_g")),
            self.to_decimal_or_none(stat_map.get("pts_per_g")),
            self.to_decimal_or_none(stat_map.get("trb_per_g")),
            self.to_decimal_or_none(stat_map.get("ast_per_g")),
            self.to_decimal_or_none(stat_map.get("stl_per_g")),
            self.to_decimal_or_none(stat_map.get("blk_per_g")),

            # Totals
            self.to_int_or_none(stat_map.get("fg")),
            self.to_int_or_none(stat_map.get("fga")),
            self.to_decimal_or_none(stat_map.get("fg_pct")),
            self.to_int_or_none(stat_map.get("fg3")),
            self.to_int_or_none(stat_map.get("fg3a")),
            self.to_decimal_or_none(stat_map.get("fg3_pct")),
            self.to_int_or_none(stat_map.get("fg2")),
            self.to_int_or_none(stat_map.get("fg2a")),
            self.to_decimal_or_none(stat_map.get("fg2_pct")),
            self.to_decimal_or_none(stat_map.get("efg_pct")),
            self.to_int_or_none(stat_map.get("ft")),
            self.to_int_or_none(stat_map.get("fta")),
            self.to_decimal_or_none(stat_map.get("ft_pct")),
            self.to_int_or_none(stat_map.get("orb")),
            self.to_int_or_none(stat_map.get("drb")),
            self.to_int_or_none(stat_map.get("trb")),
            self.to_int_or_none(stat_map.get("ast")),
            self.to_int_or_none(stat_map.get("stl")),
            self.to_int_or_none(stat_map.get("blk")),
            self.to_int_or_none(stat_map.get("tov")),
            self.to_int_or_none(stat_map.get("pf")),
            self.to_int_or_none(stat_map.get("pts")),
            self.to_str_or_none(stat_map.get("awards")),
        )

    def sanitize_advanced_stats_row(self, cells: list[str]) -> tuple:
        # Advanced table column order (29 cols):
        # Season, Age, Team, Lg, Pos, G, GS, MP,
        # PER, TS%, 3PAr, FTr, ORB%, DRB%, TRB%, AST%, STL%, BLK%, TOV%, USG%,
        # OWS, DWS, WS, WS/48, OBPM, DBPM, BPM, VORP, Awards
        return (
            self.to_str_or_none(cells[0]),  # season
            self.to_int_or_none(cells[1]),  # age
            self.to_str_or_none(cells[2]),  # team
            self.to_str_or_none(cells[3]),  # league
            self.to_str_or_none(cells[4]),  # position
            self.to_int_or_none(cells[5]),  # games_played
            self.to_int_or_none(cells[6]),  # games_started
            self.to_int_or_none(cells[7]),  # minutes_played (total, not per game)
            self.to_decimal_or_none(cells[8]),  # per
            self.to_decimal_or_none(cells[9]),  # ts_pct
            self.to_decimal_or_none(cells[10]),  # three_point_attempt_rate
            self.to_decimal_or_none(cells[11]),  # free_throw_rate
            self.to_decimal_or_none(cells[12]),  # orb_pct
            self.to_decimal_or_none(cells[13]),  # drb_pct
            self.to_decimal_or_none(cells[14]),  # trb_pct
            self.to_decimal_or_none(cells[15]),  # ast_pct
            self.to_decimal_or_none(cells[16]),  # stl_pct
            self.to_decimal_or_none(cells[17]),  # blk_pct
            self.to_decimal_or_none(cells[18]),  # tov_pct
            self.to_decimal_or_none(cells[19]),  # usg_pct
            self.to_decimal_or_none(cells[20]),  # ows
            self.to_decimal_or_none(cells[21]),  # dws
            self.to_decimal_or_none(cells[22]),  # ws
            self.to_decimal_or_none(cells[23]),  # ws_per_48
            self.to_decimal_or_none(cells[24]),  # obpm
            self.to_decimal_or_none(cells[25]),  # dbpm
            self.to_decimal_or_none(cells[26]),  # bpm
            self.to_decimal_or_none(cells[27]),  # vorp
            self.to_str_or_none(cells[28]),  # awards
        )

    def sanitize_stats_row(self, cells: list[str]) -> tuple:
        # Column order: Season, Age, Team, Lg, Pos, G, GS, MP, FG, FGA, FG%, 3P, 3PA, 3P%,
        #               2P, 2PA, 2P%, eFG%, FT, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, Awards
        return (
            self.to_str_or_none(cells[0]),  # season       VARCHAR
            self.to_int_or_none(cells[1]),  # age          INTEGER
            self.to_str_or_none(cells[2]),  # team         VARCHAR
            self.to_str_or_none(cells[3]),  # league       VARCHAR
            self.to_str_or_none(cells[4]),  # position     VARCHAR
            self.to_int_or_none(cells[5]),  # games_played INTEGER
            self.to_int_or_none(cells[6]),  # games_started INTEGER
            self.to_decimal_or_none(cells[7]),  # minutes_played_per_game
            self.to_decimal_or_none(cells[8]),  # field_goals_made
            self.to_decimal_or_none(cells[9]),  # field_goals_attempted
            self.to_decimal_or_none(cells[10]),  # field_goal_percentage
            self.to_decimal_or_none(cells[11]),  # three_pointers_made
            self.to_decimal_or_none(cells[12]),  # three_pointers_attempted
            self.to_decimal_or_none(cells[13]),  # three_point_percentage
            self.to_decimal_or_none(cells[14]),  # two_pointers_made
            self.to_decimal_or_none(cells[15]),  # two_pointers_attempted
            self.to_decimal_or_none(cells[16]),  # two_point_percentage
            self.to_decimal_or_none(cells[17]),  # effective_field_goal_percentage
            self.to_decimal_or_none(cells[18]),  # free_throws_made
            self.to_decimal_or_none(cells[19]),  # free_throws_attempted
            self.to_decimal_or_none(cells[20]),  # free_throw_percentage
            self.to_decimal_or_none(cells[21]),  # offensive_rebounds
            self.to_decimal_or_none(cells[22]),  # defensive_rebounds
            self.to_decimal_or_none(cells[23]),  # rebound_avg
            self.to_decimal_or_none(cells[24]),  # assist_avg
            self.to_decimal_or_none(cells[25]),  # steal_avg
            self.to_decimal_or_none(cells[26]),  # block_avg
            self.to_decimal_or_none(cells[27]),  # turnover_avg
            self.to_decimal_or_none(cells[28]),  # personal_foul_avg
            self.to_decimal_or_none(cells[29]),  # point_avg
            self.to_str_or_none(cells[30]),  # awards       VARCHAR
        )

    def sanitize_player_row(self, cells: list[str]) -> tuple:

        # NOTE:
        # Indices based on Basketball Reference player table column order:
        # 0: player_name, 1: year_debuted, 2: year_retired, 3: position,
        # 4: height, 5: weight, 6: birth_date, 7: colleges
        return (
            self.to_str_or_none(value=cells[0]),
            self.to_int_or_none(value=cells[1]),
            self.to_int_or_none(value=cells[2]),
            self.to_str_or_none(value=cells[3]),
            self.to_str_or_none(value=cells[4]),
            self.to_int_or_none(value=cells[5]),
            self.to_str_or_none(value=cells[6]),
            self.to_str_or_none(value=cells[7]),
        )

    def sanitize_advanced_stats_row_by_stat(self, stat_map: dict[str, str]) -> tuple:
        """Sanitize an advanced stats row using data-stat keys — handles missing columns gracefully."""
        return (
            self.to_str_or_none(stat_map.get("year_id", "")),
            self.to_int_or_none(stat_map.get("age", "")),
            self.to_str_or_none(stat_map.get("team_name_abbr", "")),
            self.to_str_or_none(stat_map.get("comp_name_abbr", "")),
            self.to_str_or_none(stat_map.get("pos", "")),
            self.to_int_or_none(stat_map.get("games", "")),
            self.to_int_or_none(stat_map.get("games_started", "")),
            self.to_int_or_none(stat_map.get("mp", "")),
            self.to_decimal_or_none(stat_map.get("per", "")),
            self.to_decimal_or_none(stat_map.get("ts_pct", "")),
            self.to_decimal_or_none(stat_map.get("fg3a_per_fga_pct", "")),
            self.to_decimal_or_none(stat_map.get("fta_per_fga_pct", "")),
            self.to_decimal_or_none(stat_map.get("orb_pct", "")),
            self.to_decimal_or_none(stat_map.get("drb_pct", "")),
            self.to_decimal_or_none(stat_map.get("trb_pct", "")),
            self.to_decimal_or_none(stat_map.get("ast_pct", "")),
            self.to_decimal_or_none(stat_map.get("stl_pct", "")),
            self.to_decimal_or_none(stat_map.get("blk_pct", "")),
            self.to_decimal_or_none(stat_map.get("tov_pct", "")),
            self.to_decimal_or_none(stat_map.get("usg_pct", "")),
            self.to_decimal_or_none(stat_map.get("ows", "")),
            self.to_decimal_or_none(stat_map.get("dws", "")),
            self.to_decimal_or_none(stat_map.get("ws", "")),
            self.to_decimal_or_none(stat_map.get("ws_per_48", "")),
            self.to_decimal_or_none(stat_map.get("obpm", "")),
            self.to_decimal_or_none(stat_map.get("dbpm", "")),
            self.to_decimal_or_none(stat_map.get("bpm", "")),
            self.to_decimal_or_none(stat_map.get("vorp", "")),
            self.to_str_or_none(stat_map.get("awards", "")),
        )

    def sanitize_stats_row_by_stat(self, stat_map: dict[str, str]) -> tuple:
        """Sanitize a per game stats row using data-stat keys — handles missing columns gracefully."""
        return (
                self.to_str_or_none(stat_map.get("year_id", "")),       # season
            self.to_int_or_none(stat_map.get("age", "")),           # age
            self.to_str_or_none(stat_map.get("team_name_abbr", "")),# team
            self.to_str_or_none(stat_map.get("comp_name_abbr", "")),# league
            self.to_str_or_none(stat_map.get("pos", "")),           # position
            self.to_int_or_none(stat_map.get("games", "")),         # games_played
            self.to_int_or_none(stat_map.get("games_started", "")), # games_started
            self.to_decimal_or_none(stat_map.get("mp_per_g", "")),  # minutes_played_per_game
            self.to_decimal_or_none(stat_map.get("fg_per_g", "")),  # field_goals_made
            self.to_decimal_or_none(stat_map.get("fga_per_g", "")), # field_goals_attempted
            self.to_decimal_or_none(stat_map.get("fg_pct", "")),    # field_goal_percentage
            self.to_decimal_or_none(stat_map.get("fg3_per_g", "")), # three_pointers_made
            self.to_decimal_or_none(stat_map.get("fg3a_per_g", "")),# three_pointers_attempted
            self.to_decimal_or_none(stat_map.get("fg3_pct", "")),   # three_point_percentage
            self.to_decimal_or_none(stat_map.get("fg2_per_g", "")), # two_pointers_made
            self.to_decimal_or_none(stat_map.get("fg2a_per_g", "")),# two_pointers_attempted
            self.to_decimal_or_none(stat_map.get("fg2_pct", "")),   # two_point_percentage
            self.to_decimal_or_none(stat_map.get("efg_pct", "")),   # effective_field_goal_percentage
            self.to_decimal_or_none(stat_map.get("ft_per_g", "")),  # free_throws_made
            self.to_decimal_or_none(stat_map.get("fta_per_g", "")), # free_throws_attempted
            self.to_decimal_or_none(stat_map.get("ft_pct", "")),    # free_throw_percentage
            self.to_decimal_or_none(stat_map.get("orb_per_g", "")), # offensive_rebounds
            self.to_decimal_or_none(stat_map.get("drb_per_g", "")), # defensive_rebounds
            self.to_decimal_or_none(stat_map.get("trb_per_g", "")), # rebound_avg
            self.to_decimal_or_none(stat_map.get("ast_per_g", "")), # assist_avg
            self.to_decimal_or_none(stat_map.get("stl_per_g", "")), # steal_avg
            self.to_decimal_or_none(stat_map.get("blk_per_g", "")), # block_avg
            self.to_decimal_or_none(stat_map.get("tov_per_g", "")), # turnover_avg
            self.to_decimal_or_none(stat_map.get("pf_per_g", "")),  # personal_foul_avg
            self.to_decimal_or_none(stat_map.get("pts_per_g", "")), # point_avg
            self.to_str_or_none(stat_map.get("awards", "")),        # awards
        )

    def to_int_or_none(self, value: str | None) -> int | None:
        """Convert a string to int, returning None if empty, None, or non-numeric."""
        if not value:
            return None
        val_clean = value.strip()
        if not val_clean:
            return None
        return int(val_clean) if val_clean.lstrip("-").isdigit() else None

    def to_decimal_or_none(self, value: str | None) -> float | None:
        """Convert a string to float, returning None if empty, None, or non-numeric."""
        if not value:
            return None
        val_clean = value.strip()
        if not val_clean:
            return None
        try:
            return float(val_clean)
        except ValueError:
            return None

    def to_str_or_none(self, value: str | None) -> str | None:
        """Convert a string to None if empty, whitespace-only, or None."""
        if not value:
            return None
        val_clean = value.strip()
        return val_clean if val_clean else None