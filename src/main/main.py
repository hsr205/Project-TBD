import asyncio
from logging import Logger

from src.config.config import Settings
from src.database.data_loader import DataLoader
from src.logger.logger import AppLogger
from src.utils.constants import Constants


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))
    settings: Settings = Settings()

    data_loader: DataLoader = DataLoader(settings)

    try:

        await data_loader.load_data_into_table(
            insert_query_str=Constants.Queries.INSERT_INTO_PLAYER_REGULAR_SEASON_ADVANCED_STATS_TABLE_STR)

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
