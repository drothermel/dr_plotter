from typing import Any

from dr_plotter.scripting import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties


@inspect_plot_properties()
def main(args: Any) -> Any:
    line_data = ExampleData.time_series(periods=50, seed=102)
    assert "time" in line_data.columns
    assert "value" in line_data.columns

    plot_config = PlotConfig(
        layout={"rows": 1, "cols": 1, "figsize": (8.0, 6.0)},
        style={"plot_styles": {"linewidth": 2.0, "alpha": 0.9}, "theme": "line"},
        legend={"strategy": "subplot", "position": "lower center"},
    )

    with FigureManager(plot_config) as fm:
        fm.plot(
            line_data,
            "line",
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
