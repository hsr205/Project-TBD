import asyncio
from logging import Logger

from immaculate_grid.immaculate_grid import ImmaculateGrid
from src.config.config import Settings
from src.logger.logger import AppLogger


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))
    settings: Settings = Settings()

    immaculate_grid: ImmaculateGrid = ImmaculateGrid(settings=settings)

    try:

        # for index in range(1, 1_115):
        for index in range(99, 1_115):
            index_str:str = str(index)
            await immaculate_grid.get_immaculate_grid_answer_matrix(index_str=index_str)

        # logger.info("Executing application")
        # logger.info("=" * 100)
        #
        # umap_rending: UMAPRendering = UMAPRendering(settings=settings)
        #
        # umap_rending.display_umap_rending()
        #
        # logger.info("Successfully completed application execution")
        # logger.info("=" * 100)

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
