from logging import Logger

import numpy as np
from playwright.async_api import async_playwright, Page, Locator

from src.config.config import Settings
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger
from src.utils.constants import Constants
from src.web_scraper.web_scraper import WebScraper

# TODO: In the event a player has already been selected and placed in the grid the player cannot be selected twice.
#       An additional SQL query to the local database is required to find a player that has not been selected.
class ImmaculateGrid:

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._immaculate_grid_url: str = settings.immaculate_grid_url
        self._web_scraper: WebScraper = WebScraper(settings=self._settings)
        self._database_client: DatabaseClient = DatabaseClient(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    async def _insert_players_into_immaculate_grid(self, page: Page, immaculate_grid_answer_matrix: np.ndarray) -> None:

        self._logger.info("Inserting players into immaculate grid:")

        for row_int in range(len(immaculate_grid_answer_matrix)):
            for column_int in range(len(immaculate_grid_answer_matrix[row_int])):
                # self._logger.info(f"player_name -> {immaculate_grid_answer_matrix[row_int][column_int]}")
                player_name_str: str = immaculate_grid_answer_matrix[row_int][column_int]
                await self._fill_immaculate_grid(page=page, row_int=row_int, column_int=column_int,
                                                 player_name_str=player_name_str)

        await self._display_immaculate_grid_rarity_outcome(page=page)

    async def _display_immaculate_grid_rarity_outcome(self, page: Page) -> None:

        received_rarity_score: float = await self._get_specified_rarity_score(page=page, text_header_str="Rarity Score")
        average_rarity_score: float = await self._get_specified_rarity_score(page=page, text_header_str="Average Score")

        self._logger.info(f"Successfully completed immaculate grid with a rarity score of: {received_rarity_score}")
        self._logger.info(f"The average rarity score was: {average_rarity_score}")

        self._logger.info("=" * 100)

    async def _get_specified_rarity_score(self, page: Page, text_header_str: str) -> float:
        metric_locator: Locator = page.locator(f"h3:has-text('{text_header_str}') ~ div .countup-wrap span")

        await metric_locator.wait_for(state="visible")
        metric_text: str = await metric_locator.inner_text()
        metric_score = float(metric_text.strip())

        return metric_score

    async def _fill_immaculate_grid(self, page: Page, row_int: int, column_int: int, player_name_str: str) -> None:
        # 1. Click the grid cell button using data-testid

        cell_button_locator: Locator = page.locator(f'[data-testid="ig-grid-{row_int + 1}-{column_int + 1}"] button')
        await cell_button_locator.click()

        # 2. Type into the search input box that appears in the overlay/modal
        search_input_locator: Locator = page.locator('input[type="search"], input[type="text"]')
        await search_input_locator.wait_for(state="visible")
        await search_input_locator.fill(value=player_name_str)

        # 3. Locate the first result's "Select" button inside the combobox options list
        select_button_locator: Locator = page.locator(
            'ul[id^="headlessui-combobox-options"] li[role="option"]') \
            .first \
            .locator('div:has-text("Select")')

        # Wait for the option to appear and click "Select"
        await select_button_locator.wait_for(state="visible")
        await select_button_locator.click()

    async def _get_immaculate_grid_answer_matrix(self, immaculate_grid_list_data) -> np.ndarray:

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

            element_1_str: str = initial_category_str if initial_category_str else sql_condition_str_1
            element_2_str: str = secondary_category_str if secondary_category_str else sql_condition_str_2

            query_elements_tuple: tuple = tuple([element_1_str, element_2_str])

            column_names_list, query_result_list = self._database_client.get_immaculate_grid_query_results(
                query_elements_tuple=query_elements_tuple)

            result_player_name_str: str = query_result_list[0][0]
            player_result_list.append(result_player_name_str)

        result_matrix: np.ndarray = np.array(player_result_list).reshape(3, 3)

        return result_matrix

    async def complete_immaculate_grid(self, index_str: str) -> None:

        async with async_playwright() as playwright_obj:
            async with await playwright_obj.chromium.launch(headless=False) as browser:
                page = await browser.new_page()
                self._logger.info(f"Navigating to {self._immaculate_grid_url + index_str}")
                await page.goto(url=self._immaculate_grid_url + index_str, wait_until="domcontentloaded",
                                timeout=60_000)
                self._logger.info(f"Successfully navigated to {self._immaculate_grid_url + index_str}")
                self._logger.info("=" * 100)

                immaculate_grid_list_data: list[tuple] = []
                column_text_list: list[str] = await self._get_column_text_list(page=page)
                row_text_list = await self._get_row_text_list(page=page)

                for row_index in range(0, 3):
                    for column_index in range(0, len(row_text_list)):
                        row_value_str: str = row_text_list[row_index]

                        column_value_str: str = column_text_list[column_index]

                        tuple_to_add: tuple = tuple([column_value_str, row_value_str])
                        immaculate_grid_list_data.append(tuple_to_add)

                immaculate_grid_answer_matrix: np.ndarray = await self._get_immaculate_grid_answer_matrix(
                    immaculate_grid_list_data=immaculate_grid_list_data)

                self._logger.info(f"immaculate_grid_answer_matrix = {immaculate_grid_answer_matrix}")
                self._logger.info("=" * 100)

                await self._insert_players_into_immaculate_grid(page=page,
                                                                immaculate_grid_answer_matrix=immaculate_grid_answer_matrix)

    async def _get_row_text_list(self, page: Page) -> list[str]:

        row_text_list: list[str] = []

        for row_index in range(3, 6):
            tooltip_locator = page.locator(f'[data-testid="ig-tooltip-{row_index}"]')
            image_locator: Locator = tooltip_locator.locator("img").first
            img_count: int = int(await image_locator.count())

            if img_count > 0:
                grid_row_image_text: str = await image_locator.get_attribute("alt")
                row_text_list.append(grid_row_image_text)
            else:
                raw_text = await self._get_text_from_grid_category(tooltip_locator=tooltip_locator)

                row_text_list.append(raw_text)

        return row_text_list

    async def _get_column_text_list(self, page: Page) -> list[str]:

        # self._logger.info("Retrieving column data")

        column_text_list: list[str] = []

        for column_num in range(3):

            if column_num == 0:
                await self._is_cancel_button_present(page=page)

            tooltip_locator = page.locator(f'[data-testid="ig-tooltip-{column_num}"]')
            image_locator: Locator = tooltip_locator.locator("img").first
            img_count: int = int(await image_locator.count())

            if img_count > 0:

                grid_column_image_text: str = await image_locator.get_attribute("alt")
                column_text_list.append(grid_column_image_text)

            else:
                raw_text = await self._get_text_from_grid_category(tooltip_locator=tooltip_locator)

                column_text_list.append(raw_text)

        return column_text_list

    async def _get_text_from_grid_category(self, tooltip_locator: Locator):

        text_container = tooltip_locator.locator(".font-display, .cursor-pointer").first
        raw_text_str: str = await text_container.text_content()

        return raw_text_str

    async def _is_cancel_button_present(self, page: Page) -> None:
        close_button: Locator = page.locator("#dismiss-instruction-modal-button")

        if await close_button.is_visible():
            await close_button.click()
            # self._logger.info("Navigating away from instruction modal")
            # self._logger.info("=" * 100)

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
