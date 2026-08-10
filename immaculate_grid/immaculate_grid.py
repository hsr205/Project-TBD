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

            self._logger.info(f"({element_one_str}, {element_two_str})")

            initial_category_str: str = Constants.TEAM_ABBREVIATION_DICT.get(element_one_str, '')
            secondary_category_str: str = Constants.TEAM_ABBREVIATION_DICT.get(element_two_str, '')

            sql_condition_str_1: str = self._get_sql_condition_str(category_str=initial_category_str,
                                                                   element_str=element_one_str)

            sql_condition_str_2: str = self._get_sql_condition_str(category_str=secondary_category_str,
                                                                   element_str=element_two_str)

            query_elements_list: list[str] = []

            if sql_condition_str_1 == '' and sql_condition_str_2 == '':
                query_elements_list.append(initial_category_str)
                query_elements_list.append(secondary_category_str)

            else:

                if sql_condition_str_1 == '':
                    query_elements_list.append(sql_condition_str_2)
                    query_elements_list.append(initial_category_str)

                if sql_condition_str_2 == '':
                    query_elements_list.append(sql_condition_str_1)
                    query_elements_list.append(secondary_category_str)

                if sql_condition_str_1 != '' and sql_condition_str_2 != '':
                    query_elements_list.append(sql_condition_str_1)
                    query_elements_list.append(sql_condition_str_2)

            self._logger.info(f"query_elements_list = {query_elements_list}")
            self._logger.info("=" * 100)

            if initial_category_str == 'N/A' or secondary_category_str == 'N/A':
                continue

            # if sql_condition_str_1 == '':
            #     team_abbreviation_list[0] = sql_condition_str_1
            #     team_abbreviation_list[1] =

            # column_names_list, query_result_list = self._database_client.get_immaculate_grid_query_results(
            #     team_abbreviation_tuple=team_abbreviation_tuple)
            #
            # result_player_name_str: str = query_result_list[0][0]
            # player_result_list.append(result_player_name_str)

        exit()

        result_matrix: np.ndarray = np.array(player_result_list).reshape(3, 3)

        print(result_matrix)

    def _get_sql_condition_str(self, category_str: str, element_str: str) -> str:

        result_sql_condition_str: str = ""

        if category_str == '':

            split_list: list[str] = element_str.split()
            test_list: list = [x.replace('+', '') for x in split_list]

            quantity_value: float = 0.0

            for element in test_list:

                if element.isdigit():
                    quantity_value = float(element)

                sql_condition_str: str = Constants.ImmaculateGridCategories.IMMACULATE_GRID_CATEGORY_SQL_MAPPING_DICT.get(
                    element, '')

                if quantity_value > 0.0 and sql_condition_str != '':
                    result_sql_condition_str += sql_condition_str + ' ' + str(quantity_value)

        return result_sql_condition_str
