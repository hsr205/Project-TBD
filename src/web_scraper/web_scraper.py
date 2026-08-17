import asyncio
import re
from logging import Logger

from playwright.async_api import async_playwright, Page, Locator
from tqdm import tqdm

from src.config.config import Settings
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.data_cleanser import DataCleanser


class WebScraper:

    def __init__(self, settings: Settings) -> None:
        self._base_url: str = settings.base_url
        self._draft_url: str = settings.draft_url
        self._stats_table_key: str = settings.stats_table_key
        self._data_cleanser: DataCleanser = DataCleanser()

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

    async def scrape_player_birth_country_data(self, page: Page, player_id: int, player_name_str: str) -> list[tuple]:

        all_players_country_data_list: list[tuple] = []

        await self._navigate_to_specified_page(page=page, search_name=player_name_str)

        await asyncio.sleep(1)

        player_birth_data_list: list[tuple] = await self._get_player_birth_data_from_player_page(page,
                                                                                                 player_id=player_id)

        all_players_country_data_list.extend(player_birth_data_list)

        return all_players_country_data_list

    async def _get_player_birth_data_from_player_page(self, page: Page, player_id: int) -> list[
        tuple]:

        country_or_us_state_name_str = await page.locator(
            "div#meta p:has(strong:has-text('Born')) a[href*='birthplaces']").inner_text()

        if country_or_us_state_name_str in Constants.US_STATES_LIST:
            country_or_us_state_name_str = 'United States'

        player_id_birth_country_tuple: tuple = tuple([player_id, country_or_us_state_name_str])

        result_list: list[tuple] = [player_id_birth_country_tuple]

        return result_list

    async def scrape_draft_pick_position(self, page: Page) -> list[tuple]:
        all_players_list: list[tuple] = await self._get_player_draft_data_list(page=page)
        await asyncio.sleep(1)

        return all_players_list

    async def _get_player_draft_data_list(self, page: Page) -> list[tuple]:

        all_players_list: list[tuple] = []
        await page.wait_for_selector("table#first_overall")
        year_links_locator: Locator = page.locator("table#first_overall tbody tr th[data-stat='draft'] a")
        total_year_links_int: int = int(await year_links_locator.count())

        for index in tqdm(range(1, total_year_links_int), desc="Scrapping Data From All NBA Drafts"):
            # Re-evaluate selector per iteration to prevent stale element handles after go_back()
            current_link = page.locator("table#first_overall tbody tr th[data-stat='draft'] a").nth(index)

            await current_link.inner_text()

            # Click the link and wait for navigation
            await current_link.click()
            await page.wait_for_load_state("domcontentloaded")

            draft_year_list: list[tuple] = await self._get_draft_data_player_list(page)

            all_players_list.extend(draft_year_list)

            await page.go_back()
            await page.wait_for_selector("table#first_overall")

        return all_players_list

    async def _get_draft_data_player_list(self, page: Page) -> list[tuple]:
        await page.wait_for_selector("table#stats")

        rows = await page.locator("table#stats tbody tr").all()

        current_round_int: int = 1
        result_list: list[tuple] = []

        for row in rows:
            row_class = await row.get_attribute("class") or ""

            if "over_header" in row_class:
                header_elem = row.locator('[data-stat="header_draft"]')
                header_element_count_int: int = await header_elem.count()
                if header_element_count_int > 0:
                    header_text = str(await header_elem.inner_text()).strip()
                    match = re.search(r"Round\s*(\d+)", header_text, re.IGNORECASE)
                    if match:
                        current_round_int = int(match.group(1))
                continue

                # Skip repeating headers
            if "thead" in row_class:
                continue

                # Extract player name
            player_elem = row.locator('[data-stat="player"]')
            player_element_count_int: int = await player_elem.count()
            if player_element_count_int > 0:
                player_name_str: str = str(await player_elem.inner_text()).strip()
                if player_name_str:
                    result_list.append((player_name_str, current_round_int))

        return result_list

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

    async def navigate_to_draft_page_url(self, page: Page) -> None:
        self._logger.info(f"Navigating to {self._draft_url}")
        await page.goto(url=self._draft_url)

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
