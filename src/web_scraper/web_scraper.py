import time
from logging import Logger

from playwright.async_api import async_playwright, Page, Locator

from src.config.config import Settings
from src.logger.logger import AppLogger


class WebScraper:

    def __init__(self, settings: Settings) -> None:
        self._base_url: str = settings.base_url
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def execute_web_scrapper(self) -> None:
        num_seconds_to_pause: int = 5

        async with async_playwright() as playwright_obj:
            self._logger.info("Launching Chromium browser")
            self._logger.info("=" * 100)

            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page: Page = await browser.new_page()

                await self._navigate_to_base_url(page=page)

                await self._navigate_to_teams_page(page=page)

                table_locator: Locator = await self._locate_active_franchise_table(page=page)

                await self._extract_data_from_active_franchise_table(page=page, table_locator=table_locator)

                self._logger.info("Pause starts now...")
                time.sleep(num_seconds_to_pause)
                self._logger.info(f"{num_seconds_to_pause} seconds have passed!")

            self._logger.info("Browser closed successfully")

    async def _navigate_to_base_url(self, page: Page) -> None:
        self._logger.info(f"Navigating to {self._base_url}")
        await page.goto(url=self._base_url)

    async def _navigate_to_teams_page(self, page: Page) -> None:
        await page.get_by_role(role="link", name="Teams", exact=False).first.click()
        self._logger.info("Teams Link Clicked")

    async def _locate_active_franchise_table(self, page: Page) -> Locator:
        await page.get_by_role(role="table", name="Active Franchises Table").get_by_label(
            text="Franchise").first.click()
        self._logger.info("Located Active Franchises Table")
        table_locator: Locator = page.get_by_role(role="table", name="Active Franchises Table")
        await table_locator.locator("tbody tr.full_table").first.wait_for()
        return table_locator

    async def _extract_data_from_active_franchise_table(self, page: Page, table_locator: Locator) -> None:
        self._logger.info("Extracting Table Headers")
        headers: list[str] = await table_locator.locator("thead tr th").all_inner_texts()

        locator_list_results: list[Locator] = await table_locator.locator("tbody tr.full_table").all()

        data_scrapped_list: list[list[str]] = [headers]
        for table_row in locator_list_results:
            table_cells_list: list[str] = await table_row.locator("th, td").all_inner_texts()
            data_scrapped_list.append(table_cells_list)

        self._logger.info(f"Scraped {len(data_scrapped_list)} rows")
        for table_row in data_scrapped_list:
            self._logger.info(table_row)

        self._logger.info("=" * 100)
