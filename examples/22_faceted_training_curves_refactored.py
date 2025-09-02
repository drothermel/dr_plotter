from typing import List, Tuple
import argparse
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
from dr_plotter.figure_manager import FigureManager
from dr_plotter.plot_config import PlotConfig
from dr_plotter.scripting.datadec_utils import get_datadec_functions

DataDecide, select_params, select_data = get_datadec_functions()


def load_and_prepare_data() -> pd.DataFrame:
    try:
        dd = DataDecide()
        return dd.full_eval
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)


def prepare_faceted_data(
    df: pd.DataFrame, target_recipes: List[str], model_sizes: List[str]
) -> pd.DataFrame:
    target_metrics = ["pile-valppl", "mmlu_average_acc_raw"]

    # Filter for target recipes and model sizes
    filtered_df = df[
        df["data"].isin(target_recipes) & df["params"].isin(model_sizes)
    ].copy()

    keep_columns = ["params", "data", "step"] + target_metrics
    filtered_df = filtered_df[keep_columns].copy()

    # Melt from wide to long format for faceting
    melted_df = filtered_df.melt(
        id_vars=["params", "data", "step"],
        value_vars=target_metrics,
        var_name="metric",
        value_name="value",
    )

    # Remove NaN values to prevent line discontinuities
    melted_df = melted_df.dropna(subset=["value"])

    # Set up categorical ordering for consistent plotting
    melted_df["params"] = pd.Categorical(
        melted_df["params"], categories=model_sizes, ordered=True
    )
    melted_df["data"] = pd.Categorical(
        melted_df["data"], categories=target_recipes, ordered=True
    )

    # Create nice metric labels
    metric_label_map = {
        "pile-valppl": "Pile Validation Perplexity",
        "mmlu_average_acc_raw": "MMLU Average Accuracy",
    }
    melted_df["metric_label"] = melted_df["metric"].map(metric_label_map)

    melted_df = melted_df.sort_values(["metric", "data", "params", "step"])

    return melted_df


def plot_training_curves_faceted(
    df: pd.DataFrame,
    target_recipes: List[str],
    x_log: bool = False,
    y_log: bool = False,
    xlim: Tuple[float, float] = None,
    ylim: Tuple[float, float] = None,
) -> None:
    figwidth = max(12, len(target_recipes) * 3.5)

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 2,  # 2 metrics
                "cols": len(target_recipes),  # N recipes
                "figsize": (figwidth, 9),
                "tight_layout_pad": 0.3,
                "subplot_kwargs": {"sharey": "row"},
            },
            legend={
                "strategy": "figure",
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"Faceted Training Curves: 2 Metrics × {len(target_recipes)} Data Recipes",
            fontsize=16,
            y=0.96,
        )

        # Here's the magic: replace 95+ lines of manual loops with a single faceted call!
        fm.plot_faceted(
            data=df,
            plot_type="line",
            rows="metric",  # Facet metrics across rows
            cols="data",  # Facet recipes across columns
            lines="params",  # Model sizes get different colors
            x="step",
            y="value",
            linewidth=1.5,
            alpha=0.8,
        )

        # Apply custom formatting to each subplot
        for row_idx in range(2):  # 2 metrics
            for col_idx in range(len(target_recipes)):  # N recipes
                ax = fm.get_axes(row_idx, col_idx)

                # Set labels and titles
                if row_idx == 1:  # Bottom row
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:  # Left column
                    # Get the metric for this row
                    metrics = df["metric"].unique()
                    if row_idx < len(metrics):
                        metric = metrics[row_idx]
                        metric_label = df[df["metric"] == metric]["metric_label"].iloc[
                            0
                        ]
                        ax.set_ylabel(metric_label)
                else:
                    ax.set_ylabel("")

                # Set recipe title
                recipe = target_recipes[col_idx]
                if row_idx == 0:  # Top row only
                    ax.set_title(recipe, pad=10)

                # Apply axis formatting
                if x_log:
                    ax.set_xscale("log")
                else:
                    ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))

                if y_log:
                    ax.set_yscale("log")

                if xlim:
                    ax.set_xlim(xlim)

                if ylim:
                    ax.set_ylim(ylim)

                ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        "plots/07_faceted_training_curves_refactored.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.show()
    time.sleep(5)
    plt.close()


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Faceted Training Curves (Refactored) - Using dr_plotter faceting system"
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
        validated_recipes = select_data(args.recipes)
        validated_model_sizes = select_params(args.model_sizes)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Preparing data for faceted plotting...")
    faceted_df = prepare_faceted_data(df, validated_recipes, validated_model_sizes)
    print(f"Melted to {len(faceted_df):,} rows for faceting")

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
    print("✨ Using the new dr_plotter faceting system - watch the magic!")

    plot_training_curves_faceted(
        faceted_df,
        validated_recipes,
        x_log=args.x_log,
        y_log=args.y_log,
        xlim=args.xlim,
        ylim=args.ylim,
    )
    print("Visualization complete!")
    print("🎉 Reduced from 95+ lines to ~15 lines of core plotting code!")


if __name__ == "__main__":
    main()
