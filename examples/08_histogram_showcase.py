"""
Example 8: Histogram Showcase - All histogram features.
Demonstrates single and multiple distribution histograms.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Histogram Showcase")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(12, 10)) as fm:
        fm.fig.suptitle("Histogram Showcase: Distribution Visualization", fontsize=16)

        # Basic histogram
        basic_data = ExampleData.distribution_data()
        fm.plot(
            "histogram", 0, 0, basic_data, "values", bins=20, title="Basic Histogram"
        )

        # Density histogram
        fm.plot(
            "histogram",
            0,
            1,
            basic_data,
            "values",
            bins=20,
            density=True,
            title="Density Histogram",
        )

        # Multiple distributions
        multi_data = ExampleData.distribution_data(distributions=3)
        fm.plot(
            "histogram",
            1,
            0,
            multi_data,
            "value",
            hue_by="distribution",
            bins=20,
            title="Multiple Distributions",
            alpha=0.7,
        )

        # Custom styling
        fm.plot(
            "histogram",
            1,
            1,
            basic_data,
            "values",
            bins=30,
            title="Custom Styling",
            color="red",
            alpha=0.6,
        )

        show_or_save_plot(fm.fig, args, "08_histogram_showcase")
