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

    async def get_immaculate_grid_answer_matrix(self, index_str: str) -> None:
        immaculate_grid_list_data: list[tuple] = await self._web_scraper.get_immaculate_grid_list_data(
            index_str=index_str)

        player_result_list: list[str] = []

        for tuple_obj in immaculate_grid_list_data:
            element_one_str: str = tuple_obj[0]
            element_two_str: str = tuple_obj[1]

            initial_category_str: str = Constants.TEAM_ABBREVIATION_DICT.get(element_one_str, '')
            secondary_category_str: str = Constants.TEAM_ABBREVIATION_DICT.get(element_two_str, '')

            sql_condition_str_1: str = self._get_sql_condition_str(category_str=initial_category_str,
                                                                   element_str=element_one_str)

            sql_condition_str_2: str = self._get_sql_condition_str(category_str=secondary_category_str,
                                                                   element_str=element_two_str)

            elem_1: str = initial_category_str if initial_category_str else sql_condition_str_1
            elem_2: str = secondary_category_str if secondary_category_str else sql_condition_str_2

            query_elements_tuple: tuple = tuple([elem_1, elem_2])

            column_names_list, query_result_list = self._database_client.get_immaculate_grid_query_results(
                query_elements_tuple=query_elements_tuple)

            result_player_name_str: str = query_result_list[0][0]
            player_result_list.append(result_player_name_str)

        result_matrix: np.ndarray = np.array(player_result_list).reshape(3, 3)

        self._logger.info("Result Matrix:")

        self._logger.info("=" * 100)

        print(result_matrix)

        self._logger.info("=" * 100)

    def _get_sql_condition_str(self, category_str: str, element_str: str) -> str:

        if category_str:
            return ""

        clean_str = element_str.replace('\xa0', ' ').strip()
        mapping = Constants.ImmaculateGridCategories.IMMACULATE_GRID_CATEGORY_SQL_MAPPING_DICT

        is_career: bool = 'career' in clean_str.lower()

        for key, sql in mapping.items():

            if is_career and not key.endswith('career'):
                continue
            if not is_career and key.endswith('career'):
                continue

            if key in clean_str and sql:
                if sql.endswith('> '):
                    num = self._extract_number(clean_str)
                    return f"{sql}{num}" if num else ""
                return sql

        return ""

    def _extract_number(self, text: str) -> float:
        for word in text.split():
            cleaned = ''.join(char for char in word if char.isdigit() or char == '.')
            try:
                return float(cleaned)
            except ValueError:
                continue
        return 0.0
