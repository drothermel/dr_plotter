"""
Example 11: Bar Plot Showcase - All bar plot features.
Demonstrates single and grouped bar plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Bar Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Bar Plot Showcase: Single and Grouped Bars", fontsize=16)

        # Simple bar chart
        simple_data = ExampleData.categorical_data()
        simple_summary = simple_data.groupby("category")["value"].mean().reset_index()
        fm.plot(
            "bar", 0, 0, simple_summary, x="category", y="value", title="Simple Bar Chart"
        )

        # Grouped bar chart
        grouped_data = ExampleData.grouped_categories()
        grouped_summary = (
            grouped_data.groupby(["category", "group"])["value"].mean().reset_index()
        )
        fm.plot(
            "bar",
            0,
            1,
            grouped_summary,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Bar Chart",
        )

        show_or_save_plot(fm.fig, args, "11_bar_showcase")
