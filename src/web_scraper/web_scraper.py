import time
from datetime import datetime
from logging import Logger

from playwright.async_api import async_playwright, Page, Locator

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants


class WebScraper:

    def __init__(self, settings: Settings) -> None:
        self._base_url: str = settings.base_url
        self._current_year: int = datetime.now().year
        self._stats_table_key: str = settings.stats_table_key
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)
        self._player_stats_table_mapping_dict: dict[str, list[str, int]] = Constants.PLAYER_STATS_TABLE_MAPPING_DICT

    async def scrape_player_stats(self, page: Page, player_name: str) -> list[tuple]:
        await self._navigate_to_player_page(page=page, player_name=player_name)
        time.sleep(1)
        return await self._extract_player_stats_from_html_table(page=page, player_name=player_name)

    async def _extract_player_stats_from_html_table(self, page: Page, player_name: str) -> \
            list[tuple]:

        html_table_name_str: str = self._player_stats_table_mapping_dict.get(self._stats_table_key, "")[0]

        if html_table_name_str == "":
            self._logger.error("No value passed for html_table_name_str")
            raise Exception("No value passed for html_table_name_str")

        table_locator: Locator = page.locator(html_table_name_str)

        per_season_stats_list: list[tuple] = await self._get_per_season_stats_list(
            table_locator=table_locator,
            player_name=player_name,
        )
        self._logger.info(f"Extracted {len(per_season_stats_list):,} season of data for {player_name}")
        self._logger.info("=" * 100)

        return per_season_stats_list

    async def _get_per_season_stats_list(self, table_locator: Locator, player_name: str) -> list[tuple]:

        num_columns_in_table: int = self._player_stats_table_mapping_dict.get(self._stats_table_key, "")[1]

        await table_locator.wait_for()

        rows: list[Locator] = await table_locator.locator("tbody tr").all()

        per_season_stats_list: list[tuple] = []
        for row in rows:
            cells: list[str] = await row.locator("th, td").all_inner_texts()

            if len(cells) < num_columns_in_table:
                self._logger.info(f"Skipping incomplete row for {player_name}: {cells[0] if cells else 'unknown'}")
                continue

            if self._stats_table_key == "reg-season-qsiB8VY":
                per_season_stats_list.append(self._sanitize_stats_row(cells=cells))
            elif self._stats_table_key == "reg-season-adv-uBMv04w":
                per_season_stats_list.append(self._sanitize_advanced_stats_row(cells=cells))
            elif self._stats_table_key == "playoffs-vsy03Dw":
                per_season_stats_list.append(self._sanitize_playoff_series_row(cells=cells))

        return per_season_stats_list

    async def _navigate_to_player_page(self, page: Page, player_name: str) -> None:

        self._logger.info(f"Locating: {player_name}")
        await page.locator("input[name='search']").fill(player_name)
        time.sleep(1)
        suggestion_locator: Locator = page.locator(".ac-dataset-bbr__players .ac-suggestion").first
        await suggestion_locator.wait_for(state="visible")
        time.sleep(1)
        await suggestion_locator.click()
        self._logger.info(f"Navigating to {player_name}'s stats page")

    # TODO: Add in a component to bypass ads as they appear during scrapping
    async def get_all_nba_players_list(self) -> list[tuple]:
        all_nba_players_tuple_list: list[tuple] = []

        async with async_playwright() as playwright_obj:
            self._logger.info("Launching Chromium browser")
            self._logger.info("=" * 100)

            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page: Page = await browser.new_page()

                alphabet_list: list[str] = self._get_alphabet_list()

                for letter in alphabet_list:
                    await self.navigate_to_base_url(page=page)
                    await self._navigate_to_players_page(page=page, first_letter_of_last_name_str=letter)

                    all_nba_players_tuple_list.extend(await self._extract_players_data(page=page))
                    time.sleep(5)

                self._logger.info(f"Total players gathered: {len(all_nba_players_tuple_list):,}")

            self._logger.info("Browser closed successfully")

        return all_nba_players_tuple_list

    async def _navigate_to_players_page(self, page: Page, first_letter_of_last_name_str: str) -> None:
        await page.get_by_role(role="link", name="Players", exact=False).first.click()
        self._logger.info("Players Link Clicked")
        time.sleep(3)
        await page.locator("#div_alphabet").get_by_role(role="link", name=first_letter_of_last_name_str.upper(),
                                                        exact=True).click()
        time.sleep(5)
        self._logger.info(
            f"Clicked on Players with last names starting with: '{first_letter_of_last_name_str.upper()}'")

    async def _extract_players_data(self, page: Page) -> list[tuple]:

        table_locator: Locator = page.locator("table#players")

        await table_locator.wait_for()

        table_rows_list: list[Locator] = await table_locator.locator("tbody tr:not(.thead)").all()

        players_list: list[tuple] = []
        for row in table_rows_list:
            cells: list[str] = await row.locator("th, td").all_inner_texts()
            sanitized_player_tuple: tuple = self._sanitize_player_row(cells=cells)
            players_list.append(sanitized_player_tuple)

        self._logger.info(f"Scraped {len(players_list)} player rows")
        self._logger.info("=" * 100)

        return players_list

    async def get_nba_franchise_list(self) -> list[tuple]:
        nba_franchise_tuple_list: list[tuple] = []

        async with async_playwright() as playwright_obj:
            self._logger.info("Launching Chromium browser")
            self._logger.info("=" * 100)

            async with await playwright_obj.chromium.launch(headless=True) as browser:
                page: Page = await browser.new_page()

                await self.navigate_to_base_url(page=page)

                await self._navigate_to_teams_page(page=page)

                table_locator: Locator = await self._locate_active_franchise_table(page=page)

                nba_franchise_tuple_list = await self._extract_franchise_data_to_list(table_locator=table_locator)

            self._logger.info("Browser closed successfully")

        return nba_franchise_tuple_list

    async def navigate_to_base_url(self, page: Page) -> None:
        self._logger.info(f"Navigating to {self._base_url}")
        await page.goto(url=self._base_url)

    async def _navigate_to_teams_page(self, page: Page) -> None:
        await page.get_by_role(role="link", name="Teams", exact=False).first.click()
        self._logger.info("Players Link Clicked")

    async def _locate_active_franchise_table(self, page: Page) -> Locator:
        await page.get_by_role(role="table", name="Active Franchises Table").get_by_label(
            text="Franchise").first.click()
        self._logger.info("Located Active Franchises Table")
        table_locator: Locator = page.get_by_role(role="table", name="Active Franchises Table")
        await table_locator.locator("tbody tr.full_table").first.wait_for()
        return table_locator

    async def _extract_franchise_data_to_list(self, table_locator: Locator) -> list[tuple]:
        locator_list_results: list[Locator] = await table_locator.locator("tbody tr.full_table").all()

        franchise_list: list[tuple] = []
        for table_row in locator_list_results:
            table_cell_tuple: tuple = tuple(await table_row.locator("th, td").all_inner_texts())
            franchise_list.append(table_cell_tuple)

        self._logger.info(f"Scraped {len(franchise_list)} rows")
        self._logger.info("=" * 100)

        return franchise_list

    def _get_alphabet_list(self) -> list[str]:

        alphabet_list: list[str] = []

        for element in range(65, 91):
            ascii_character: str = chr(element)

            if element == 88:
                self._logger.info("Skipping X last names")
                continue

            alphabet_list.append(ascii_character)

        return alphabet_list

    def _sanitize_playoff_series_row(self, cells: list[str]) -> tuple:
        # Playoff series table column order (37 cols):
        # Season, Age, Team, Lg, Round, Opp, W/L, G,
        # Per Game: MP, PTS, TRB, AST, STL, BLK,
        # Totals: FG, FGA, FG%, 3P, 3PA, 3P%, 2P, 2PA, 2P%, eFG%,
        #         FT, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS,
        # Awards
        return (
            self.to_str_or_none(cells[0]),  # season
            self.to_int_or_none(cells[1]),  # age
            self.to_str_or_none(cells[2]),  # team
            self.to_str_or_none(cells[3]),  # league
            self.to_str_or_none(cells[4]),  # round
            self.to_str_or_none(cells[5]),  # opponent
            self.to_str_or_none(cells[6]),  # series_result (W/L)
            self.to_int_or_none(cells[7]),  # games
            self.to_decimal_or_none(cells[8]),  # mp_per_g
            self.to_decimal_or_none(cells[9]),  # pts_per_g
            self.to_decimal_or_none(cells[10]),  # trb_per_g
            self.to_decimal_or_none(cells[11]),  # ast_per_g
            self.to_decimal_or_none(cells[12]),  # stl_per_g
            self.to_decimal_or_none(cells[13]),  # blk_per_g
            self.to_int_or_none(cells[14]),  # fg
            self.to_int_or_none(cells[15]),  # fga
            self.to_decimal_or_none(cells[16]),  # fg_pct
            self.to_int_or_none(cells[17]),  # fg3
            self.to_int_or_none(cells[18]),  # fg3a
            self.to_decimal_or_none(cells[19]),  # fg3_pct
            self.to_int_or_none(cells[20]),  # fg2
            self.to_int_or_none(cells[21]),  # fg2a
            self.to_decimal_or_none(cells[22]),  # fg2_pct
            self.to_decimal_or_none(cells[23]),  # efg_pct
            self.to_int_or_none(cells[24]),  # ft
            self.to_int_or_none(cells[25]),  # fta
            self.to_decimal_or_none(cells[26]),  # ft_pct
            self.to_int_or_none(cells[27]),  # orb
            self.to_int_or_none(cells[28]),  # drb
            self.to_int_or_none(cells[29]),  # trb
            self.to_int_or_none(cells[30]),  # ast
            self.to_int_or_none(cells[31]),  # stl
            self.to_int_or_none(cells[32]),  # blk
            self.to_int_or_none(cells[33]),  # tov
            self.to_int_or_none(cells[34]),  # pf
            self.to_int_or_none(cells[35]),  # pts
            self.to_str_or_none(cells[36]),  # awards
        )

    def _sanitize_advanced_stats_row(self, cells: list[str]) -> tuple:
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

    def _sanitize_stats_row(self, cells: list[str]) -> tuple:
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

    def _sanitize_player_row(self, cells: list[str]) -> tuple:

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

    def to_int_or_none(self, value: str) -> int | None:
        """Convert a string to int, returning None if empty or non-numeric."""
        stripped = value.strip()
        return int(stripped) if stripped.lstrip("-").isdigit() else None

    def to_decimal_or_none(self, value: str) -> float | None:
        """Convert a string to float, returning None if empty or non-numeric."""
        stripped = value.strip()
        try:
            return float(stripped) if stripped else None
        except ValueError:
            return None

    def to_str_or_none(self, value: str) -> str | None:
        """Convert a string to None if empty."""
        stripped = value.strip()
        return stripped if stripped else None
