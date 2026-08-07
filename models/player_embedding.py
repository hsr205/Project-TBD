from logging import Logger

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config.config import Settings
from src.database.database_client import DatabaseClient
from src.logger.logger import AppLogger


class PlayerEmbedding:

    def __init__(self, settings: Settings) -> None:
        self._player_ids_list: list[int] = []
        self._player_names_list: list[str] = []
        self._database_client: DatabaseClient = DatabaseClient(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    def get_player_ids_list(self) -> list[int]:
        return self._player_ids_list

    def get_names_list(self) -> list[str]:
        return self._player_names_list

    def _parse_height_to_inches(self, height_str: str):
        """Converts a height string formatted as 'Feet-Inches' (e.g., '6-11') to total inches."""
        feet, inches = map(int, str(height_str).split('-'))
        return feet * 12 + inches

    def get_similarity_matrix(self) -> np.ndarray:

        player_embeddings_array: np.ndarray = self.get_all_nba_player_embeddings_array()

        # Calculates the exact geometric length (magnitude) of every single player's statistical arrow in multi-dimensional space
        norms: np.ndarray = np.linalg.norm(player_embeddings_array, axis=1, keepdims=True)

        # Avoid division by zero for zero-vectors
        safe_norms: np.ndarray = np.where(norms == 0, 1e-10, norms)

        normalized_embeddings: np.ndarray = player_embeddings_array / safe_norms

        similarity_matrix_array: np.ndarray = np.dot(normalized_embeddings, normalized_embeddings.T)

        self._logger.info(f"Final Similarity Matrix Shape (N, D): {similarity_matrix_array.shape}")

        return similarity_matrix_array

    def get_all_nba_player_embeddings_array(self) -> np.ndarray:

        cleaned_dataframe: pd.DataFrame = self._get_cleaned_dataframe()

        # 4. Convert to NumPy Array (NxD Matrix)
        array_prior_to_normalization: np.ndarray = cleaned_dataframe.to_numpy()

        # 5. Standardize Features (Zero mean, Unit variance)
        scaler: StandardScaler = StandardScaler()
        normalized_array: np.ndarray = scaler.fit_transform(array_prior_to_normalization)

        self._logger.info(f"Final Matrix Shape (N, D): {normalized_array.shape}")

        return normalized_array

    def _get_cleaned_dataframe(self) -> pd.DataFrame:

        # column_names_list, all_regular_season_career_averages_list = self._database_client.get_all_regular_season_career_averages_list()
        column_names_list, all_regular_season_career_averages_list = self._database_client.get_all_regular_season_advanced_career_averages_list()

        dataframe: pd.DataFrame = pd.DataFrame(data=all_regular_season_career_averages_list, columns=column_names_list)

        self._player_ids_list = dataframe['player_id'].to_list()
        self._player_names_list = dataframe['player_name'].to_list()

        features_dataframe: pd.DataFrame = dataframe.drop(columns=['player_id', 'player_name'])

        transformed_dataframe: pd.DataFrame = self._get_transformed_dataframe(features_dataframe=features_dataframe)

        self._convert_all_numerical_columns_to_float_values(transformed_dataframe=transformed_dataframe)

        # encoded_dataframe: pd.DataFrame = self._get_one_hot_encoded_dataframe(
        #     transformed_dataframe=transformed_dataframe)
        #
        # # Combine encoded positions back with numerical features (dropping original 'position')
        # result_dataframe: pd.DataFrame = pd.concat([encoded_dataframe, transformed_dataframe.drop(columns=['position'])],
        #                                            axis=1)
        return transformed_dataframe

    def _get_transformed_dataframe(self, features_dataframe: pd.DataFrame) -> pd.DataFrame:

        nan_cols = features_dataframe.columns[features_dataframe.isna().any()].tolist()
        for col in nan_cols:
            features_dataframe[f'{col}_was_missing'] = features_dataframe[col].isna().astype(float)

        result_dataframe: pd.DataFrame = features_dataframe.fillna(0.0)

        return result_dataframe

    def _get_one_hot_encoded_dataframe(self, transformed_dataframe: pd.DataFrame) -> pd.DataFrame:

        # Handle position categories (e.g., 'C', 'PF', 'SF', 'SG', 'PG')
        one_hot_encoder: OneHotEncoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_position = one_hot_encoder.fit_transform(transformed_dataframe[['position']])

        # Build DataFrame of encoded position columns
        position_columns_list: list[str] = [f"pos_{category}" for category in one_hot_encoder.categories_[0]]
        result_dataframe: pd.DataFrame = pd.DataFrame(encoded_position, columns=position_columns_list)

        return result_dataframe

    def _lookup_individual_player_embeddings(self, normalized_array, target_id_num: int) -> None:

        player_matrix_map: dict[tuple[int, str], any] = {
            (pid, name): row
            for pid, name, row in zip(self._player_ids_list, self._player_names_list, normalized_array)
        }

        for (pid, name), features in player_matrix_map.items():
            if pid == target_id_num:
                print(f"ID: {pid} | Name: {name}")
                print("Scaled Features:\n", features)
                break

        self._logger.info("=" * 100)

    def _convert_all_numerical_columns_to_float_values(self, transformed_dataframe: pd.DataFrame) -> None:
        for col in transformed_dataframe.columns:
            if col != 'position':
                transformed_dataframe[col] = transformed_dataframe[col].astype(float)
