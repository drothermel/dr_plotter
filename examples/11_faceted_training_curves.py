"""
Faceted Training Curves Example

Requires DataDecide integration:
    uv add "dr_plotter[datadec]"

This example demonstrates advanced faceted plotting with real ML training data.
"""

from typing import List, Tuple
import argparse
import itertools
import pandas as pd
import matplotlib.pyplot as plt
from dr_plotter.figure_manager import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.legend_manager import LegendConfig
from dr_plotter.positioning_calculator import PositioningConfig
from dr_plotter.theme import Theme, PlotStyles, AxesStyles, FigureStyles, BASE_THEME
from dr_plotter import consts
from dr_plotter.scripting.datadec_utils import get_datadec_functions
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import inspect_plot_properties

# Get DataDecide functions once at module level
DataDecide, select_params, select_data = get_datadec_functions()


def load_and_prepare_data() -> pd.DataFrame:
    """Load clean, pre-validated data from DataDecide."""
    dd = DataDecide()
    return dd.get_filtered_df(filter_types=["max_steps"], return_means=True)


def create_faceted_training_curves_theme(
    x_log: bool = False, y_log: bool = False, model_sizes: List[str] = None
) -> Theme:
    model_sizes = select_params(model_sizes or "all")

    color_palette = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#aec7e8",
        "#ffbb78",
        "#98df8a",
        "#ff9896",
    ]

    return Theme(
        name="faceted_training_curves",
        parent=BASE_THEME,
        plot_styles=PlotStyles(
            linewidth=1.5,
            alpha=0.8,
        ),
        axes_styles=AxesStyles(
            grid_alpha=0.3,
            label_fontsize=11,
            legend_fontsize=9,
            xscale="log" if x_log else "linear",
            yscale="log" if y_log else "linear",
        ),
        figure_styles=FigureStyles(
            title_fontsize=10,
        ),
        **{
            consts.get_cycle_key("hue"): itertools.cycle(
                color_palette[: len(model_sizes)]
            ),
        },
    )


def subset_data_for_plotting(
    df: pd.DataFrame, target_recipes: List[str], model_sizes: List[str]
) -> pd.DataFrame:
    """Filter DataFrame for target metrics, recipes, and model sizes."""
    target_metrics = ["pile-valppl", "mmlu_average_correct_prob"]

    # DataDecide guarantees these columns exist, but filter for what we need
    filtered_df = df[
        df["data"].isin(target_recipes) & df["params"].isin(model_sizes)
    ].copy()

    keep_columns = ["params", "data", "step"] + target_metrics
    filtered_df = filtered_df[keep_columns].copy()

    # Set up categorical ordering for consistent plotting
    filtered_df["params"] = pd.Categorical(
        filtered_df["params"], categories=model_sizes, ordered=True
    )
    filtered_df["data"] = pd.Categorical(
        filtered_df["data"], categories=target_recipes, ordered=True
    )
    filtered_df = filtered_df.sort_values(["params", "data", "step"])

    return filtered_df


@inspect_plot_properties()
def plot_training_curves(
    df: pd.DataFrame,
    target_recipes: List[str],
    args: argparse.Namespace,
    x_log: bool = False,
    y_log: bool = False,
    xlim: Tuple[float, float] = None,
    ylim: Tuple[float, float] = None,
) -> plt.Figure:
    num_model_sizes = len(df["params"].cat.categories)
    custom_theme = create_faceted_training_curves_theme(x_log=x_log, y_log=y_log)
    figwidth = max(12, len(target_recipes) * 3.5)

    with FigureManager(
        figure=FigureConfig(
            rows=2,
            cols=len(target_recipes),
            figsize=(figwidth, 9),
            tight_layout_pad=0.3,
            subplot_kwargs={"sharey": "row"},
        ),
        legend=LegendConfig(
            strategy="figure",
            ncol=min(num_model_sizes, 8),
            layout_top_margin=0.1,
            layout_bottom_margin=0.12,
            positioning_config=PositioningConfig(legend_y_offset_factor=0.02),
        ),
        theme=custom_theme,
    ) as fm:
        fm.fig.suptitle(
            f"Faceted Training Curves: 2 Metrics × {len(target_recipes)} Data Recipes",
            fontsize=16,
            y=0.96,
        )

        metrics = ["pile-valppl", "mmlu_average_correct_prob"]
        metric_labels = [
            "Pile Validation Perplexity",
            "MMLU Average Correct Probability",
        ]

        for col_idx, recipe in enumerate(target_recipes):
            recipe_data = df[df["data"] == recipe].copy()

            for row_idx, (metric, metric_label) in enumerate(
                zip(metrics, metric_labels)
            ):
                # DataDecide provides clean data, minimal processing needed
                metric_data = recipe_data[["params", "step", metric]].copy()

                # Remove NaN values to prevent gaps in lines
                metric_data = metric_data.dropna(subset=[metric])

                if len(metric_data) == 0:
                    continue

                fm.plot(
                    "line",
                    row_idx,
                    col_idx,
                    metric_data,
                    x="step",
                    y=metric,
                    hue_by="params",
                    linewidth=1.5,
                    alpha=0.8,
                    title=f"{recipe}",
                )

                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == 1:
                    ax.set_xlabel("Training Steps")

                if col_idx == 0:
                    ax.set_ylabel(metric_label)

                theme_x_scale = custom_theme.axes_styles.get("xscale", "linear")
                theme_y_scale = custom_theme.axes_styles.get("yscale", "linear")

                if theme_x_scale == "log":
                    ax.set_xscale("log")
                else:
                    ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))

                if theme_y_scale == "log":
                    ax.set_yscale("log")

                if xlim:
                    ax.set_xlim(xlim)

                if ylim:
                    ax.set_ylim(ylim)

        # Store figure reference before exiting context
        figure = fm.fig

    plt.tight_layout()
    show_or_save_plot(figure, args, "11_faceted_training_curves")

    return figure


def create_arg_parser() -> argparse.ArgumentParser:
    parser = setup_arg_parser("Faceted Training Curves - 2 Metrics × N Data Recipes")
    parser.add_argument(
        "--x-log", action="store_true", help="Use log scale for X-axis (training steps)"
    )
    parser.add_argument(
        "--y-log", action="store_true", help="Use log scale for Y-axis (metric values)"
    )
    parser.add_argument(
        "--save", action="store_true", help="Save plot instead of displaying"
    )

    # Filtering and ordering
    parser.add_argument(
        "--recipes",
        nargs="+",
        default=["C4", "Dolma1.7", "FineWeb-Edu", "DCLM-Baseline"],
        help="Data recipes to include (in order for subplot columns)",
    )
    parser.add_argument(
        "--model-sizes",
        nargs="+",
        default=["10M", "14M", "16M"],
        help="Model sizes to include (in order for line styling). Use 'all' for all available.",
    )

    # Axis limits
    parser.add_argument(
        "--xlim", nargs=2, type=float, metavar=("MIN", "MAX"), help="X-axis limits"
    )
    parser.add_argument(
        "--ylim", nargs=2, type=float, metavar=("MIN", "MAX"), help="Y-axis limits"
    )

    return parser


def main() -> None:
    parser = create_arg_parser()
    args = parser.parse_args()

    print("Loading and preparing data...")
    df = load_and_prepare_data()
    print(f"Loaded {len(df):,} rows")

    # Validate CLI arguments using DataDecide utilities
    validated_recipes = select_data(args.recipes)
    validated_model_sizes = select_params(args.model_sizes)

    print("Filtering data for target metrics, recipes, and model sizes...")
    filtered_df = subset_data_for_plotting(df, validated_recipes, validated_model_sizes)
    print(f"Filtered to {len(filtered_df):,} rows")

    print(f"Model sizes (in order): {validated_model_sizes}")
    print(f"Data recipes (in order): {validated_recipes}")

    config_info = []
    if args.x_log:
        config_info.append("X-log")
    if args.y_log:
        config_info.append("Y-log")
    if args.xlim:
        config_info.append(f"xlim={args.xlim}")
    if args.ylim:
        config_info.append(f"ylim={args.ylim}")
    config_desc = " + ".join(config_info) if config_info else "default settings"

    print(f"Creating faceted training curves visualization with {config_desc}...")
    figure = plot_training_curves(
        filtered_df,
        validated_recipes,
        args,
        x_log=args.x_log,
        y_log=args.y_log,
        xlim=args.xlim,
        ylim=args.ylim,
    )
    print("Visualization complete!")


if __name__ == "__main__":
    main()
