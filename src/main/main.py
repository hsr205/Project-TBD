import asyncio
from logging import Logger

from src.logger.logger import AppLogger
from src.web_scraper.web_scraper import WebScraper


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))

    web_scraper:WebScraper = WebScraper()

    try:

        await web_scraper.playwright_test_method()

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
