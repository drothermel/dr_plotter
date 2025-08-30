from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from dr_plotter import consts
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.theme import VIOLIN_THEME, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    ComponentSchema,
    Phase,
    SubPlotterParamName,
    VisualChannel,
)

from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    plotter_name: str = "violin"
    plotter_params: List[str] = [
        "alpha",
        "color",
        "label",
        "hue_by",
        "marker_by",
        "style_by",
        "size_by",
    ]
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
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
            "bodies": {"facecolor", "edgecolor", "alpha", "linewidth"},
            "stats": {"color", "linewidth", "linestyle"},
        },
    }

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Optional[Theme] = None,
        figure_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
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
        if not self._has_groups:
            self._draw_simple(ax, data, **kwargs)

    def _apply_post_processing(
        self, parts: Dict[str, Any], label: Optional[str] = None
    ) -> None:
        artists = self._collect_all_parts_to_style(parts)
        self.style_applicator.apply_post_processing("violin", artists)
        if self._should_create_legend():
            label = (
                label
                if label is not None
                else self.style_applicator.get_style_with_fallback("missing_label_str")
            )
            proxy = self._create_proxy_artist_from_bodies(parts["bodies"])
            self._register_legend_entry_if_valid(proxy, label)

    def _collect_all_parts_to_style(self, parts: Dict[str, Any]) -> Dict[str, Any]:
        artists = {
            "bodies": parts["bodies"],
        }
        stats_parts = [parts[bar] for bar in ["cbars", "cmins", "cmaxes"]]
        if self.style_applicator.get_style_with_fallback("showmeans"):
            stats_parts.append(parts["cmeans"])
        if self.style_applicator.get_style_with_fallback("showmedians"):
            stats_parts.append(parts["cmedians"])
        artists["stats"] = stats_parts
        return artists

    def _create_proxy_artist_from_bodies(self, bodies: List[Any]) -> Optional[Patch]:
        if not bodies:
            return None

        first_body = bodies[0]

        assert hasattr(first_body, "get_facecolor"), (
            "Body must have get_facecolor method"
        )
        facecolor = first_body.get_facecolor()

        if hasattr(facecolor, "__len__") and len(facecolor) > 0:
            fc = facecolor[0]
            if isinstance(fc, np.ndarray) and fc.size >= 3:
                facecolor = tuple(fc[:4] if fc.size >= 4 else list(fc[:3]) + [1.0])
            else:
                facecolor = self.figure_manager.legend_manager.get_error_color(
                    "face", self.theme
                )
        else:
            facecolor = self.figure_manager.legend_manager.get_error_color(
                "face", self.theme
            )

        assert hasattr(first_body, "get_edgecolor"), (
            "Body must have get_edgecolor method"
        )
        edgecolor = first_body.get_edgecolor()

        if hasattr(edgecolor, "__len__") and len(edgecolor) > 0:
            ec = edgecolor[0]
            if isinstance(ec, np.ndarray) and ec.size >= 3:
                edgecolor = tuple(ec[:4] if ec.size >= 4 else list(ec[:3]) + [1.0])
            else:
                edgecolor = self.figure_manager.legend_manager.get_error_color(
                    "edge", self.theme
                )
        else:
            edgecolor = self.figure_manager.legend_manager.get_error_color(
                "edge", self.theme
            )

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
        parts = ax.violinplot(datasets, **self._filtered_plot_kwargs)

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
        has_x_labels = consts.X_COL_NAME in data.columns

        if has_x_labels:
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
                    **self._filtered_plot_kwargs,
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
                **self._filtered_plot_kwargs,
            )

        self._apply_post_processing(parts, label)
