from logging import Logger

import numpy as np

from src.config.config import Settings
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.web_scraper import WebScraper


class ImmaculateGrid:

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._web_scraper: WebScraper = WebScraper(settings=self._settings)
        self._database_client: DatabaseClient = DatabaseClient(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def get_immaculate_grid_answer_matrix(self) -> None:
        immaculate_grid_list_data: list[tuple] = await self._web_scraper.get_immaculate_grid_list_data()

        player_result_list: list[str] = []

        for tuple_obj in immaculate_grid_list_data:

            element_one_str: str = tuple_obj[0]
            element_two_str: str = tuple_obj[1]

            # self._logger.info(f"({element_one_str}, {element_two_str})")

            initial_category_str: str = Constants.TEAM_ABBREVIATION_DICT.get(element_one_str, '')
            secondary_category_str: str = Constants.TEAM_ABBREVIATION_DICT.get(element_two_str, '')

            if initial_category_str == '':
                self._logger.info(f"({element_one_str}, {element_two_str})")

                split_list:list[str] = element_one_str.split()
                test_list:list = [x.replace('+', '') for x in split_list]

                quantity_value: float = 0.0

                for element in test_list:

                    if element.isdigit():
                        quantity_value = float(element)

                    if quantity_value > 0.0:
                        self._logger.info(f"result = {Constants.ImmaculateGridCategories.IMMACULATE_GRID_CATEGORY_SQL_MAPPING_DICT.get(element, '')}{quantity_value}")

                self._logger.info("=" * 100)

            if secondary_category_str == '':
                self._logger.info("secondary_category_str == ''")
                self._logger.info(f"({element_one_str}, {element_two_str})")

                split_list:list[str] = element_two_str.split()
                test_list:list = [x.replace('+', '') for x in split_list]

                quantity_value: float = 0.0

                for element in test_list:

                    if element.isdigit():
                        quantity_value = float(element)

                for element in test_list:

                    if element.isdigit():
                        quantity_value = float(element)

                    if quantity_value > 0.0:
                        self._logger.info(
                            f"result = {Constants.ImmaculateGridCategories.IMMACULATE_GRID_CATEGORY_SQL_MAPPING_DICT.get(element, '')}{quantity_value}")

                self._logger.info("=" * 100)

            if initial_category_str == 'N/A' or secondary_category_str == 'N/A':
                continue

            # team_abbreviation_tuple: tuple = tuple([team_abbreviation_one_text, team_abbreviation_two_text])
            #
            # column_names_list, query_result_list = self._database_client.get_immaculate_grid_query_results(
            #     team_abbreviation_tuple=team_abbreviation_tuple)
            #
            # result_player_name_str: str = query_result_list[0][0]
            # player_result_list.append(result_player_name_str)

        exit()

        result_matrix: np.ndarray = np.array(player_result_list).reshape(3, 3)

        print(result_matrix)
