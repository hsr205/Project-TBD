from src.logger.logger import AppLogger


class WebScraper:

    def __init__(self) -> None:
        self._logger = AppLogger.get_logger(self.__class__.__name__)
