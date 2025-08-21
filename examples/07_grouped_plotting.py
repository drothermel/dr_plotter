"""
Example 7: Grouped Plotting - Bar and violin plots with grouping.
Demonstrates the grouped plotting functionality for bar and violin plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Grouped Plotting Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Grouped Plotting: Side-by-Side Comparisons", fontsize=16)

        # Simple grouping: 2 groups for clear comparison
        simple_grouped = ExampleData.grouped_categories(n_groups=2)

        # Simple grouped bar charts
        fm.plot(
            "bar",
            0,
            0,
            simple_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="2-Group Bar Chart",
        )

        # Simple grouped violin plots
        fm.plot(
            "violin",
            0,
            1,
            simple_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="2-Group Violin Plot",
        )

        # Complex grouping: 4 groups for more complex comparison
        complex_grouped = ExampleData.grouped_categories(n_groups=4)
        fm.plot(
            "bar",
            1,
            0,
            complex_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="4-Group Bar Chart",
        )

        # Complex grouped violin plots
        fm.plot(
            "violin",
            1,
            1,
            complex_grouped,
            x="category",
            y="value",
            hue_by="group",
            title="4-Group Violin Plot",
        )

        show_or_save_plot(fm.fig, args, "07_grouped_plotting")
