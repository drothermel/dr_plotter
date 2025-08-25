from typing import Any
from dr_plotter.figure import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example, verify_plot_properties
from plot_data import ExampleData

EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue"],
    (1, 0): ["hue"],
    (1, 1): ["hue"],
}


@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=1,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 4},
        (0, 1): {"hue": 4},
        (1, 0): {"hue": 4},
        (1, 1): {"hue": 4},
    },
)
def main(args: Any) -> Any:
    shared_data = ExampleData.get_legend_positioning_data()

    assert "category_group" in shared_data.columns
    assert "performance" in shared_data.columns
    assert "accuracy" in shared_data.columns
    assert len(shared_data.groupby("category_group")) == 4

    with FigureManager(
        rows=2,
        cols=2,
        figsize=(16, 12),
        legend_strategy="figure_below",
        legend_position="lower center",
        legend_ncol=4,
    ) as fm:
        fm.fig.suptitle(
            "Example 10: Legend Positioning + Management - Shared Figure Legend",
            fontsize=16,
        )

        fm.plot(
            "scatter",
            0,
            0,
            shared_data,
            x="performance",
            y="accuracy",
            hue_by="category_group",
            s=60,
            alpha=0.8,
            title="Scatter: Contributing to Shared Legend",
        )

        fm.plot(
            "line",
            0,
            1,
            shared_data.sort_values("performance"),
            x="performance",
            y="accuracy",
            hue_by="category_group",
            linewidth=2,
            alpha=0.8,
            title="Line: Contributing to Shared Legend",
        )

        fm.plot(
            "scatter",
            1,
            0,
            shared_data,
            x="runtime",
            y="memory",
            hue_by="category_group",
            s=60,
            alpha=0.8,
            title="Scatter Alt: Contributing to Shared Legend",
        )

        fm.plot(
            "scatter",
            1,
            1,
            shared_data,
            x="performance",
            y="accuracy",
            hue_by="category_group",
            s=60,
            alpha=0.8,
            legend=False,
            title="No Legend: Grouping Without Legend Display",
        )

    show_or_save_plot(fm.fig, args, "10_legend_positioning")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(
        description="Legend Positioning + Management - Legend System Robustness"
    )
    args = parser.parse_args()
    main(args)
