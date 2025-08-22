from typing import Any, Dict, List, Optional, Set

import pandas as pd

from dr_plotter import consts
from dr_plotter.grouping import GroupingConfig
from dr_plotter.legend import Legend
from dr_plotter.plotters.style_engine import StyleEngine
from dr_plotter.theme import BASE_COLORS, BASE_THEME, DR_PLOTTER_STYLE_KEYS, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    ColName,
    SubPlotterParamName,
    VisualChannel,
)

BASE_PLOTTER_PARAMS = [
    "x",
    "y",
    "colorbar_label",
    "_figure_manager",
    "_shared_hue_styles",
]


def as_list(x: Optional[Any | List[Any]]) -> List[Any]:
    return x if isinstance(x, list) else [x]


def fmt_txt(text: str) -> str:
    if text is not None:
        return text.replace("_", " ").title()


def ylabel_from_metrics(metrics: List[ColName]) -> str:
    if len(metrics) != 1:
        return None
    return metrics[0]


class BasePlotter:
    _registry = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        BasePlotter._registry[cls.plotter_name] = cls

    @classmethod
    def get_plotter(cls, plot_type: str) -> type:
        return cls._registry[plot_type]

    @classmethod
    def list_plotters(cls) -> List[str]:
        return sorted(cls._registry.keys())

    plotter_name: str = "base"
    plotter_params: List[str] = []
    param_mapping: Dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: Set[VisualChannel] = set()
    default_theme: Theme = BASE_THEME

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Optional[Theme] = None,
        figure_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        self.raw_data: pd.DataFrame = data
        self.kwargs: Dict[str, Any] = kwargs
        self.figure_manager: Optional[Any] = figure_manager
        grouping_cfg.validate_against_enabled(self.__class__.enabled_channels)
        self.grouping_params: GroupingConfig = grouping_cfg
        self.theme = self.__class__.default_theme if theme is None else theme
        self.style_engine: StyleEngine = StyleEngine(self.theme, self.figure_manager)
        self.plot_data: Optional[pd.DataFrame] = None
        self._initialize_subplot_specific_params()

        self.x_col: Optional[ColName] = self._get_x_metric_column_name()
        self.y_cols: List[ColName] = self._get_y_metric_column_names()

    @property
    def _has_groups(self) -> bool:
        return len(self.grouping_params.active_channels) > 0

    @property
    def _multi_metric(self) -> bool:
        return len(self._get_y_metric_column_names()) > 1

    @property
    def _filtered_plot_kwargs(self) -> Dict[str, Any]:
        filter_keys = set(
            DR_PLOTTER_STYLE_KEYS
            + self.grouping_params.channel_strs
            + BASE_PLOTTER_PARAMS
            + self.__class__.plotter_params
        )
        return {k: v for k, v in self.kwargs.items() if k not in filter_keys}

    def _plot_specific_data_prep(self) -> None:
        pass

    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        pass

    def render(self, ax: Any) -> None:
        self.prepare_data()
        legend = Legend()
        style_kwargs = {
            **self.theme.plot_styles,
            **self._filtered_plot_kwargs,
        }
        self._draw(
            ax,
            self.plot_data,
            legend,
            **style_kwargs,
        )
        self._apply_styling(ax, legend)

    def prepare_data(self) -> None:
        self.plot_data = self.raw_data.copy()

        if self.x_col is not None:
            self.plot_data.rename(columns={self.x_col: consts.X_COL_NAME}, inplace=True)

        if len(self.y_cols) > 0:
            df_cols = set(self.plot_data.columns)
            value_cols = set(self.y_cols)
            assert len(value_cols - df_cols) == 0, "All metrics must be in the data"
            id_cols = df_cols - value_cols
            self.plot_data = pd.melt(
                self.plot_data,
                id_vars=id_cols,
                value_vars=self.y_cols,
                var_name=consts.METRIC_COL_NAME,
                value_name=consts.Y_COL_NAME,
            )

        self._plot_specific_data_prep()

    def _get_style(self, key: str, default_override: Optional[Any] = None) -> Any:
        return self.kwargs.get(key, self.theme.get(key, default_override))

    def _apply_styling(self, ax: Any, legend: Legend) -> None:
        ax.set_title(
            self._get_style("title"), fontsize=self.theme.get("title_fontsize")
        )

        label_fontsize = self._get_style("label_fontsize")
        xlabel = self._get_style("xlabel", fmt_txt(self.x_col))
        ylabel = self._get_style(
            "ylabel",
            fmt_txt(ylabel_from_metrics(self.y_cols)),
        )
        ax.set_xlabel(xlabel, fontsize=label_fontsize)
        ax.set_ylabel(ylabel, fontsize=label_fontsize)

        if self._get_style("grid", True):
            ax.grid(True, alpha=self.theme.get("grid_alpha"))
        else:
            ax.grid(False)

        if self._get_style("legend") is None or self._get_style("legend"):
            if self._has_groups or legend.has_entries():
                if not ax.get_legend():
                    if legend.has_entries():
                        ax.legend(
                            handles=legend.get_handles(),
                            fontsize=self.theme.get("legend_fontsize"),
                        )
                    else:
                        ax.legend(fontsize=self.theme.get("legend_fontsize"))
            elif self._get_style("legend") is True:
                if not ax.get_legend():
                    ax.legend(fontsize=self.theme.get("legend_fontsize"))

    def _render_with_grouped_method(self, ax: Any, legend: Legend) -> None:
        group_cols = list(self.grouping_params.active.values())
        grouped = self.plot_data.groupby(group_cols)
        n_groups = len(grouped)

        x_categories = None
        if hasattr(self, "x") and self.x_col:
            x_categories = self.plot_data[self.x_col].unique()

        for group_index, (name, group_data) in enumerate(grouped):
            if isinstance(name, tuple):
                group_values = dict(zip(group_cols, name))
            else:
                group_values = {group_cols[0]: name}

            styles = self.style_engine.get_styles_for_group(
                group_values, self.grouping_params
            )
            plot_kwargs = self._build_group_plot_kwargs(styles, name, group_cols)
            group_position = self._calculate_group_position(group_index, n_groups)
            group_position["x_categories"] = x_categories

            self._draw_grouped(ax, group_data, group_position, legend, **plot_kwargs)

    def _calculate_group_position(
        self, group_index: int, n_groups: int
    ) -> Dict[str, Any]:
        width = 0.8 / n_groups
        offset = width * (group_index - n_groups / 2 + 0.5)

        return {
            "index": group_index,
            "total": n_groups,
            "width": width,
            "offset": offset,
        }

    def _build_group_plot_kwargs(
        self, styles: Dict[str, Any], name: Any, group_cols: List[str]
    ) -> Dict[str, Any]:
        default_color = styles.get("color", BASE_COLORS[0])

        plot_kwargs = {
            "color": default_color,
            "alpha": styles.get("alpha", self._get_style("alpha", 1.0)),
        }

        if "linestyle" in styles:
            plot_kwargs["linestyle"] = styles["linestyle"]
        if "marker" in styles:
            plot_kwargs["marker"] = styles["marker"]
        if "size_mult" in styles:
            if hasattr(self, "line_width"):
                plot_kwargs["linewidth"] = (
                    self._get_style("line_width", 2.0) * styles["size_mult"]
                )
            elif hasattr(self, "marker_size"):
                plot_kwargs["s"] = (
                    self._get_style("marker_size", 50) * styles["size_mult"]
                )

        user_kwargs = self._filtered_plot_kwargs
        for k, v in user_kwargs.items():
            if k not in plot_kwargs:
                plot_kwargs[k] = v

        if isinstance(name, tuple):
            if len(name) == 1:
                plot_kwargs["label"] = str(name[0])
            else:
                label_parts = []
                for col, val in zip(group_cols, name):
                    if col == consts.METRIC_COL_NAME:
                        label_parts.append(str(val))
                    else:
                        label_parts.append(f"{col}={val}")
                plot_kwargs["label"] = ", ".join(label_parts)
        else:
            plot_kwargs["label"] = str(name)

        return plot_kwargs

    def _mapped_param(self, param: BasePlotterParamName) -> SubPlotterParamName:
        return self.__class__.param_mapping.get(param, param)

    def _unmapped_param(self, param: SubPlotterParamName) -> BasePlotterParamName:
        return {v: k for k, v in self.__class__.param_mapping.items()}.get(param, param)

    def _get_x_metric_column_name(self) -> Optional[ColName]:
        subplotter_x_metric = self._mapped_param("x")
        return self.kwargs.get(subplotter_x_metric)

    def _get_y_metric_column_names(self) -> List[ColName]:
        subplotter_y_metric = self._mapped_param("y")
        metric_col_name = self.kwargs.get(subplotter_y_metric)
        return as_list(metric_col_name if metric_col_name is not None else [])

    def _initialize_subplot_specific_params(self) -> None:
        for param in self.__class__.plotter_params:
            setattr(self, param, self.kwargs.get(param))

    def _style_zero_line(self, ax: Any) -> None:
        ax.axhline(y=0, linewidth=2.0, color="#333333", zorder=0.5)
