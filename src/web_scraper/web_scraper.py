import time
from logging import Logger

from playwright.async_api import async_playwright, Page, Locator

from src.config.config import Settings
from src.logger.logger import AppLogger


class WebScraper:

    def __init__(self, settings: Settings) -> None:
        self._base_url: str = settings.base_url
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def get_all_nba_players_list(self) -> list[tuple]:
        all_nba_players_tuple_list: list[tuple] = []

        async with async_playwright() as playwright_obj:
            self._logger.info("Launching Chromium browser")
            self._logger.info("=" * 100)

            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page: Page = await browser.new_page()

                alphabet_list: list[str] = self._get_alphabet_list()

                for letter in alphabet_list:
                    await self._navigate_to_base_url(page=page)
                    await self._navigate_to_players_page(page=page, first_letter_of_last_name_str=letter)

                    table_locator: Locator = page.locator("table#players")
                    all_nba_players_tuple_list.extend(await self._extract_players_data(table_locator=table_locator))
                    time.sleep(5)

                self._logger.info(f"Total players gathered: {len(all_nba_players_tuple_list):,}")

            self._logger.info("Browser closed successfully")

        return all_nba_players_tuple_list

    def _get_alphabet_list(self) -> list[str]:

        alphabet_list: list[str] = []

        for element in range(65, 91):
            ascii_character: str = chr(element)

            if element == 88:
                self._logger.info("Skipping X last names")
                continue

            alphabet_list.append(ascii_character)

        return alphabet_list

    async def _navigate_to_players_page(self, page: Page, first_letter_of_last_name_str: str) -> None:
        await page.get_by_role(role="link", name="Players", exact=False).first.click()
        self._logger.info("Players Link Clicked")
        time.sleep(3)
        await page.locator("#div_alphabet").get_by_role(role="link", name=first_letter_of_last_name_str.upper(),
                                                        exact=True).click()
        time.sleep(5)
        self._logger.info(f"Clicked on Players with last names starting with: '{first_letter_of_last_name_str.upper()}'")

    async def _extract_players_data(self, table_locator: Locator) -> list[tuple]:
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

    def to_str_or_none(self, value: str) -> str | None:
        """Convert a string to None if empty."""
        stripped = value.strip()
        return stripped if stripped else None

    async def get_nba_franchise_list(self) -> list[tuple]:
        nba_franchise_tuple_list: list[tuple] = []

        async with async_playwright() as playwright_obj:
            self._logger.info("Launching Chromium browser")
            self._logger.info("=" * 100)

            async with await playwright_obj.chromium.launch(headless=True) as browser:
                page: Page = await browser.new_page()

                await self._navigate_to_base_url(page=page)

                await self._navigate_to_teams_page(page=page)

                table_locator: Locator = await self._locate_active_franchise_table(page=page)

                nba_franchise_tuple_list = await self._extract_franchise_data_to_list(table_locator=table_locator)

            self._logger.info("Browser closed successfully")

        return nba_franchise_tuple_list

    async def _navigate_to_base_url(self, page: Page) -> None:
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
