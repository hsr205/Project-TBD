import asyncio
from logging import Logger

from src.config.config import Settings
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger
from src.web_scraper.web_scraper import WebScraper


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))
    settings: Settings = Settings()
    web_scraper: WebScraper = WebScraper(settings=settings)
    database_client: DatabaseClient = DatabaseClient(settings=settings)

    try:

        nba_franchise_list:list[tuple] = await web_scraper.get_nba_franchise_list()
        # database_client.create_franchise_table()
        # database_client.drop_franchise_table()
        database_client.insert_rows_into_franchises_table(nba_franchise_list=nba_franchise_list)

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
