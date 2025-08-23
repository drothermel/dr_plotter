"""
Example 1: Quickstart - Simplest possible usage.
Shows the absolute minimal code needed to create a plot.
"""

import dr_plotter.api as drp
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example
from plot_data import ExampleData


@verify_example(expected_legends=0)
def main(args):
    # Get some simple data
    data = ExampleData.simple_scatter()

    # Create a plot - that's it!
    fig, ax = drp.scatter(data, x="x", y="y", title="Quickstart Scatter Plot")

    show_or_save_plot(fig, args, "01_quickstart")
    return fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Quickstart Example")
    args = parser.parse_args()
    main(args)
