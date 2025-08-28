"""
Themed Faceted Training Curves Example

Requires DataDecide integration:
    uv add "dr_plotter[datadec]"

This example demonstrates advanced themed faceted plotting with real ML training data.
"""

from typing import List, Tuple
import argparse
import itertools
import sys
import pandas as pd
import matplotlib.pyplot as plt
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.legend_manager import LegendConfig, LegendStrategy
from dr_plotter.theme import Theme, PlotStyles, AxesStyles, FigureStyles, BASE_THEME
from dr_plotter.scripting.datadec_utils import get_clean_datadec_df, validate_cli_params, validate_cli_data


def load_and_prepare_data() -> pd.DataFrame:
    """Load clean, pre-validated data from DataDecide."""
    try:
        return get_clean_datadec_df(filter_types=["ppl", "max_steps"])
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)




def create_faceted_training_curves_theme(
    x_log: bool = False, y_log: bool = False, model_sizes: List[str] = None
) -> Theme:
    if model_sizes is None:
        # Default model sizes - will be overridden by actual data
        model_sizes = ["4M", "6M", "8M", "10M", "14M", "16M", "20M", "60M", "90M", "150M", "300M", "530M", "750M", "1B"]

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

    from dr_plotter import consts

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
    filtered_df = df[df["data"].isin(target_recipes) & df["params"].isin(model_sizes)].copy()
    
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


def plot_training_curves_themed(
    df: pd.DataFrame,
    target_recipes: List[str],
    x_log: bool = False,
    y_log: bool = False,
    xlim: Tuple[float, float] = None,
    ylim: Tuple[float, float] = None,
) -> None:
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
            strategy=LegendStrategy.FIGURE_BELOW,
            ncol=min(num_model_sizes, 8),
            layout_top_margin=0.1,
            layout_bottom_margin=0.12,
            bbox_y_offset=0.02,
        ),
        theme=custom_theme,
    ) as fm:
        fm.fig.suptitle(
            f"Themed Faceted Training Curves: 2 Metrics × {len(target_recipes)} Data Recipes",
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

    plt.tight_layout()
    plt.savefig(
        "examples/plots/06b_faceted_training_curves_themed.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.show()


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Themed Faceted Training Curves - 2 Metrics × N Data Recipes"
    )
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
        default=["all"],
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
    try:
        validated_recipes = validate_cli_data(args.recipes)
        validated_model_sizes = validate_cli_params(args.model_sizes)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)

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

    print(f"Creating custom theme with {config_desc}...")
    custom_theme = create_faceted_training_curves_theme(
        x_log=args.x_log, y_log=args.y_log, model_sizes=validated_model_sizes
    )
    print(f"Theme created: {custom_theme.name}")
    print(f"Theme plot styles: {custom_theme.plot_styles}")

    axes_info = custom_theme.axes_styles
    print(
        f"Theme axes scales: X={axes_info.get('xscale', 'linear')}, Y={axes_info.get('yscale', 'linear')}"
    )

    print(
        f"Creating themed faceted training curves visualization with {config_desc}..."
    )
    plot_training_curves_themed(
        filtered_df,
        validated_recipes,
        x_log=args.x_log,
        y_log=args.y_log,
        xlim=args.xlim,
        ylim=args.ylim,
    )
    print("Themed visualization complete!")


if __name__ == "__main__":
    main()
