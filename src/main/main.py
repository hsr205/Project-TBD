import asyncio
from logging import Logger

from src.config.config import Settings
from src.database.data_loader import DataLoader
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger
from src.utils.constants import Constants


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))
    settings: Settings = Settings()

    data_loader: DataLoader = DataLoader(settings)

    database_client: DatabaseClient = DatabaseClient(settings=settings)

    try:

        player_dict: dict[int, str] = database_client.get_player_dict_from_player_table()

        logger.info("Executing application")
        logger.info("=" * 100)
        await data_loader.load_data_into_table(
            insert_query_str=Constants.Queries.INSERT_INTO_PLAYER_PLAYOFF_SERIES_STATS_TABLE_STR,
            entity_dict=player_dict)

        logger.info("Successfully completed application execution")
        logger.info("=" * 100)

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
