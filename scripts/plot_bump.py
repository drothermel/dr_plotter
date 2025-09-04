#!/usr/bin/env python3

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.datadec_utils import get_datadec_functions, prepare_plot_data


def format_perplexity(ppl_value: float) -> str:
    return f"{ppl_value:.2f}"


def add_value_annotations(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    # Create mapping from model size names to numeric positions for x-axis
    time_points = sorted(bump_data["time"].unique())
    time_to_x = {time_point: idx for idx, time_point in enumerate(time_points)}

    # Get the ranking data that BumpPlotter created (inverted y-axis, rank 1 at top)
    ranked_data = []
    for time_point in time_points:
        time_data = bump_data[bump_data["time"] == time_point].copy()
        time_data = time_data.sort_values("score", ascending=False)
        time_data["rank"] = range(1, len(time_data) + 1)
        ranked_data.append(time_data)

    all_ranked_data = pd.concat(ranked_data, ignore_index=True)

    # Add annotations for each point
    for _, row in all_ranked_data.iterrows():
        x_pos = time_to_x[row["time"]]
        y_pos = row["rank"]  # Rank position (1 = top)
        ppl_text = format_perplexity(row["original_ppl"])

        # Position text slightly above and to the right of each point
        ax.annotate(
            ppl_text,
            xy=(x_pos, y_pos),  # Point location
            xytext=(5, 8),  # Offset: 5 pixels right, 8 pixels up
            textcoords="offset points",
            fontsize=8,
            ha="left",
            va="bottom",
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "white",
                "alpha": 0.8,
                "edgecolor": "gray",
            },
            arrowprops=None,  # No arrow, just floating text
        )


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot bump chart rankings for datadecide"
    )

    parser.add_argument(
        "metric",
        default="pile-valppl",
        nargs="?",
        help="Metric to plot for ranking comparison (default: pile-valppl)",
    )

    parser.add_argument(
        "--params",
        nargs="+",
        default=["all"],
        help="Param sizes (e.g., 150M 300M 1B) or 'all'",
    )

    parser.add_argument(
        "--data",
        nargs="+",
        default=["all"],
        help="Data recipes to include or 'all' for all available",
    )

    parser.add_argument(
        "--exclude-params",
        nargs="+",
        default=[],
        help="Model parameter sizes to exclude when using 'all'",
    )

    parser.add_argument(
        "--exclude-data",
        nargs="+",
        default=[],
        help="Data recipes to exclude when using 'all'",
    )

    parser.add_argument("--save", type=str, help="Save plot to file (specify path)")
    parser.add_argument(
        "--no-show", action="store_true", help="Don't display plot interactively"
    )

    parser.add_argument(
        "--figsize",
        nargs=2,
        type=float,
        default=[12, 8],
        help="Figure size width height (default: 12 8)",
    )

    return parser


def plot_bump(
    metric: str = "pile-valppl",
    params: list[str] | None = None,
    data: list[str] | None = None,
    exclude_params: list[str] | None = None,
    exclude_data: list[str] | None = None,
    save_path: str | None = None,
    show_plot: bool = True,
    figsize: tuple[float, float] = (12, 8),
) -> None:
    DataDecide, select_params, select_data = get_datadec_functions()

    exclude_params = exclude_params or []
    exclude_data = exclude_data or []

    # Handle "all" values and exclusions
    if params is None or (len(params) == 1 and params[0] == "all"):
        params = select_params("all", exclude=exclude_params)
    if data is None or (len(data) == 1 and data[0] == "all"):
        data = select_data("all", exclude=exclude_data)

    dd = DataDecide()
    metrics = [metric]

    print(f"Preparing data for recipes: {data}")
    print(f"Model sizes: {params}")
    print(f"Metric: {metrics}")

    # Get training curve data (not aggregated for bump plot temporal dimension)
    df = prepare_plot_data(dd, params, data, metrics, aggregate_seeds=True)

    print(f"\nData after prepare_plot_data: {df.shape}")
    print(f"Unique params in df: {sorted(df['params'].unique())}")
    print(f"Unique data in df: {sorted(df['data'].unique())}")
    print(f"Step range: {df['step'].min()} to {df['step'].max()}")

    # Debug: Check what's happening with the final step filtering
    print("\nDebugging final step selection:")
    print(f"Max step globally: {df['step'].max()}")
    print("Step distribution by params:")
    step_by_params = df.groupby("params")["step"].agg(["min", "max", "count"])
    print(step_by_params)

    # The issue: different model sizes have different max steps!
    # We need to use the final available step for each model size
    final_step_per_params = df.groupby("params")["step"].max().reset_index()
    print("\nFinal step per model size:")
    print(final_step_per_params)

    # Get final performance for each (params, data) combination
    final_rows = []
    for params_size in df["params"].unique():
        params_df = df[df["params"] == params_size]
        max_step_for_params = params_df["step"].max()
        final_step_data = params_df[params_df["step"] == max_step_for_params]
        final_rows.append(final_step_data)

    final_step_df = pd.concat(final_rows, ignore_index=True)
    print(f"\nFinal step df shape: {final_step_df.shape}")
    print(f"Params in final step df: {sorted(final_step_df['params'].unique())}")

    # Create bump plot data while preserving original values for labels
    bump_data = final_step_df.rename(
        columns={
            "params": "time",  # Model sizes become time dimension
            "data": "category",  # Recipes become categories (trajectories)
            "value": "score",  # Performance values (lower is better for perplexity)
        }
    )[["time", "category", "score"]]

    # Keep original perplexity values for labeling (before inversion)
    bump_data["original_ppl"] = bump_data["score"].copy()

    bump_data["score"] = -bump_data["score"]
    metric_str = metric.replace("_", " ").replace("-", " ").title()

    print("\nBump plot data preview:")
    print(bump_data.head(10))
    print(f"\nBump data shape: {bump_data.shape}")
    print(f"Categories (recipes): {sorted(bump_data['category'].unique())}")
    print(f"Time points (model sizes): {sorted(bump_data['time'].unique())}")

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,
                "cols": 1,
                "figsize": figsize,
            }
        )
    ) as fm:
        fm.plot(
            "bump",
            0,
            0,
            bump_data,
            time_col="time",
            value_col="score",
            category_col="category",
            marker="o",
            linewidth=2,
            title=f"Data Recipe Rankings Across Model Sizes ({metric_str})",
        )

        # Add perplexity value annotations over each point
        ax = fm.get_axes(0, 0)
        add_value_annotations(ax, bump_data)

        # Add annotation style label positioned below the highest ranking line (rank 1)
        # Position it at y=1.5 (between rank 1 and rank 2) to avoid collision
        metric_label = metric_str + " Values"
        ax.text(
            0.02,
            1.5,
            metric_label,
            fontsize=8,
            ha="left",
            va="center",
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "white",
                "alpha": 0.8,
                "edgecolor": "gray",
            },
        )

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Plot saved to: {save_path}")

    if show_plot:
        plt.show()

    if not show_plot and not save_path:
        print("Warning: Plot not saved or displayed. Use --save or remove --no-show")


def main() -> None:
    parser = create_arg_parser()
    args = parser.parse_args()

    show_plot = not args.no_show
    figsize = tuple(args.figsize)

    plot_bump(
        metric=args.metric,
        params=args.params,
        data=args.data,
        exclude_params=args.exclude_params,
        exclude_data=args.exclude_data,
        save_path=args.save,
        show_plot=show_plot,
        figsize=figsize,
    )


if __name__ == "__main__":
    main()
