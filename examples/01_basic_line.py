from typing import Any

from plot_data import ExampleData

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties


@inspect_plot_properties()
def main(args: Any) -> Any:
    line_data = ExampleData.time_series(periods=50, seed=102)
    assert "time" in line_data.columns
    assert "value" in line_data.columns

    with FigureManager(
        PlotConfig(layout={"rows": 1, "cols": 1, "figsize": (5, 5)})
    ) as fm:
        fm.plot(
            "line",
            0,
            1,
            line_data,
            x="time",
            y="value",
            linewidth=2,
            alpha=0.9,
            title="Basic Time Series",
        )

    show_or_save_plot(fm.fig, args, "01_basic_functionality")
    return fm.fig  # used for decorators


if __name__ == "__main__":
    parser = setup_arg_parser(description="Basic Functionality Example")
    args = parser.parse_args()
    main(args)
