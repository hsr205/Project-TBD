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


@dataclass(frozen=True)
class VisualPlayerPointAdvanced:
    """Immutable data object representing a player's metric coordinates."""

    player_id: int
    player_name: str
    per: float  # X-axis
    ws_per_48: float  # Y-axis
    vorp: float  # Z-axis


class UMAPRendering:

    def __init__(self, settings: Settings) -> None:
        self._player_embedding: PlayerEmbedding = PlayerEmbedding(settings=settings)
        self._logger: Logger = AppLogger.get_logger(self.__class__.__name__)

    def display_umap_rendering_for_advanced_stats(self) -> None:
        visual_points: list[VisualPlayerPointAdvanced] = self._get_visual_player_advanced_points_list()

        x_coordinate: list[float] = [p.per for p in visual_points]
        y_coordinate: list[float] = [p.ws_per_48 for p in visual_points]
        z_coordinate: list[float] = [p.vorp for p in visual_points]
        num_players: int = len(visual_points)

        # Baseline point attributes
        base_marker_sizes: list[float] = [5.0]
        base_opacity: list[float] = [0.75] * num_players

        # Hover tooltip formatting with clear metric labels
        hover_templates: list[str] = [
            (
                f"<b>{p.player_name}</b><br>"
                f"PER: {p.per:.1f}<br>"
                f"WS/48: {p.ws_per_48:.3f}<br>"
                f"VORP: {p.vorp:.1f}"
            )
            for p in visual_points
        ]

        # Primary 3D scatter trace
        main_scatter: go.Scatter3d = go.Scatter3d(
            x=x_coordinate,
            y=y_coordinate,
            z=z_coordinate,
            mode="markers",
            hoverinfo="text",
            hovertext=hover_templates,
            marker=dict(
                size=base_marker_sizes,
                color=z_coordinate,  # Color coded by VORP
                colorscale="Viridis",
                colorbar=dict(title="Career VORP"),
                opacity=0.75,
                line=dict(width=0.5, color="white"),
            ),
        )

        # Dropdown search configuration
        dropdown_buttons: list[dict] = []

        # Option 1: Reset View
        reset_button: dict = dict(
            label="-- Reset Search / Show All --",
            method="update",
            args=[
                {"marker.size": [base_marker_sizes], "marker.opacity": [base_opacity]},
                {"scene.annotations": []},
            ],
        )
        dropdown_buttons.append(reset_button)

        # Option 2: Search specific players
        for idx, target_point in enumerate(visual_points):
            custom_sizes: list[float] = [4.0] * num_players
            custom_opacities: list[float] = [0.25] * num_players

            custom_sizes[idx] = 16.0
            custom_opacities[idx] = 1.0

            annotation: dict = dict(
                x=target_point.per,
                y=target_point.ws_per_48,
                z=target_point.vorp,
                text=f"SELECTED: {target_point.player_name}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                arrowsize=1.5,
                ax=0,
                ay=-40,
                font=dict(color="black", size=12),
                bgcolor="yellow",
                bordercolor="red",
                borderwidth=2,
            )

            player_button: dict = dict(
                label=f"Find: {target_point.player_name}",
                method="update",
                args=[
                    {"marker.size": [custom_sizes], "marker.opacity": [custom_opacities]},
                    {"scene.annotations": [annotation]},
                ],
            )
            dropdown_buttons.append(player_button)

        update_menus: list[dict] = [
            dict(
                type="dropdown",
                direction="down",
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top",
                buttons=dropdown_buttons,
                pad=dict(r=10, t=10),
            )
        ]

        layout: go.Layout = go.Layout(
            title=dict(
                text="NBA Player Averaged and Normalized Advanced Career Metrics - 3D Feature Space",
                font=dict(size=18),
            ),
            updatemenus=update_menus,
            scene=dict(
                xaxis=dict(title="Career Avg & Normalized PER"),
                yaxis=dict(title="Career Avg & Normalized WS/48"),
                zaxis=dict(title="Career Avg & Normalized VORP"),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            ),
            margin=dict(l=0, r=0, b=0, t=60),
        )

        fig: go.Figure = go.Figure(data=[main_scatter], layout=layout)
        fig.show()

    def display_umap_rending(self) -> None:
        visual_points: list[VisualPlayerPoint] = self._get_visual_player_points_list()

        x_coords: list[float] = [p.x_coordinate for p in visual_points]
        y_coords: list[float] = [p.y_coordinate for p in visual_points]
        z_coords: list[float] = [p.z_coordinate for p in visual_points]
        num_players: int = len(visual_points)

        # Baseline point attributes
        base_marker_sizes: list[float] = [5.0]
        base_opacity: list[float] = [0.75] * num_players

        # Hover tooltip formatting
        hover_templates: list[str] = [
            f"<b>{p.player_name}</b><br>X: {p.x_coordinate:.2f} | Y: {p.y_coordinate:.2f} | Z: {p.z_coordinate:.2f}"
            for p in visual_points
        ]

        # Primary 3D scatter trace
        main_scatter: go.Scatter3d = go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode="markers+text",
            textposition="top center",
            hoverinfo="text",
            hovertext=hover_templates,
            marker=dict(
                size=base_marker_sizes,
                color=z_coords,
                colorscale="Viridis",
                colorbar=dict(title="UMAP Z-Axis"),
                opacity=0.75,
                line=dict(width=0.5, color="white"),
            ),
        )

        # Construct search dropdown options (updatemenus)
        dropdown_buttons: list[dict] = []

        # Option 1: Reset View Button
        reset_button: dict = dict(
            label="-- Reset Search / Show All --",
            method="update",
            args=[
                {
                    "marker.size": [base_marker_sizes],
                    "marker.opacity": [base_opacity],
                },
                {
                    "scene.annotations": [],
                },
            ],
        )
        dropdown_buttons.append(reset_button)

        # Option 2: Individual Player Search Entries
        for idx, target_point in enumerate(visual_points):
            # Highlight target player, dim all other points
            custom_sizes: list[float] = [4.0] * num_players
            custom_opacities: list[float] = [0.25] * num_players

            # Emphasize target point
            custom_sizes[idx] = 16.0
            custom_opacities[idx] = 1.0

            # Create 3D text callout annotation pointing to searched player
            annotation: dict = dict(
                x=target_point.x_coordinate,
                y=target_point.y_coordinate,
                z=target_point.z_coordinate,
                text=f"SELECTED: {target_point.player_name}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                arrowsize=1.5,
                ax=0,
                ay=-40,
                font=dict(color="black", size=12),
                bgcolor="yellow",
                bordercolor="red",
                borderwidth=2,
            )

            player_button: dict = dict(
                label=f"Find: {target_point.player_name}",
                method="update",
                args=[
                    {
                        "marker.size": [custom_sizes],
                        "marker.opacity": [custom_opacities],
                    },
                    {
                        "scene.annotations": [annotation],
                    },
                ],
            )
            dropdown_buttons.append(player_button)

        # Attach dropdown menu to layout
        update_menus: list[dict] = [
            dict(
                type="dropdown",
                direction="down",
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top",
                buttons=dropdown_buttons,
                pad=dict(r=10, t=10),
            )
        ]

        layout: go.Layout = go.Layout(
            title=dict(
                text="NBA Player Similarity - Unsupervised 3D Vector Space (Use Dropdown to Search)", font=dict(size=18)
            ),
            updatemenus=update_menus,
            scene=dict(
                xaxis=dict(title="UMAP Dimension 1"),
                yaxis=dict(title="UMAP Dimension 2"),
                zaxis=dict(title="UMAP Dimension 3"),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            ),
            margin=dict(l=0, r=0, b=0, t=60),
        )

        fig: go.Figure = go.Figure(data=[main_scatter], layout=layout)

        fig.show()

    def _get_visual_player_advanced_points_list(self) -> list[VisualPlayerPointAdvanced]:
        self._logger.info("Generating 3D Coordinate Mapping for UMAP Generation")
        self._logger.info("=" * 100)

        player_embeddings_array: np.ndarray = self._player_embedding.get_all_nba_player_embeddings_array()
        player_ids_list: list[int] = self._player_embedding.get_player_ids_list()
        player_names_list: list[str] = self._player_embedding.get_names_list()

        visual_player_advanced_point_list: list[VisualPlayerPointAdvanced] = []

        for index_num, player_name in enumerate(player_names_list):
            visual_player_point_obj: VisualPlayerPointAdvanced = VisualPlayerPointAdvanced(
                player_id=player_ids_list[index_num],
                player_name=player_names_list[index_num],
                per=float(player_embeddings_array[index_num, 0]),
                ws_per_48=float(player_embeddings_array[index_num, 1]),
                vorp=float(player_embeddings_array[index_num, 2]),
            )

            visual_player_advanced_point_list.append(visual_player_point_obj)

        return visual_player_advanced_point_list

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
            n_neighbors=3,
            min_dist=0.1,
            metric="cosine",
            random_state=42,
        )

        player_embeddings_array: np.ndarray = self._player_embedding.get_all_nba_player_embeddings_array()

        coordinate_array: np.ndarray = dimension_reducer.fit_transform(X=player_embeddings_array)

        self._logger.info(f"Reduced embeddings from {player_embeddings_array.shape} to {coordinate_array.shape}")

        return coordinate_array
