from dataclasses import dataclass
from logging import Logger

import numpy as np
import plotly.graph_objects as go
import umap

from models.player_embedding import PlayerEmbedding
from src.config.config import Settings
from src.logger.logger import AppLogger


@dataclass(frozen=True)
class VisualPlayerPoint:
    """Immutable data object representing a player's spatial visual point."""

    player_id: int
    player_name: str
    x_coordinate: float
    y_coordinate: float
    z_coordinate: float


class UMAPRendering:

    def __init__(self, settings: Settings) -> None:
        self._player_embedding: PlayerEmbedding = PlayerEmbedding(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    def display_umap_rending(self) -> None:
        visual_player_points_list: list[VisualPlayerPoint] = self._get_visual_player_points_list()

        x_coordinate: list[float] = [player_point.x_coordinate for player_point in visual_player_points_list]
        y_coordinate: list[float] = [player_point.y_coordinate for player_point in visual_player_points_list]
        z_coordinate: list[float] = [player_point.z_coordinate for player_point in visual_player_points_list]

        # Construct contextual hover HTML without archetype dependencies
        hover_templates_list: list[str] = [
            f"<b>{player_point.player_name}</b><br>"
            f"X: {player_point.x_coordinate:.2f} | Y: {player_point.y_coordinate:.2f} | Z: {player_point.z_coordinate:.2f}"
            for player_point in visual_player_points_list
        ]

        scatter_3d: go.Scatter3d = go.Scatter3d(
            x=x_coordinate,
            y=y_coordinate,
            z=z_coordinate,
            mode="markers+text",
            textposition="top center",
            hoverinfo="text",
            hovertext=hover_templates_list,
            marker=dict(
                size=7,
                color=z_coordinate,  # Color mapped continuously to Z-axis elevation
                colorscale="Viridis",
                colorbar=dict(title="UMAP Z-Dimension"),
                opacity=0.85,
                line=dict(width=0.5, color="white"),
            ),
        )

        layout: go.Layout = go.Layout(
            title=dict(text="NBA Player Similarity - Unsupervised 3D Vector Space", font=dict(size=20)),
            scene=dict(
                xaxis=dict(title="UMAP Dimension 1"),
                yaxis=dict(title="UMAP Dimension 2"),
                zaxis=dict(title="UMAP Dimension 3"),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                ),
            ),
            margin=dict(l=0, r=0, b=0, t=40),
        )

        figure: go.Figure = go.Figure(data=[scatter_3d], layout=layout)
        self._logger.info("Displaying UMAP Rendering")
        self._logger.info("=" * 100)
        figure.show()

    def _get_visual_player_points_list(self) -> list[VisualPlayerPoint]:
        self._logger.info("Generating 3D Coordinate Mapping for UMAP Generation")
        self._logger.info("=" * 100)

        coordinates_array: np.ndarray = self._get_reduced_dimensions_array()
        player_ids_list: list[int] = self._player_embedding.get_player_ids_list()
        player_names_list: list[str] = self._player_embedding.get_names_list()

        visual_player_point_list: list[VisualPlayerPoint] = []

        for index_num, player_name in enumerate(player_names_list):
            visual_player_point_obj: VisualPlayerPoint = VisualPlayerPoint(
                player_id=player_ids_list[index_num],
                player_name=player_names_list[index_num],
                x_coordinate=float(coordinates_array[index_num, 0]),
                y_coordinate=float(coordinates_array[index_num, 1]),
                z_coordinate=float(coordinates_array[index_num, 2]),
            )

            visual_player_point_list.append(visual_player_point_obj)

        return visual_player_point_list

    def _get_reduced_dimensions_array(self) -> np.ndarray:
        dimension_reducer: umap.UMAP = umap.UMAP(
            n_components=3,
            n_neighbors=5,
            min_dist=0.1,
            metric="cosine",
            random_state=42,
        )

        player_embeddings_array: np.ndarray = self._player_embedding.get_all_nba_player_embeddings_array()

        coordinate_array: np.ndarray = dimension_reducer.fit_transform(X=player_embeddings_array)

        self._logger.info(f"Reduced embeddings from {player_embeddings_array.shape} to {coordinate_array.shape}")

        return coordinate_array
