"""
Example 16: Color Coordination - Cross-subplot consistency.
Demonstrates consistent colors across multiple subplots using FigureManager.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Color Coordination Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle(
            "Color Coordination: Consistent Colors Across Subplots", fontsize=16
        )

        # Use the same grouped data across all plots
        grouped_data = ExampleData.time_series_grouped()

        # All plots use the same hue variable, so colors should be consistent
        fm.plot(
            "line", 0, 0, grouped_data, "time", "value", hue_by="group", title="Line Plot"
        )

        fm.plot(
            "scatter",
            0,
            1,
            grouped_data,
            "time",
            "value",
            hue_by="group",
            title="Scatter Plot",
        )

        # Bar plot version (aggregate the data first)
        bar_data = grouped_data.groupby("group")["value"].mean().reset_index()
        fm.plot("bar", 1, 0, bar_data, "group", "value", hue_by="group", title="Bar Plot")

        # Violin plot
        fm.plot(
            "violin",
            1,
            1,
            grouped_data,
            "group",
            "value",
            hue_by="group",
            title="Violin Plot",
        )

        show_or_save_plot(fm.fig, args, "16_color_coordination")
