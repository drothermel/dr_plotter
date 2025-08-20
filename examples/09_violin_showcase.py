"""
Example 9: Violin Plot Showcase - All violin plot features.
Demonstrates single and grouped violin plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Violin Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Violin Plot Showcase: Distribution Shapes", fontsize=16)

        # Simple violin plot
        simple_data = ExampleData.categorical_data()
        fm.violin(
            0, 0, simple_data, x="category", y="value", title="Simple Violin Plot"
        )

        # Grouped violin plot
        grouped_data = ExampleData.grouped_categories()
        fm.violin(
            0,
            1,
            grouped_data,
            x="category",
            y="value",
            hue_by="group",
            title="Grouped Violin Plot",
        )

        show_or_save_plot(fm.fig, args, "09_violin_showcase")
