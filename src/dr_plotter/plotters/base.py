from __future__ import annotations
from typing import Any

import pandas as pd

from dr_plotter import consts
from dr_plotter.channel_metadata import ChannelRegistry
from dr_plotter.configs import GroupingConfig
from dr_plotter.plotters.style_engine import StyleEngine
from dr_plotter.style_applicator import StyleApplicator
from dr_plotter.theme import BASE_COLORS, BASE_THEME, DR_PLOTTER_STYLE_KEYS, Theme
from dr_plotter.types import (
    BasePlotterParamName,
    ColName,
    ComponentSchema,
    GroupContext,
    GroupInfo,
    Phase,
    StyleAttrName,
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


def as_list(x: Any | list[Any] | None) -> list[Any]:
    return x if isinstance(x, list) else [x]


def fmt_txt(text: str) -> str:
    if text is not None:
        return text.replace("_", " ").title()


def ylabel_from_metrics(metrics: list[ColName]) -> str | None:
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
    def list_plotters(cls) -> list[str]:
        return sorted(cls._registry.keys())

    plotter_name: str = "base"
    plotter_params: list[str] = []
    param_mapping: dict[BasePlotterParamName, SubPlotterParamName] = {}
    enabled_channels: set[VisualChannel] = set()
    default_theme: Theme = BASE_THEME
    supports_legend: bool = True
    supports_grouped: bool = True

    component_schema: dict[Phase, ComponentSchema] = {
        "plot": {"main": set()},
        "axes": {
            "title": {"text", "fontsize", "color"},
            "xlabel": {"text", "fontsize", "color"},
            "ylabel": {"text", "fontsize", "color"},
            "grid": {"visible", "alpha", "color", "linestyle"},
        },
    }

    def __init__(
        self,
        data: pd.DataFrame,
        grouping_cfg: GroupingConfig,
        theme: Theme | None = None,
        figure_manager: Any | None = None,
        **kwargs: Any,
    ) -> None:
        self.raw_data: pd.DataFrame = data
        self.kwargs: dict[str, Any] = kwargs
        self.figure_manager: Any | None = figure_manager
        grouping_cfg.validate_against_enabled(self.__class__.enabled_channels)
        self.grouping_params: GroupingConfig = grouping_cfg
        self.theme = self.__class__.default_theme if theme is None else theme
        self.style_engine: StyleEngine = StyleEngine(self.theme, self.figure_manager)
        self.styler: StyleApplicator = StyleApplicator(
            self.theme,
            self.kwargs,
            self.grouping_params,
            figure_manager=self.figure_manager,
            plot_type=self.__class__.plotter_name,
            style_engine=self.style_engine,
        )
        self.plot_data: pd.DataFrame | None = None
        self._initialize_subplot_specific_params()

        self.styler.register_post_processor(
            self.__class__.plotter_name, "title", self._style_title
        )
        self.styler.register_post_processor(
            self.__class__.plotter_name, "xlabel", self._style_xlabel
        )
        self.styler.register_post_processor(
            self.__class__.plotter_name, "ylabel", self._style_ylabel
        )
        self.styler.register_post_processor(
            self.__class__.plotter_name, "grid", self._style_grid
        )

        self.x_col: ColName | None = self._get_x_metric_column_name()
        self.y_cols: list[ColName] = self._get_y_metric_column_names()

    @property
    def _has_groups(self) -> bool:
        return len(self.grouping_params.active_channels) > 0

    @property
    def _multi_metric(self) -> bool:
        return len(self._get_y_metric_column_names()) > 1

    @property
    def _filtered_plot_kwargs(self) -> dict[str, Any]:
        filter_keys = set(
            DR_PLOTTER_STYLE_KEYS
            + self.grouping_params.channel_strs
            + BASE_PLOTTER_PARAMS
            + self.__class__.plotter_params
        )
        return {k: v for k, v in self.kwargs.items() if k not in filter_keys}

    def _plot_specific_data_prep(self) -> None:
        pass

    def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
        pass

    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        if not self.supports_grouped:
            self._draw(ax, self.plot_data, **kwargs)
        else:
            self._draw(ax, data, **kwargs)

    def _setup_continuous_channels(self) -> None:
        for channel in self.grouping_params.active_channels_ordered:
            spec = ChannelRegistry.get_spec(channel)
            if spec.channel_type == "continuous":
                column = getattr(self.grouping_params, channel)
                if column and column in self.plot_data.columns:
                    values = self.plot_data[column].dropna().tolist()
                    sample_values = values[:5]
                    assert all(
                        isinstance(v, (int, float))
                        or (
                            isinstance(v, str)
                            and v.replace(".", "").replace("-", "").isdigit()
                        )
                        for v in sample_values
                    ), f"Column {column} contains non-numeric values"

                    if values:
                        self.style_engine.set_continuous_range(channel, column, values)

    def render(self, ax: Any) -> None:
        self.prepare_data()
        self.current_axis = ax
        self._setup_continuous_channels()

        if self._has_groups:
            self._render_with_grouped_method(ax)
        else:
            component_styles = self.styler.get_component_styles(
                self.__class__.plotter_name
            )
            style_kwargs = component_styles.get("main", {})

            self._draw(
                ax,
                self.plot_data,
                **style_kwargs,
            )

        if self._has_groups:
            self.styler.clear_group_context()

        self._apply_styling(ax)

    def prepare_data(self) -> None:
        self.plot_data = self.raw_data.copy()

        if self.x_col is not None:
            self.plot_data = self.plot_data.rename(
                columns={self.x_col: consts.X_COL_NAME}
            )

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

    def _build_plot_args(self) -> dict[str, Any]:
        main_plot_params = self.component_schema.get("plot", {}).get("main", set())
        plot_args = {}
        for key in main_plot_params:
            if key in self._filtered_plot_kwargs:
                plot_args[key] = self._filtered_plot_kwargs[key]
            else:
                style = self.styler.get_style(key)
                if style is not None:
                    plot_args[key] = style
        return plot_args

    def _should_create_legend(self) -> bool:
        if not self.supports_legend:
            return False
        legend_param = self.kwargs.get("legend", self.theme.get("legend"))
        return legend_param is not False

    def _register_legend_entry_if_valid(self, artist: Any, label: str | None) -> None:
        if not self._should_create_legend():
            return
        if self.figure_manager and label and artist:
            entry = self.styler.create_legend_entry(artist, label, self.current_axis)
            if entry:
                self.figure_manager.register_legend_entry(entry)

    def _apply_styling(self, ax: Any) -> None:
        artists = {
            "title": ax,
            "xlabel": ax,
            "ylabel": ax,
            "grid": ax,
        }
        self.styler.apply_post_processing(self.__class__.plotter_name, artists)

    def _render_with_grouped_method(self, ax: Any) -> None:
        grouped_data = self._process_grouped_data()
        x_categories = self._extract_x_categories()

        for group_index, group_info in enumerate(grouped_data):
            group_context = self._setup_group_context(
                group_info, group_index, len(grouped_data)
            )
            plot_kwargs = self._resolve_group_plot_kwargs(group_context)
            group_position = self._calculate_group_position(
                group_index, len(grouped_data), x_categories
            )

            self._draw_grouped(ax, group_context["data"], group_position, **plot_kwargs)

    def _process_grouped_data(self) -> list[GroupInfo]:
        categorical_cols = []
        for channel, column in self.grouping_params.active.items():
            spec = ChannelRegistry.get_spec(channel)
            if spec.channel_type == "categorical":
                categorical_cols.append(column)

        if categorical_cols:
            grouped = self.plot_data.groupby(categorical_cols, observed=False)
            return list(grouped)
        else:
            return [(None, self.plot_data)]

    def _extract_x_categories(self) -> Any | None:
        if hasattr(self, "x") and self.x_col:
            return self.plot_data[self.x_col].unique()
        return None

    def _setup_group_context(
        self, group_info: GroupInfo, group_index: int, n_groups: int
    ) -> GroupContext:
        name, group_data = group_info

        categorical_cols = []
        for channel, column in self.grouping_params.active.items():
            spec = ChannelRegistry.get_spec(channel)
            if spec.channel_type == "categorical":
                categorical_cols.append(column)

        if name is None:
            group_values = {}
        elif isinstance(name, tuple):
            group_values = dict(zip(categorical_cols, name))
        else:
            group_values = {categorical_cols[0]: name} if categorical_cols else {}

        return {
            "name": name,
            "data": group_data,
            "values": group_values,
            "categorical_cols": categorical_cols,
        }

    def _resolve_group_plot_kwargs(self, group_context: GroupContext) -> dict[str, Any]:
        self.styler.set_group_context(group_context["values"])
        component_styles = self.styler.get_component_styles(self.__class__.plotter_name)
        plot_kwargs = component_styles.get("main", {})
        plot_kwargs["label"] = self._build_group_label(
            group_context["name"], group_context["categorical_cols"]
        )

        if (
            self.__class__.plotter_name == "scatter"
            and "size" in self.grouping_params.active_channels
        ):
            size_col = self.grouping_params.size
            if size_col and size_col in group_context["data"].columns:
                sizes = []
                for value in group_context["data"][size_col]:
                    style = self.style_engine._get_continuous_style(
                        "size", size_col, value
                    )
                    size_mult = style.get("size_mult", 1.0)
                    base_size = plot_kwargs.get("s", 50)
                    sizes.append(
                        base_size * size_mult
                        if isinstance(base_size, (int, float))
                        else 50 * size_mult
                    )
                plot_kwargs["s"] = sizes

        return plot_kwargs

    def _calculate_group_position(
        self, group_index: int, n_groups: int, x_categories: Any | None = None
    ) -> dict[str, Any]:
        width = 0.8 / n_groups
        offset = width * (group_index - n_groups / 2 + 0.5)

        return {
            "index": group_index,
            "total": n_groups,
            "width": width,
            "offset": offset,
            "x_categories": x_categories,
        }

    def _build_group_plot_kwargs(
        self, styles: dict[StyleAttrName, Any], name: Any, group_cols: list[str]
    ) -> dict[str, Any]:
        default_color = styles.get("color") or self.theme.general_styles.get(
            "default_color", BASE_COLORS[0]
        )

        plot_kwargs = {
            "color": default_color,
            "alpha": styles.get("alpha", self.styler.get_style("alpha", 1.0)),
        }

        if "linestyle" in styles:
            plot_kwargs["linestyle"] = styles["linestyle"]
        if "marker" in styles:
            plot_kwargs["marker"] = styles["marker"]
        if "size_mult" in styles:
            if hasattr(self, "line_width"):
                plot_kwargs["linewidth"] = self.styler.get_computed_style(
                    "line_width", "multiply", styles["size_mult"]
                )
            elif hasattr(self, "marker_size"):
                plot_kwargs["s"] = self.styler.get_computed_style(
                    "marker_size", "multiply", styles["size_mult"]
                )

        user_kwargs = self._filtered_plot_kwargs
        for k, v in user_kwargs.items():
            if k not in plot_kwargs:
                plot_kwargs[k] = v

        plot_kwargs["label"] = self._build_group_label(name, group_cols)

        return plot_kwargs

    def _mapped_param(self, param: BasePlotterParamName) -> SubPlotterParamName:
        return self.__class__.param_mapping.get(param, param)

    def _unmapped_param(self, param: SubPlotterParamName) -> BasePlotterParamName:
        return {v: k for k, v in self.__class__.param_mapping.items()}.get(param, param)

    def _get_x_metric_column_name(self) -> ColName | None:
        subplotter_x_metric = self._mapped_param("x")
        return self.kwargs.get(subplotter_x_metric)

    def _get_y_metric_column_names(self) -> list[ColName]:
        subplotter_y_metric = self._mapped_param("y")
        metric_col_name = self.kwargs.get(subplotter_y_metric)
        return as_list(metric_col_name if metric_col_name is not None else [])

    def _initialize_subplot_specific_params(self) -> None:
        for param in self.__class__.plotter_params:
            setattr(self, param, self.kwargs.get(param))

    def _build_group_label(self, name: Any, group_cols: list[str]) -> str:
        if isinstance(name, tuple):
            if len(name) == 1:
                return str(name[0])
            label_parts = []
            for col, val in zip(group_cols, name):
                if col == consts.METRIC_COL_NAME:
                    label_parts.append(str(val))
                else:
                    label_parts.append(f"{col}={val}")
            return ", ".join(label_parts)
        return str(name)

    def _style_title(self, ax: Any, styles: dict[str, Any]) -> None:
        title_text = styles.get("text", self.styler.get_style("title"))
        if title_text:
            ax.set_title(
                title_text,
                fontsize=styles.get("fontsize", self.theme.get("title_fontsize")),
                color=styles.get("color", self.theme.get("title_color")),
            )

    def _style_xlabel(self, ax: Any, styles: dict[str, Any]) -> None:
        xlabel_text = styles.get(
            "text",
            self.styler.get_style("xlabel", None),
        )
        if xlabel_text:
            ax.set_xlabel(
                xlabel_text,
                fontsize=styles.get(
                    "fontsize",
                    self.styler.get_style("label_fontsize"),
                ),
                color=styles.get("color", self.theme.get("label_color")),
            )

    def _style_ylabel(self, ax: Any, styles: dict[str, Any]) -> None:
        ylabel_text = styles.get(
            "text",
            self.styler.get_style("ylabel", None),
        )
        if ylabel_text:
            ax.set_ylabel(
                ylabel_text,
                fontsize=styles.get(
                    "fontsize",
                    self.styler.get_style("label_fontsize"),
                ),
                color=styles.get("color", self.theme.get("label_color")),
            )

    def _style_grid(self, ax: Any, styles: dict[str, Any]) -> None:
        grid_visible = styles.get("visible", self.styler.get_style("grid", True))
        if grid_visible:
            ax.grid(
                True,
                alpha=styles.get("alpha", self.theme.get("grid_alpha")),
                color=styles.get("color", self.theme.get("grid_color")),
                linestyle=styles.get(
                    "linestyle", self.theme.get("grid_linestyle", "-")
                ),
            )
        else:
            ax.grid(False)
