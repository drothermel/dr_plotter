from typing import Any
from dr_plotter.figure import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example, verify_plot_properties
from plot_data import ExampleData

EXPECTED_CHANNELS = {
    (0, 0): ["hue", "marker"],
    (0, 1): ["hue", "marker"],
}


@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=2,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 2, "marker": 2},
        (0, 1): {"hue": 2, "marker": 2},
    },
)
def main(args: Any) -> Any:
    complex_data = ExampleData.get_cross_groupby_legends_data()

    filtered_data = complex_data[complex_data["experiment"].isin(["Exp_A", "Exp_B"])]
    time_series_data = ExampleData.experiment_time_series()

    assert "experiment" in filtered_data.columns
    assert "condition" in filtered_data.columns
    assert "algorithm" in filtered_data.columns
    assert "performance" in filtered_data.columns
    assert "accuracy" in filtered_data.columns
    assert len(filtered_data.groupby("experiment")) == 2
    assert len(filtered_data.groupby("condition")) == 2
    assert len(filtered_data.groupby("algorithm")) == 3

    with FigureManager(
        rows=1,
        cols=2,
        figsize=(16, 6),
        legend_strategy="split",
        legend_bottom_margin=0.2,
        legend_y_offset=0.2,
        legend_max_col=2,
    ) as fm:
        fm.fig.suptitle(
            "Example 9: Cross Group-By + Legend Types - Split Legend System",
            fontsize=16,
        )

        fm.plot(
            "scatter",
            0,
            0,
            filtered_data,
            x="performance",
            y="accuracy",
            hue_by="experiment",
            marker_by="condition",
            s=60,
            alpha=0.7,
            title="Scatter: Experiment (Hue) × Condition (Marker)",
        )

        fm.plot(
            "line",
            0,
            1,
            time_series_data,
            x="time_point",
            y="performance",
            hue_by="experiment",
            marker_by="condition",
            linewidth=2,
            alpha=0.8,
            title="Line: Experiment (Hue) × Condition (Marker)",
        )

    show_or_save_plot(fm.fig, args, "09_cross_groupby_legends")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(
        description="Cross Group-By + Legend Types - Multi-Channel Visual Encoding"
    )
    args = parser.parse_args()
    main(args)
