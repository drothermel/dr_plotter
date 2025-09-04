#!/usr/bin/env python3

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.theme import Theme, BUMP_PLOT_THEME
from dr_plotter.scripting.datadec_utils import (
    BASE_RECIPES,
    BASE_AND_QC, 
    RECIPES_WITHOUT_ABLATIONS,
    CUSTOM_RECIPE_FAMILIES,
    PPL_PERFORMANCE_RECIPE_CHUNKS,
    OLMES_PERFORMANCE_RECIPE_CHUNKS,
    get_datadec_functions, 
    prepare_plot_data
)


def format_perplexity(ppl_value: float) -> str:
    return f"{ppl_value:.2f}"


def create_extended_color_palette() -> list[str]:
    return [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
        "#c49c94", "#f7b6d3", "#c7c7c7", "#dbdb8d", "#9edae5",
        "#393b79", "#637939", "#8c6d31", "#843c39", "#7b4173",
        "#5254a3", "#8ca252", "#bd9e39", "#ad494a", "#a55194",
        "#6b6ecf", "#b5cf6b", "#e7ba52", "#d6616b", "#ce6dbd",
        "#de9ed6", "#31a354", "#756bb1", "#636363", "#969696"
    ]


def create_bump_theme_with_colors(num_categories: int) -> Theme:
    import itertools
    from dr_plotter import consts
    
    extended_colors = create_extended_color_palette()
    colors_to_use = extended_colors[:max(num_categories, len(extended_colors))]
    
    return Theme(
        name="bump_timesteps_extended", 
        parent=BUMP_PLOT_THEME,
        **{
            consts.get_cycle_key("hue"): itertools.cycle(colors_to_use),
        }
    )


def format_step_label(step: float) -> str:
    if step >= 1000:
        return f"{step/1000:.1f}k"
    else:
        return f"{int(step)}"


def add_left_ranking_labels(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    time_points = sorted(bump_data["time"].unique())
    first_time = time_points[0]
    first_time_data = bump_data[bump_data["time"] == first_time].copy()
    first_time_data = first_time_data.sort_values("score", ascending=False)
    first_time_data["rank"] = range(1, len(first_time_data) + 1)
    
    for _, row in first_time_data.iterrows():
        category_name = row["category"]
        rank = row["rank"]
        
        ax.text(
            -0.02 * (max(bump_data["time"]) - min(bump_data["time"])),
            rank,
            category_name,
            transform=ax.transData,
            fontsize=9,
            ha="right",
            va="center",
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": "lightblue",
                "alpha": 0.7,
                "edgecolor": "navy",
            },
        )


def add_value_annotations(ax: plt.Axes, bump_data: pd.DataFrame) -> None:
    time_points = sorted(bump_data["time"].unique())
    time_to_x = {time_point: time_point for time_point in time_points}

    ranked_data = []
    for time_point in time_points:
        time_data = bump_data[bump_data["time"] == time_point].copy()
        time_data = time_data.sort_values("score", ascending=False)
        time_data["rank"] = range(1, len(time_data) + 1)
        ranked_data.append(time_data)

    all_ranked_data = pd.concat(ranked_data, ignore_index=True)

    for _, row in all_ranked_data.iterrows():
        x_pos = time_to_x[row["time"]]
        y_pos = row["rank"]
        ppl_text = format_perplexity(row["original_ppl"])

        ax.annotate(
            ppl_text,
            xy=(x_pos, y_pos),
            xytext=(5, 8),
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
            arrowprops=None,
        )


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot bump chart rankings across training steps for a single model size"
    )

    parser.add_argument(
        "metric",
        default="pile-valppl",
        nargs="?",
        help="Metric to plot for ranking comparison (default: pile-valppl)",
    )

    parser.add_argument(
        "model_size",
        help="Single model size to analyze (e.g., 150M, 1B)",
    )

    parser.add_argument(
        "--data",
        nargs="+",
        default=["all"],
        help="Data recipes: 'all', 'base', 'base_qc', 'no_ablations', or specific names. Named groups: 'core_datasets', 'dolma17_variants', 'dclm_variants', 'falcon_cc_variants', 'fineweb_variants', 'mix_with_baselines', 'best_ppl', 'good_ppl', 'medium_ppl', 'poor_ppl', 'best_olmes', 'good_olmes', 'medium_olmes', 'poor_olmes'",
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
        default=[14, 8],
        help="Figure size width height (default: 14 8)",
    )

    parser.add_argument(
        "--min-step",
        type=float,
        help="Minimum training step to include (optional)",
    )

    parser.add_argument(
        "--max-step",
        type=float,
        help="Maximum training step to include (optional)",
    )

    return parser


def resolve_data_groups(data_args: list[str]) -> list[str]:
    named_groups = {
        "base": BASE_RECIPES,
        "base_qc": BASE_AND_QC,
        "no_ablations": RECIPES_WITHOUT_ABLATIONS,
        **CUSTOM_RECIPE_FAMILIES,
        **{f"{k.replace('_performance', '')}": v for k, v in PPL_PERFORMANCE_RECIPE_CHUNKS.items()},
        **{f"{k.replace('_performance', '')}": v for k, v in OLMES_PERFORMANCE_RECIPE_CHUNKS.items()},
    }
    
    resolved_recipes = []
    for arg in data_args:
        if arg in named_groups:
            resolved_recipes.extend(named_groups[arg])
        elif arg == "all":
            return data_args
        else:
            resolved_recipes.append(arg)
    
    return list(dict.fromkeys(resolved_recipes))


def plot_bump_timesteps(
    metric: str = "pile-valppl",
    model_size: str = "150M",
    data: list[str] | None = None,
    exclude_data: list[str] | None = None,
    save_path: str | None = None,
    show_plot: bool = True,
    figsize: tuple[float, float] = (14, 8),
    min_step: float | None = None,
    max_step: float | None = None,
) -> None:
    DataDecide, select_params, select_data = get_datadec_functions()

    exclude_data = exclude_data or []

    # Use only the specified model size
    params = [model_size]
    
    # Resolve named data groups first, then handle "all" and exclusions
    if data is None:
        data = ["all"]
    
    resolved_data = resolve_data_groups(data)
    if len(resolved_data) == 1 and resolved_data[0] == "all":
        data = select_data("all", exclude=exclude_data)
    else:
        data = [d for d in resolved_data if d not in (exclude_data or [])]

    dd = DataDecide()
    metrics = [metric]

    print(f"Preparing data for recipes: {data}")
    print(f"Model size: {model_size}")
    print(f"Metric: {metrics}")

    # Get training curve data (not aggregated to preserve timestep dimension)
    df = prepare_plot_data(dd, params, data, metrics, aggregate_seeds=True)

    print(f"\nData after prepare_plot_data: {df.shape}")
    print(f"Unique params in df: {sorted(df['params'].unique())}")
    print(f"Unique data in df: {sorted(df['data'].unique())}")
    print(f"Step range: {df['step'].min()} to {df['step'].max()}")

    # Filter by step range if specified
    if min_step is not None:
        df = df[df['step'] >= min_step]
        print(f"After min_step filter: {df.shape}")
    
    if max_step is not None:
        df = df[df['step'] <= max_step]
        print(f"After max_step filter: {df.shape}")

    if df.empty:
        print(f"No data found for model size {model_size} with the specified filters")
        return

    # Create bump plot data using timesteps as x-axis
    bump_data = df.rename(
        columns={
            "step": "time",  # Training steps become time dimension
            "data": "category",  # Recipes become categories (trajectories)
            "value": "score",  # Performance values (lower is better for perplexity)
        }
    )[["time", "category", "score"]]

    # Keep original perplexity values for labeling (before inversion)
    bump_data["original_ppl"] = bump_data["score"].copy()

    # Invert scores for ranking (higher score = better rank)
    bump_data["score"] = -bump_data["score"]
    metric_str = metric.replace("_", " ").replace("-", " ").title()

    print("\nBump plot data preview:")
    print(bump_data.head(10))
    print(f"\nBump data shape: {bump_data.shape}")
    print(f"Categories (recipes): {sorted(bump_data['category'].unique())}")
    print(f"Time points (steps): {sorted(bump_data['time'].unique())}")
    
    # DEBUG: Check rankings at first and last time points
    time_points = sorted(bump_data["time"].unique())
    first_time = time_points[0]
    last_time = time_points[-1]
    
    print(f"\n=== DEBUG: Timestep Bump Plot ===")
    print(f"First step: {first_time}")
    print(f"Last step: {last_time}")
    
    first_data = bump_data[bump_data["time"] == first_time].copy()
    first_data = first_data.sort_values("score", ascending=False)
    first_data["rank"] = range(1, len(first_data) + 1)
    print(f"\nFirst step rankings (LEFT labels):")
    for _, row in first_data.iterrows():
        print(f"  Rank {row['rank']}: {row['category']} (ppl={row['original_ppl']:.2f})")
    
    last_data = bump_data[bump_data["time"] == last_time].copy()
    last_data = last_data.sort_values("score", ascending=False)
    last_data["rank"] = range(1, len(last_data) + 1)
    print(f"\nLast step rankings (RIGHT labels):")
    for _, row in last_data.iterrows():
        print(f"  Rank {row['rank']}: {row['category']} (ppl={row['original_ppl']:.2f})")
    
    print(f"\n=== End Debug ===\n")
    
    # Create custom theme with extended colors for better distinction
    num_categories = len(bump_data["category"].unique())
    custom_theme = create_bump_theme_with_colors(num_categories)
    print(f"Using extended color palette for {num_categories} categories")

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,
                "cols": 1,
                "figsize": figsize,
            },
            style={"theme": custom_theme}
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
            title=f"Data Recipe Rankings Over Training ({model_size} - {metric_str})",
        )

        # Add annotations and labels
        ax = fm.get_axes(0, 0)
        add_left_ranking_labels(ax, bump_data)
        add_value_annotations(ax, bump_data)

        # Format x-axis to show step labels nicely
        step_labels = sorted(bump_data["time"].unique())
        ax.set_xticks(step_labels[::max(1, len(step_labels)//8)])  # Show ~8 labels max
        ax.set_xticklabels([format_step_label(s) for s in ax.get_xticks()])
        ax.set_xlabel("Training Step")

        # Add metric label
        metric_label = metric_str + " Values"
        ax.text(
            0.02,
            1.5,
            metric_label,
            transform=ax.transData,
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

    plot_bump_timesteps(
        metric=args.metric,
        model_size=args.model_size,
        data=args.data,
        exclude_data=args.exclude_data,
        save_path=args.save,
        show_plot=show_plot,
        figsize=figsize,
        min_step=args.min_step,
        max_step=args.max_step,
    )


if __name__ == "__main__":
    main()