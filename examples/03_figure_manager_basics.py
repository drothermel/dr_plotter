"""
Example 3: FigureManager Basics - Multi-subplot layouts.
Shows how to create complex figures with multiple subplots using FigureManager.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="FigureManager Basics Example")
    args = parser.parse_args()

    # Create a 2x2 figure
    with FigureManager(rows=2, cols=2, figsize=(12, 10)) as fm:
        fm.fig.suptitle("FigureManager: Multi-Subplot Layout", fontsize=16)

        # Top left: Scatter plot
        scatter_data = ExampleData.simple_scatter()
        fm.scatter(0, 0, scatter_data, x="x", y="y", title="Scatter Plot")

        # Top right: Line plot
        line_data = ExampleData.time_series()
        fm.line(0, 1, line_data, x="time", y="value", title="Line Plot")

        # Bottom left: Bar plot
        bar_data = ExampleData.categorical_data()
        bar_summary = bar_data.groupby("category")["value"].mean().reset_index()
        fm.bar(1, 0, bar_summary, x="category", y="value", title="Bar Plot")

        # Bottom right: Histogram
        hist_data = ExampleData.distribution_data()
        fm.hist(1, 1, hist_data, x="values", title="Histogram")

        show_or_save_plot(fm.fig, args, "03_figure_manager_basics")
