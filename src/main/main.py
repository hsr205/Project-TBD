import asyncio
from logging import Logger

from src.logger.logger import AppLogger


async def main() -> int:
    logger: Logger = AppLogger().get_logger(class_name=str(__name__))

    try:

        logger.info(f"Hello from {__name__}")
        return 0

    except Exception as e:
        logger.exception(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    asyncio.run(main())
