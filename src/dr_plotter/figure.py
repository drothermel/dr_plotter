from typing import Any, Dict, List, Optional, Tuple
import math

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.cycle_config import CycleConfig
from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.figure_config import FigureConfig
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.legend_manager import (
    LegendConfig,
    LegendEntry,
    LegendManager,
    LegendStrategy,
)
from dr_plotter.theme import BASE_THEME, Theme
from .plotters import BasePlotter


class FigureManager:
    def __init__(
        self,
        figure: Optional["FigureConfig"] = None,
        legend: Optional[LegendConfig] = None,
        theme: Optional[Any] = None,
    ) -> None:
        figure = figure or FigureConfig()
        legend = legend or LegendConfig()

        if theme and hasattr(theme, "legend_config") and theme.legend_config:
            legend = theme.legend_config

        figure.validate()
        legend.validate() if hasattr(legend, "validate") else None

        self._init_from_configs(figure, legend, theme)

    def _init_from_configs(
        self,
        figure: "FigureConfig",
        legend: Optional[LegendConfig],
        theme: Optional[Any] = None,
    ) -> None:
        figure.validate()

        self.figure_config = figure
        self._setup_layout_configuration(figure)

        fig, axes, external_mode = self._create_figure_axes(
            figure.external_ax,
            figure.figure_kwargs,
            figure.subplot_kwargs,
            figure.figsize,
            figure.rows,
            figure.cols,
        )
        self.fig = fig
        self.figure = fig
        self.axes = axes
        self.external_mode = external_mode

        legend_manager = self._build_legend_system(legend, theme)
        self.legend_config = legend_manager.config
        self.legend_manager = legend_manager

        self._coordinate_styling(theme, figure.shared_styling)

        self._facet_grid_info: Optional[Dict[str, Any]] = None

    @classmethod
    def _create_from_configs(
        cls,
        figure: "FigureConfig",
        legend: Optional[LegendConfig],
        theme: Optional[Any] = None,
    ) -> "FigureManager":
        instance = cls.__new__(cls)
        instance._init_from_configs(figure, legend, theme)
        return instance

    def _create_figure_axes(
        self,
        external_ax: Optional[plt.Axes],
        figure_kwargs: Dict[str, Any],
        subplot_kwargs: Dict[str, Any],
        figsize: Tuple[int, int],
        rows: int,
        cols: int,
    ) -> Tuple[plt.Figure, plt.Axes, bool]:
        if external_ax is not None:
            return external_ax.get_figure(), external_ax, True

        combined_kwargs = {**figure_kwargs, **subplot_kwargs}
        if "figsize" not in combined_kwargs:
            combined_kwargs["figsize"] = figsize

        fig, axes = plt.subplots(
            rows, cols, constrained_layout=False, **combined_kwargs
        )
        return fig, axes, False

    def _setup_layout_configuration(self, figure: "FigureConfig") -> None:
        self._layout_rect = None
        self._layout_pad = figure.tight_layout_pad
        self.rows = figure.rows
        self.cols = figure.cols

    def _build_legend_system(
        self,
        legend_config: Optional[LegendConfig],
        theme: Optional[Theme],
    ) -> LegendManager:
        effective_config = (
            legend_config
            or (
                theme.legend_config
                if theme and hasattr(theme, "legend_config")
                else None
            )
            or LegendConfig()
        )

        return LegendManager(self, effective_config)

    def _coordinate_styling(
        self,
        theme: Optional[Theme],
        shared_styling: Optional[bool],
    ) -> None:
        self.shared_styling = shared_styling

        if self._should_use_shared_cycle_config():
            theme_for_cycle = theme or BASE_THEME
            self.shared_cycle_config = CycleConfig(theme_for_cycle)
        else:
            self.shared_cycle_config = None

    def _should_use_shared_cycle_config(self) -> bool:
        if self.shared_styling is not None:
            return self.shared_styling

        coordination_strategies = {
            LegendStrategy.GROUPED_BY_CHANNEL,
            LegendStrategy.FIGURE_BELOW,
        }
        return self.legend_config.strategy in coordination_strategies

    def __enter__(self) -> "FigureManager":
        return self

    def register_legend_entry(self, entry: LegendEntry) -> None:
        self.legend_manager.registry.add_entry(entry)

    def finalize_legends(self) -> None:
        self.legend_manager.finalize()

    def finalize_layout(self) -> None:
        self.finalize_legends()
        self._apply_axis_labels()

        needs_legend_space = (
            self.legend_config.strategy == LegendStrategy.GROUPED_BY_CHANNEL
            or self.legend_config.strategy == LegendStrategy.FIGURE_BELOW
        )

        if self._layout_rect is not None:
            self.fig.tight_layout(rect=self._layout_rect, pad=self._layout_pad)
        elif needs_legend_space:
            rect = [
                self.legend_config.layout_left_margin,
                self.legend_config.layout_bottom_margin,
                self.legend_config.layout_right_margin,
                self.legend_config.layout_top_margin,
            ]
            self.fig.tight_layout(rect=rect, pad=self._layout_pad)
        elif self.fig._suptitle is not None:
            self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=self._layout_pad)
        elif self._has_subplot_titles():
            self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=self._layout_pad)
        else:
            self.fig.tight_layout(pad=self._layout_pad)

    def _apply_axis_labels(self) -> None:
        if self.external_mode:
            return

        if self.figure_config.x_labels is not None:
            for row_idx, row_labels in enumerate(self.figure_config.x_labels):
                for col_idx, label in enumerate(row_labels):
                    ax = self.get_axes(row_idx, col_idx)
                    if label is not None:
                        ax.set_xlabel(label)
                    else:
                        ax.set_xlabel("")

        if self.figure_config.y_labels is not None:
            for row_idx, row_labels in enumerate(self.figure_config.y_labels):
                for col_idx, label in enumerate(row_labels):
                    ax = self.get_axes(row_idx, col_idx)
                    if label is not None:
                        ax.set_ylabel(label)
                    else:
                        ax.set_ylabel("")

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.finalize_layout()
        return False

    def _has_subplot_titles(self) -> bool:
        if hasattr(self.axes, "flat"):
            axes_to_check = self.axes.flat
        elif hasattr(self.axes, "__iter__") and not isinstance(self.axes, str):
            axes_to_check = self.axes
        else:
            axes_to_check = [self.axes]

        for ax in axes_to_check:
            if ax.get_title():
                return True
        return False

    def get_axes(
        self, row: Optional[int] = None, col: Optional[int] = None
    ) -> plt.Axes:
        if self.external_mode:
            return self.axes

        if not hasattr(self.axes, "__len__"):
            return self.axes
        if self.axes.ndim == 1:
            idx = col if col is not None else row
            return self.axes[idx]
        if row is not None and col is not None:
            return self.axes[row, col]
        elif row is not None:
            return self.axes[row, :]
        elif col is not None:
            return self.axes[:, col]
        return self.axes

    def _add_plot(
        self,
        plotter_class: type,
        plotter_args: tuple,
        row: int,
        col: int,
        **kwargs: Any,
    ) -> None:
        if self.external_mode:
            ax = self.axes
        else:
            ax = self.get_axes(row, col)

        kwargs["grouping_cfg"] = GroupingConfig()
        kwargs["grouping_cfg"].set_kwargs(kwargs)

        plotter = plotter_class(*plotter_args, figure_manager=self, **kwargs)
        plotter.render(ax)

    def _analyze_data_dimensions(
        self, data: pd.DataFrame, config: FacetingConfig
    ) -> Dict[str, List[str]]:
        result = {"rows": [], "cols": [], "lines": []}

        if config.rows is not None:
            assert config.rows in data.columns, (
                f"Row dimension column '{config.rows}' not found in data. Available columns: {sorted(data.columns.tolist())}"
            )
            row_values = data[config.rows].unique().tolist()
            if config.row_order is not None:
                missing_values = [v for v in config.row_order if v not in row_values]
                assert not missing_values, (
                    f"Row order values {missing_values} not found in data['{config.rows}']. Available values: {sorted(row_values)}"
                )
                result["rows"] = config.row_order
            else:
                result["rows"] = sorted(row_values, key=str)

        if config.cols is not None:
            assert config.cols in data.columns, (
                f"Column dimension column '{config.cols}' not found in data. Available columns: {sorted(data.columns.tolist())}"
            )
            col_values = data[config.cols].unique().tolist()
            if config.col_order is not None:
                missing_values = [v for v in config.col_order if v not in col_values]
                assert not missing_values, (
                    f"Column order values {missing_values} not found in data['{config.cols}']. Available values: {sorted(col_values)}"
                )
                result["cols"] = config.col_order
            else:
                result["cols"] = sorted(col_values, key=str)

        if config.lines is not None:
            assert config.lines in data.columns, (
                f"Lines dimension column '{config.lines}' not found in data. Available columns: {sorted(data.columns.tolist())}"
            )
            line_values = data[config.lines].unique().tolist()
            if config.lines_order is not None:
                missing_values = [v for v in config.lines_order if v not in line_values]
                assert not missing_values, (
                    f"Lines order values {missing_values} not found in data['{config.lines}']. Available values: {sorted(line_values)}"
                )
                result["lines"] = config.lines_order
            else:
                result["lines"] = sorted(line_values, key=str)

        return result

    def _compute_facet_grid(
        self, data: pd.DataFrame, config: FacetingConfig
    ) -> Tuple[int, int, Dict[str, Any]]:
        dimensions = self._analyze_data_dimensions(data, config)

        row_values = dimensions["rows"]
        col_values = dimensions["cols"]

        if config.rows and config.cols:
            grid_type = "explicit"
            n_rows = len(row_values)
            n_cols = len(col_values)
            fill_order = [(r, c) for r in range(n_rows) for c in range(n_cols)]

        elif config.rows and config.ncols:
            grid_type = "wrapped_rows"
            n_cols = config.ncols
            n_rows = math.ceil(len(row_values) / n_cols)
            fill_order = []
            for i, _ in enumerate(row_values):
                row_idx = i // n_cols
                col_idx = i % n_cols
                fill_order.append((row_idx, col_idx))

        elif config.cols and config.nrows:
            grid_type = "wrapped_cols"
            n_rows = config.nrows
            n_cols = math.ceil(len(col_values) / n_rows)
            fill_order = []
            for i, _ in enumerate(col_values):
                col_idx = i // n_rows
                row_idx = i % n_rows
                fill_order.append((row_idx, col_idx))

        else:
            assert False, (
                f"Invalid grid configuration. Must specify either (rows + cols), (rows + ncols), or (cols + nrows). Got rows='{config.rows}', cols='{config.cols}', ncols={config.ncols}, nrows={config.nrows}"
            )

        layout_metadata = {
            "row_values": row_values,
            "col_values": col_values,
            "grid_type": grid_type,
            "fill_order": fill_order,
            "dimensions": dimensions,
        }

        return n_rows, n_cols, layout_metadata

    def _resolve_targeting(
        self, config: FacetingConfig, grid_rows: int, grid_cols: int
    ) -> List[Tuple[int, int]]:
        target_row = config.target_row
        target_col = config.target_col
        target_rows = config.target_rows
        target_cols = config.target_cols

        if target_row is not None:
            assert 0 <= target_row < grid_rows, (
                f"target_row={target_row} invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_rows - 1}"
            )
        if target_col is not None:
            assert 0 <= target_col < grid_cols, (
                f"target_col={target_col} invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_cols - 1}"
            )
        if target_rows is not None:
            for tr in target_rows:
                assert 0 <= tr < grid_rows, (
                    f"target_rows contains {tr} which is invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_rows - 1}"
                )
        if target_cols is not None:
            for tc in target_cols:
                assert 0 <= tc < grid_cols, (
                    f"target_cols contains {tc} which is invalid for {grid_rows}×{grid_cols} grid. Valid range: 0-{grid_cols - 1}"
                )

        if all(x is None for x in [target_row, target_col, target_rows, target_cols]):
            return [(r, c) for r in range(grid_rows) for c in range(grid_cols)]

        effective_rows = (
            target_rows
            if target_rows is not None
            else ([target_row] if target_row is not None else None)
        )
        effective_cols = (
            target_cols
            if target_cols is not None
            else ([target_col] if target_col is not None else None)
        )

        if effective_rows is not None and effective_cols is not None:
            return [(r, c) for r in effective_rows for c in effective_cols]
        elif effective_rows is not None:
            return [(r, c) for r in effective_rows for c in range(grid_cols)]
        elif effective_cols is not None:
            return [(r, c) for r in range(grid_rows) for c in effective_cols]

        return [(r, c) for r in range(grid_rows) for c in range(grid_cols)]

    def _validate_facet_grid_against_existing(
        self, new_rows: int, new_cols: int
    ) -> None:
        if not self._has_existing_plots():
            return

        current_rows = self.rows
        current_cols = self.cols

        assert new_rows == current_rows and new_cols == current_cols, (
            f"Computed facet grid {new_rows}×{new_cols} conflicts with existing FigureManager grid {current_rows}×{current_cols}. "
            f"Cannot change grid dimensions when plots already exist."
        )

    def _set_facet_grid_info(self, grid_info: Dict[str, Any]) -> None:
        self._facet_grid_info = grid_info

    def _has_existing_plots(self) -> bool:
        if self.external_mode:
            ax = self.axes
            return bool(ax.get_children())

        if hasattr(self.axes, "flat"):
            axes_to_check = self.axes.flat
        elif hasattr(self.axes, "__iter__") and not isinstance(self.axes, str):
            axes_to_check = self.axes
        else:
            axes_to_check = [self.axes]

        for ax in axes_to_check:
            if ax.get_children():
                return True
        return False

    def _resolve_faceting_config(
        self, faceting: Optional[FacetingConfig], **kwargs
    ) -> FacetingConfig:
        if faceting is None:
            return FacetingConfig(**kwargs)

        config_dict = {k: v for k, v in faceting.__dict__.items()}
        for key, value in kwargs.items():
            if hasattr(FacetingConfig, key) and value is not None:
                config_dict[key] = value

        has_rows = config_dict.get("rows") is not None
        has_cols = config_dict.get("cols") is not None
        has_ncols = config_dict.get("ncols") is not None
        has_nrows = config_dict.get("nrows") is not None

        if has_rows and has_cols and (has_ncols or has_nrows):
            config_dict["ncols"] = None
            config_dict["nrows"] = None

        return FacetingConfig(**config_dict)

    def plot_faceted(
        self,
        data: pd.DataFrame,
        plot_type: str,
        faceting: Optional[FacetingConfig] = None,
        **kwargs,
    ) -> None:
        assert isinstance(data, pd.DataFrame), (
            f"data must be DataFrame, got {type(data)}"
        )
        assert isinstance(plot_type, str), (
            f"plot_type must be string, got {type(plot_type)}"
        )

        config = self._resolve_faceting_config(faceting, **kwargs)
        config.validate()

        grid_rows, grid_cols, layout_metadata = self._compute_facet_grid(data, config)
        self._validate_facet_grid_against_existing(grid_rows, grid_cols)
        target_positions = self._resolve_targeting(config, grid_rows, grid_cols)

        self._set_facet_grid_info(
            {
                "config": config,
                "grid_dimensions": (grid_rows, grid_cols),
                "layout_metadata": layout_metadata,
                "target_positions": target_positions,
            }
        )

        self._debug_grid_info = {
            "config": config,
            "grid_dimensions": (grid_rows, grid_cols),
            "layout_metadata": layout_metadata,
            "target_positions": target_positions,
        }

        print(
            f"Grid computed: {grid_rows}×{grid_cols}, targeting {len(target_positions)} positions"
        )

    def plot(
        self, plot_type: str, row: int, col: int, *args: Any, **kwargs: Any
    ) -> None:
        plotter_class = BasePlotter.get_plotter(plot_type)
        self._add_plot(plotter_class, args, row, col, **kwargs)
