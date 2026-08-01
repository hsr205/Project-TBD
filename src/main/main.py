import asyncio
from logging import Logger

from models.umap_rendering import UMAPRendering
from src.config.config import Settings
from src.database.data_loader import DataLoader
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))
    settings: Settings = Settings()

    data_loader: DataLoader = DataLoader(settings)

    database_client: DatabaseClient = DatabaseClient(settings=settings)

    try:

        logger.info("Executing application")
        logger.info("=" * 100)

        umap_rending: UMAPRendering = UMAPRendering(settings=settings)

        umap_rending.display_umap_rendering_for_advanced_stats()

        logger.info("Successfully completed application execution")
        logger.info("=" * 100)

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
