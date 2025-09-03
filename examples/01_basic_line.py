from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import (
    LayoutConfig,
    LegendConfig,
    PlotConfig,
    PositioningConfig,
    StyleConfig,
)
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties


@inspect_plot_properties()
def main(args: Any) -> Any:
    line_data = ExampleData.time_series(periods=50, seed=102)
    assert "time" in line_data.columns
    assert "value" in line_data.columns

    positioning_config = PositioningConfig(
        default_margin_bottom=0.15,
        default_margin_top=0.95,
        default_margin_left=0.0,
        default_margin_right=1.0,
        legend_y_offset_factor=0.08,
        legend_spacing_base=0.35,
        legend_alignment_center=0.5,
        two_legend_positions=(0.25, 0.75),
        multi_legend_start_factor=0.15,
        title_space_factor=0.95,
        tight_layout_pad=0.5,
        wide_figure_threshold=16.0,
        medium_figure_threshold=12.0,
        wide_spacing_max=0.35,
        medium_spacing_max=0.3,
        wide_span_factor=0.8,
        medium_span_factor=0.7,
    )

    legend_config = LegendConfig(
        strategy="subplot",
        layout_hint=None,
        collect_strategy="smart",
        position="lower center",
        deduplication=True,
        ncol=None,
        max_col=4,
        spacing=0.1,
        remove_axes_legends=True,
        channel_titles=None,
        layout_left_margin=0.0,
        layout_bottom_margin=0.15,
        layout_right_margin=1.0,
        layout_top_margin=0.95,
        positioning_config=positioning_config,
    )

    layout_config = LayoutConfig(
        rows=1,
        cols=1,
        figsize=(8.0, 6.0),
        tight_layout_pad=0.5,
        figure_kwargs={},
        subplot_kwargs={},
        x_labels=None,
        y_labels=None,
    )

    style_config = StyleConfig(
        colors=None,
        plot_styles={"linewidth": 2.0, "alpha": 0.9},
        fonts=None,
        figure_styles=None,
        theme="line",
    )

    plot_config = PlotConfig(
        layout=layout_config,
        style=style_config,
        legend=legend_config,
    )

    with FigureManager(plot_config) as fm:
        fm.plot(
            "line",
            0,
            0,
            line_data,
            x="time",
            y="value",
            title="Comprehensive Configuration Example - Basic Time Series",
        )

    show_or_save_plot(fm.fig, args, "01_basic_functionality")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Basic Functionality Example")
    args = parser.parse_args()
    main(args)
