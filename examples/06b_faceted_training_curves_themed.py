from typing import Any, List, Tuple
import argparse
import itertools
import pandas as pd
import matplotlib.pyplot as plt
from dr_plotter.figure import FigureManager
from dr_plotter.theme import Theme, PlotStyles, AxesStyles, FigureStyles, BASE_THEME


def load_and_prepare_data() -> pd.DataFrame:
    return pd.read_parquet("data/mean_eval.parquet")


def create_model_size_ordering() -> List[str]:
    size_order = [
        "4M",
        "6M",
        "8M",
        "10M",
        "14M",
        "16M",
        "20M",
        "60M",
        "90M",
        "150M",
        "300M",
        "530M",
        "750M",
        "1B",
    ]
    return size_order


def create_faceted_training_curves_theme(
    x_log: bool = False, y_log: bool = False
) -> Theme:
    model_sizes = create_model_size_ordering()

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
    target_metrics = ["pile-valppl", "mmlu_average_correct_prob"]

    assert all(metric in df.columns for metric in target_metrics), (
        f"Missing metrics from {target_metrics}"
    )
    assert all(recipe in df["data"].values for recipe in target_recipes), (
        f"Missing recipes from {target_recipes}"
    )

    filtered_df = df[df["data"].isin(target_recipes)].copy()
    filtered_df = filtered_df[filtered_df["params"].isin(model_sizes)].copy()

    keep_columns = ["params", "data", "step"] + target_metrics
    filtered_df = filtered_df[keep_columns].copy()

    filtered_df["params"] = pd.Categorical(
        filtered_df["params"], categories=model_sizes, ordered=True
    )
    filtered_df["data"] = pd.Categorical(
        filtered_df["data"], categories=target_recipes, ordered=True
    )
    filtered_df = filtered_df.sort_values(["params", "data", "step"])

    return filtered_df


def create_faceted_grid_with_theme(
    custom_theme: Theme, num_recipes: int, num_model_sizes: int
) -> Tuple[plt.Figure, Any]:
    figwidth = max(12, num_recipes * 3.5)

    fm = FigureManager(
        rows=2,
        cols=num_recipes,
        figsize=(figwidth, 9),
        theme=custom_theme,
        legend_strategy="figure_below",
        legend_ncol=min(num_model_sizes, 8),
        plot_margin_top=0.1,
        plot_margin_bottom=0.12,
        legend_y_offset=0.02,
        layout_pad=0.3,
        sharey="row",
    )
    fm.fig.suptitle(
        f"Themed Faceted Training Curves: 2 Metrics × {num_recipes} Data Recipes",
        fontsize=16,
        y=0.96,
    )
    return fm.fig, fm


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
    fig, fm = create_faceted_grid_with_theme(
        custom_theme, len(target_recipes), num_model_sizes
    )

    metrics = ["pile-valppl", "mmlu_average_correct_prob"]
    metric_labels = ["Pile Validation Perplexity", "MMLU Average Correct Probability"]

    for col_idx, recipe in enumerate(target_recipes):
        recipe_data = df[df["data"] == recipe].copy()
        assert len(recipe_data) > 0, f"No data found for recipe: {recipe}"

        for row_idx, (metric, metric_label) in enumerate(zip(metrics, metric_labels)):
            metric_data = recipe_data[["params", "step", metric]].copy()
            metric_data = metric_data.dropna()

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

    fm.finalize_layout()

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
        default=[
            "4M",
            "6M",
            "8M",
            "10M",
            "14M",
            "16M",
            "20M",
            "60M",
            "90M",
            "150M",
            "300M",
            "530M",
            "750M",
            "1B",
        ],
        help="Model sizes to include (in order for line styling)",
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

    print("Filtering data for target metrics, recipes, and model sizes...")
    filtered_df = subset_data_for_plotting(df, args.recipes, args.model_sizes)
    print(f"Filtered to {len(filtered_df):,} rows")

    print(f"Model sizes (in order): {args.model_sizes}")
    print(f"Data recipes (in order): {args.recipes}")

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
        x_log=args.x_log, y_log=args.y_log
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
        args.recipes,
        x_log=args.x_log,
        y_log=args.y_log,
        xlim=args.xlim,
        ylim=args.ylim,
    )
    print("Themed visualization complete!")


if __name__ == "__main__":
    main()
