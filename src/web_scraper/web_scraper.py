import time
from logging import Logger

from playwright.async_api import async_playwright, Page

from src.config.config import Settings
from src.logger.logger import AppLogger


class WebScraper:

    def __init__(self) -> None:
        self._config: Settings = Settings()
        self._base_url: str = self._config.base_url
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def playwright_test_method(self) -> None:
        self._logger.info("Inside method: playwright_test_method()")

        num_seconds_to_pause: int = 5

        async with async_playwright() as playwright_obj:
            self._logger.info("Launching Chromium browser")

            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page: Page = await browser.new_page()

                self._logger.info(f"Navigating to {self._base_url}")
                await page.goto(url=self._base_url)

                # Wait for the page to be fully loaded before interacting
                await page.wait_for_load_state("networkidle")

                self._logger.info("Pause starts now...")
                time.sleep(num_seconds_to_pause)
                self._logger.info(f"{num_seconds_to_pause} seconds have passed!")

                # await page.screenshot(path="example-chromium.png")
                # self._logger.info("Screenshot saved to example-chromium.png")

            self._logger.info("Browser closed successfully")
