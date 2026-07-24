from logging import Logger

from playwright.async_api import async_playwright

from src.config.config import Settings
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger
from src.web_scraper.web_scraper import WebScraper


class DataLoader:

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._web_scraper: WebScraper = WebScraper(settings=self._settings)
        self._database_client: DatabaseClient = DatabaseClient(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def load_data_into_table(self, insert_query_str: str) -> None:

        player_dict: dict[int, str] = self._database_client.get_player_dict_from_player_table()

        async with async_playwright() as playwright_obj:
            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page = await browser.new_page()
                await self._web_scraper.navigate_to_base_url(page=page)

                for player_id, player_name in player_dict.items():
                    try:
                        stats_list: list[tuple] = await self._web_scraper.scrape_player_stats(
                            page=page,
                            player_name=player_name,
                        )

                        if not stats_list:
                            self._logger.warning(f"No stats found for {player_name}, skipping")
                            continue

                        # Insert stats rows with the known player_id
                        await self._database_client.insert_rows_into_table(
                            player_name_str=player_name,
                            player_regular_season_stats_list=stats_list,
                            current_player_dict=player_dict,
                            insert_query_str=insert_query_str
                        )

                    except Exception as player_error:
                        self._logger.warning(f"Failed to process '{player_name}', skipping — reason: {player_error}")
                        await self._web_scraper.navigate_to_base_url(page=page)
                        continue
