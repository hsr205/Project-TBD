from logging import Logger

from src.config.config import Settings
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger
from src.web_scraper.web_scraper import WebScraper


class ImmaculateGrid:

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._web_scraper: WebScraper = WebScraper(settings=self._settings)
        self._database_client: DatabaseClient = DatabaseClient(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def get_immaculate_grid_answer_matrix(self) -> None:
        self._database_client.get_immaculate_grid_query_results()
        immaculate_grid_list_data: list[tuple] = await self._web_scraper.get_immaculate_grid_list_data()

        for element in immaculate_grid_list_data:
            self._logger.info(f"element = {element}")
