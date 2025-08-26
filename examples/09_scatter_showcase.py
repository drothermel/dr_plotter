"""
Example 9: Scatter Plot Showcase - All scatter plot features.
Demonstrates all visual encoding options for scatter plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example
from plot_data import ExampleData


@verify_example(expected_legends=3)
def main(args):
    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle(
            "Scatter Plot Showcase: All Visual Encoding Options", fontsize=16
        )

        # Basic scatter
        basic_data = ExampleData.simple_scatter()
        fm.plot("scatter", 0, 0, basic_data, x="x", y="y", title="Basic Scatter")

        # Color encoding (hue)
        grouped_data = ExampleData.time_series_grouped(periods=30)
        fm.plot(
            "scatter",
            0,
            1,
            grouped_data,
            x="time",
            y="value",
            hue_by="group",
            title="Color Encoding (hue)",
        )

        # Size encoding
        complex_data = ExampleData.complex_encoding_data()
        fm.plot(
            "scatter",
            1,
            0,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            size_by="performance",
            title="Color + Size Encoding",
        )

        # Marker encoding
        fm.plot(
            "scatter",
            1,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="condition",
            marker_by="algorithm",
            title="Color + Marker Encoding",
        )

    show_or_save_plot(fm.fig, args, "09_scatter_showcase")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Scatter Plot Showcase")
    args = parser.parse_args()
    main(args)
