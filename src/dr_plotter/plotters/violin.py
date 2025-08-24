from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.theme import VIOLIN_THEME, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    SubPlotterParamName,
    VisualChannel,
    Phase,
    ComponentSchema,
)

from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    plotter_name: str = "violin"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = {"hue"}
    default_theme: Theme = VIOLIN_THEME

    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                "showmeans",
                "showmedians",
                "showextrema",
                "widths",
                "points",
            }
        },
        "post": {
            "bodies": {"facecolor", "edgecolor", "alpha", "linewidth"},
            "stats": {"color", "linewidth", "linestyle"},
        },
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.style_applicator.register_post_processor(
            "violin", "bodies", self._style_violin_bodies
        )
        self.style_applicator.register_post_processor(
            "violin", "stats", self._style_violin_stats
        )

    def _style_violin_bodies(self, bodies: Any, styles: Dict[str, Any]) -> None:
        for pc in bodies:
            for attr, value in styles.items():
                if attr == "facecolor" and hasattr(pc, "set_facecolor"):
                    pc.set_facecolor(value)
                elif attr == "edgecolor" and hasattr(pc, "set_edgecolor"):
                    pc.set_edgecolor(value)
                elif attr == "alpha" and hasattr(pc, "set_alpha"):
                    pc.set_alpha(value)
                elif attr == "linewidth" and hasattr(pc, "set_linewidth"):
                    pc.set_linewidth(value)

    def _style_violin_stats(self, stats: Any, styles: Dict[str, Any]) -> None:
        for attr, value in styles.items():
            if attr == "color" and hasattr(stats, "set_edgecolor"):
                stats.set_edgecolor(value)
            elif attr == "linewidth" and hasattr(stats, "set_linewidth"):
                stats.set_linewidth(value)
            elif attr == "linestyle" and hasattr(stats, "set_linestyle"):
                stats.set_linestyle(value)
            elif hasattr(stats, f"set_{attr}"):
                setter = getattr(stats, f"set_{attr}")
                setter(value)

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        if self._has_groups:
            pass
        else:
            self._draw_simple(ax, data, **kwargs)

    def _apply_post_processing(
        self, parts: Dict[str, Any], label: Optional[str] = None
    ) -> None:
        if not self._should_create_legend():
            return

        artists = {}
        if "bodies" in parts:
            artists["bodies"] = parts["bodies"]

        stats_parts = []
        for part_name in ("cbars", "cmins", "cmaxes", "cmeans"):
            if part_name in parts:
                stats_parts.append(parts[part_name])

        if stats_parts:
            for stats in stats_parts:
                artists["stats"] = stats
                self.style_applicator.apply_post_processing("violin", {"stats": stats})

        if artists:
            self.style_applicator.apply_post_processing("violin", artists)

        if label and "bodies" in parts and parts["bodies"]:
            proxy = self._create_proxy_artist_from_bodies(parts["bodies"])

            if self.figure_manager and proxy:
                entry = self.style_applicator.create_legend_entry(
                    proxy, label, self.current_axis
                )
                if entry:
                    self.figure_manager.register_legend_entry(entry)

    def _create_proxy_artist_from_bodies(self, bodies: List[Any]) -> Optional[Patch]:
        if not bodies:
            return None

        first_body = bodies[0]

        try:
            facecolor = first_body.get_facecolor()
            if hasattr(facecolor, "__len__") and len(facecolor) > 0:
                fc = facecolor[0]
                if isinstance(fc, np.ndarray) and fc.size >= 3:
                    facecolor = tuple(fc[:4] if fc.size >= 4 else list(fc[:3]) + [1.0])
                else:
                    facecolor = self.figure_manager.legend_manager.get_error_color(
                        "face"
                    )
            else:
                facecolor = self.figure_manager.legend_manager.get_error_color("face")
        except:
            facecolor = self.figure_manager.legend_manager.get_error_color("face")

        try:
            edgecolor = first_body.get_edgecolor()
            if hasattr(edgecolor, "__len__") and len(edgecolor) > 0:
                ec = edgecolor[0]
                if isinstance(ec, np.ndarray) and ec.size >= 3:
                    edgecolor = tuple(ec[:4] if ec.size >= 4 else list(ec[:3]) + [1.0])
                else:
                    edgecolor = self.figure_manager.legend_manager.get_error_color(
                        "edge"
                    )
            else:
                edgecolor = self.figure_manager.legend_manager.get_error_color("edge")
        except:
            edgecolor = self.figure_manager.legend_manager.get_error_color("edge")

        alpha = first_body.get_alpha() if hasattr(first_body, "get_alpha") else 1.0

        return Patch(facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)

    def _draw_simple(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        groups = []
        group_data = [data]
        if consts.X_COL_NAME in data.columns:
            groups = data[consts.X_COL_NAME].unique()
            group_data = [data[data[consts.X_COL_NAME] == group] for group in groups]
        datasets = [gd[consts.Y_COL_NAME].dropna() for gd in group_data]

        label = kwargs.pop("label", None)
        parts = ax.violinplot(datasets, **kwargs)

        if len(groups) > 0:
            ax.set_xticks(np.arange(1, len(groups) + 1))
            ax.set_xticklabels(groups)

        self._apply_post_processing(parts, label)

    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        label = kwargs.pop("label", None)

        if consts.X_COL_NAME in data.columns:
            x_categories = group_position.get("x_categories")
            if x_categories is None:
                x_categories = data[consts.X_COL_NAME].unique()

            dataset = []
            positions = []
            for i, cat in enumerate(x_categories):
                cat_data = data[data[consts.X_COL_NAME] == cat][
                    consts.Y_COL_NAME
                ].dropna()
                if not cat_data.empty:
                    dataset.append(cat_data)
                    positions.append(i + group_position["offset"])

            if dataset:
                parts = ax.violinplot(
                    dataset,
                    positions=positions,
                    widths=group_position["width"],
                    **kwargs,
                )
            else:
                parts = {}

            if group_position["index"] == 0:
                ax.set_xticks(np.arange(len(x_categories)))
                ax.set_xticklabels(x_categories)
        else:
            parts = ax.violinplot(
                [data[consts.Y_COL_NAME].dropna()],
                positions=[group_position["offset"]],
                widths=group_position["width"],
                **kwargs,
            )

        self._apply_post_processing(parts, label)
