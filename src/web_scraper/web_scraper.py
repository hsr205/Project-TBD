import asyncio
from logging import Logger

from playwright.async_api import async_playwright, Page, Locator

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.data_cleanser import DataCleanser


class WebScraper:

    def __init__(self, settings: Settings) -> None:
        self._base_url: str = settings.base_url
        self._stats_table_key: str = settings.stats_table_key
        self._data_cleanser: DataCleanser = DataCleanser()
        self._immaculate_grid_url: str = settings.immaculate_grid_url
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)
        self._player_stats_table_mapping_dict: dict[str, list[str, int]] = Constants.PLAYER_STATS_TABLE_MAPPING_DICT

    async def scrape_stats(self, page: Page, search_name: str) -> list[tuple]:
        await self._navigate_to_specified_page(page=page, search_name=search_name)
        await asyncio.sleep(1)

        if search_name in Constants.TEAM_ABBREVIATION_DICT:
            team_abbr: str = Constants.TEAM_ABBREVIATION_DICT.get(search_name, "")
            return await self._extract_franchise_stats_from_html_table(page=page, franchise_name=search_name,
                                                                       team_abbr=team_abbr)

        return await self._extract_stats_from_html_table(page=page, player_name=search_name)

    async def _extract_franchise_stats_from_html_table(self, page: Page, franchise_name: str, team_abbr: str) -> \
            list[tuple]:

        table_locator: Locator = page.locator(f"table#{team_abbr}")

        per_season_stats_list: list[tuple] = await self._get_per_season_stats_list(
            table_locator=table_locator,
            search_name=franchise_name,
        )
        self._logger.info(f"Extracted {len(per_season_stats_list):,} season of data for {franchise_name}")
        self._logger.info("=" * 100)

        return per_season_stats_list

    async def _extract_stats_from_html_table(self, page: Page, player_name: str) -> \
            list[tuple]:

        html_table_name_str: str = self._player_stats_table_mapping_dict.get(self._stats_table_key, "")[0]

        if html_table_name_str == "":
            self._logger.error("No value passed for html_table_name_str")
            raise Exception("No value passed for html_table_name_str")

        table_locator: Locator = page.locator(html_table_name_str)

        per_season_stats_list: list[tuple] = await self._get_per_season_stats_list(
            table_locator=table_locator,
            search_name=player_name,
        )
        self._logger.info(f"Extracted {len(per_season_stats_list):,} season of data for {player_name}")
        self._logger.info("=" * 100)

        return per_season_stats_list

    async def _get_per_season_stats_list(self, table_locator: Locator, search_name: str) -> list[tuple]:
        await table_locator.wait_for(timeout=1_000)

        rows: list[Locator] = await table_locator.locator("tbody tr").all()

        per_season_stats_list: list[tuple] = []
        for row in rows:
            # Check for spacer/partial rows before processing
            row_class = await row.get_attribute("class") or ""
            if "spacer" in row_class or "partial_table" in row_class:
                continue

            # Get all cell elements (Season is <th>, rest are <td>)
            cell_locators: list[Locator] = await row.locator("th, td").all()

            if not cell_locators:
                continue

            # Extract text and data-stat attribute simultaneously from each cell
            stat_map: dict[str, str] = {}
            for cell in cell_locators:
                stat_name = await cell.get_attribute("data-stat")

                cell_inner_text = await cell.inner_text()

                if stat_name:
                    stat_map[stat_name] = cell_inner_text

            # Skip "Did Not Play" or summary rows that lack essential stats
            if len(stat_map) < 4 or "year_id" not in stat_map:
                self._logger.info(f"Skipping non-stat row for {search_name}")
                continue

            # for key, value in stat_map.items():
            #     self._logger.info(f"key = {key} -> value = {value}")

            # Pass the map to your sanitizers
            if self._stats_table_key == "reg-season-qsiB8VY":
                per_season_stats_list.append(self._data_cleanser.sanitize_stats_row_by_stat(stat_map=stat_map))
            elif self._stats_table_key == "reg-season-adv-uBMv04w":
                per_season_stats_list.append(self._data_cleanser.sanitize_advanced_stats_row_by_stat(stat_map=stat_map))
            elif self._stats_table_key == "playoffs-vsy03Dw":
                per_season_stats_list.append(self._data_cleanser.sanitize_playoff_series_row(stat_map=stat_map))
            # elif self._stats_table_key == "franchise-roBWT3o":
            #     per_season_stats_list.append(self._data_cleanser.sanitize_franchise_season_row(stat_map=stat_map))

        self._logger.info("=" * 100)
        # self._logger.info(f"per_season_stats_list count = {len(per_season_stats_list)}")

        return per_season_stats_list

    async def _build_stat_map(self, row: Locator) -> dict[str, str]:
        """Build a {data-stat: inner_text} dict for a table row."""
        cells: list[Locator] = await row.locator("th, td").all()
        stat_map: dict[str, str] = {}
        for cell in cells:
            data_stat: str | None = await cell.get_attribute("data-stat")
            if data_stat:
                cell_inner_text = await cell.inner_text()

                stat_map[data_stat] = cell_inner_text

        return stat_map

    async def _navigate_to_specified_page(self, page: Page, search_name: str) -> None:

        self._logger.info(f"Locating: {search_name}")
        await page.locator("input[name='search']").fill(search_name)
        await asyncio.sleep(1)

        if search_name in Constants.TEAM_ABBREVIATION_DICT:
            suggestion_locator: Locator = page.locator(".ac-dataset-bbr__teams .ac-suggestion").first
            await self._click_on_selected_suggestion(suggestion_locator=suggestion_locator, search_name=search_name)
        else:
            suggestion_locator: Locator = page.locator(".ac-dataset-bbr__players .ac-suggestion").first
            await self._click_on_selected_suggestion(suggestion_locator=suggestion_locator, search_name=search_name)

    async def _click_on_selected_suggestion(self, suggestion_locator: Locator, search_name: str) -> None:
        await suggestion_locator.wait_for(state="visible", )
        await asyncio.sleep(1)
        await suggestion_locator.click()
        self._logger.info(f"Navigating to {search_name}'s stats page")

    async def _navigate_to_franchise_page(self, page: Page, franchise_name: str) -> None:

        self._logger.info(f"Locating: {franchise_name}")
        await page.locator("input[name='search']").fill(franchise_name)
        await asyncio.sleep(1)
        suggestion_locator: Locator = page.locator(".ac-dataset-bbr__players .ac-suggestion").first
        await suggestion_locator.wait_for(state="visible", )
        await asyncio.sleep(1)
        await suggestion_locator.click()
        self._logger.info(f"Navigating to {franchise_name}'s stats page")

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
                    await asyncio.sleep(1)

                self._logger.info(f"Total players gathered: {len(all_nba_players_tuple_list):,}")

            self._logger.info("Browser closed successfully")

        return all_nba_players_tuple_list

    async def _navigate_to_players_page(self, page: Page, first_letter_of_last_name_str: str) -> None:
        await page.get_by_role(role="link", name="Players", exact=False).first.click()
        self._logger.info("Players Link Clicked")
        await asyncio.sleep(1)
        await page.locator("#div_alphabet").get_by_role(role="link", name=first_letter_of_last_name_str.upper(),
                                                        exact=True).click()
        await asyncio.sleep(1)
        self._logger.info(
            f"Clicked on Players with last names starting with: '{first_letter_of_last_name_str.upper()}'")

    async def _extract_players_data(self, page: Page) -> list[tuple]:

        table_locator: Locator = page.locator("table#players")

        await table_locator.wait_for()

        table_rows_list: list[Locator] = await table_locator.locator("tbody tr:not(.thead)").all()

        players_list: list[tuple] = []
        for row in table_rows_list:
            cells: list[str] = await row.locator("th, td").all_inner_texts()
            cells[0] = cells[0].replace("*", "")
            sanitized_player_tuple: tuple = self._data_cleanser.sanitize_player_row(cells=cells)
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

    async def get_immaculate_grid_list_data(self, index_str: str) -> list[tuple]:

        async with async_playwright() as playwright_obj:
            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page = await browser.new_page()
                self._logger.info(f"Navigating to {self._immaculate_grid_url + index_str}")
                await page.goto(url=self._immaculate_grid_url + index_str, wait_until="domcontentloaded",
                                timeout=60_000)
                self._logger.info(f"Successfully navigated to {self._immaculate_grid_url + index_str}")
                self._logger.info("=" * 100)

                result_list: list[tuple] = []
                column_text_list: list[str] = await self._get_column_text_list(page=page)
                row_text_list = await self._get_row_text_list(page=page)

                for row_index in range(0, 3):
                    for column_index in range(0, len(row_text_list)):
                        row_value_str: str = row_text_list[row_index]
                        column_value_str: str = column_text_list[column_index]

                        tuple_to_add: tuple = tuple([column_value_str, row_value_str])
                        result_list.append(tuple_to_add)

                return result_list

    async def _get_row_text_list(self, page: Page) -> list[str]:

        # self._logger.info("Retrieving row data")

        row_text_list: list[str] = []

        for row_index in range(3, 6):
            tooltip_locator = page.locator(f'[data-testid="ig-tooltip-{row_index}"]')
            image_locator: Locator = tooltip_locator.locator("img").first
            img_count: int = int(await image_locator.count())

            if img_count > 0:
                grid_row_image_text: str = await image_locator.get_attribute("alt")
                row_text_list.append(grid_row_image_text)
            else:
                raw_text = await self._get_text_from_grid_category(tooltip_locator=tooltip_locator)

                row_text_list.append(raw_text)

        return row_text_list

    async def _get_column_text_list(self, page: Page) -> list[str]:

        # self._logger.info("Retrieving column data")

        column_text_list: list[str] = []

        for column_num in range(3):

            if column_num == 0:
                await self._is_cancel_button_present(page=page)

            tooltip_locator = page.locator(f'[data-testid="ig-tooltip-{column_num}"]')
            image_locator: Locator = tooltip_locator.locator("img").first
            img_count: int = int(await image_locator.count())

            if img_count > 0:

                grid_column_image_text: str = await image_locator.get_attribute("alt")
                column_text_list.append(grid_column_image_text)

            else:
                raw_text = await self._get_text_from_grid_category(tooltip_locator=tooltip_locator)

                column_text_list.append(raw_text)

        return column_text_list

    async def _get_text_from_grid_category(self, tooltip_locator: Locator):

        text_container = tooltip_locator.locator(".font-display, .cursor-pointer").first
        raw_text_str: str = await text_container.text_content()

        return raw_text_str

    async def _is_cancel_button_present(self, page: Page) -> None:
        close_button: Locator = page.locator("#dismiss-instruction-modal-button")

        if await close_button.is_visible():
            await close_button.click()
            # self._logger.info("Navigating away from instruction modal")
            # self._logger.info("=" * 100)

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
