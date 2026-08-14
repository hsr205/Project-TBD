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

        for index in range(0, 1_115):
            index_str: str = str(index)
            await immaculate_grid.get_immaculate_grid_answer_matrix(index_str=index_str)

        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
