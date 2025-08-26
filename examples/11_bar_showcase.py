"""
Example 11: Bar Plot Showcase - All bar plot features.
Demonstrates single and grouped bar plots.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example, verify_plot_properties
from plot_data import ExampleData

EXPECTED_CHANNELS = {
    (0, 0): [],
    (0, 1): ["hue"],
}


@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=2,
    verify_legend_consistency=True,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"legend_count": 1},
        (0, 1): {"hue": 2},
    },
)
def main(args):
    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Bar Plot Showcase: Single and Grouped Bars", fontsize=16)

        # Simple bar chart
        simple_data = ExampleData.categorical_data()
        simple_summary = simple_data.groupby("category")["value"].mean().reset_index()
        fm.plot(
            "bar",
            0,
            0,
            simple_summary,
            x="category",
            y="value",
            label="Category Values",
            title="Simple Bar Chart",
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
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Bar Plot Showcase")
    args = parser.parse_args()
    main(args)
