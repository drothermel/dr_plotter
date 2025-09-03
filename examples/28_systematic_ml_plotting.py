from __future__ import annotations

import argparse
import sys
import time

import datadec.constants
import matplotlib.pyplot as plt
import pandas as pd
from pandas.io.common import Path

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.datadec_utils import get_datadec_functions

DataDecide, select_params, select_data = get_datadec_functions()


CUSTOM_RECIPE_FAMILIES = {
    "core_datasets": ["C4", "Falcon", "Dolma1.6++"],
    "dolma17_variants": [
        "Dolma1.7",
        "Dolma1.7 (no code)",
        "Dolma1.7 (no math, code)",
        "Dolma1.7 (no Reddit)",
        "Dolma1.7 (no Flan)",
    ],
    "dclm_variants": [
        "DCLM-Baseline",
        "DCLM-Baseline (QC 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "DCLM-Baseline (QC 7%, FW2)",
        "DCLM-Baseline (QC FW 3%)",
        "DCLM-Baseline (QC FW 10%)",
    ],
    "falcon_cc_variants": [
        "Falcon+CC",
        "Falcon+CC (QC 10%)",
        "Falcon+CC (QC 20%)",
        "Falcon+CC (QC Orig 10%)",
        "Falcon+CC (QC Tulu 10%)",
    ],
    "fineweb_variants": ["FineWeb-Pro", "FineWeb-Edu"],
    "mix_with_baselines": [
        "DCLM-Baseline 25% / Dolma 75%",
        "DCLM-Baseline 50% / Dolma 50%",
        "DCLM-Baseline 75% / Dolma 25%",
        "DCLM-Baseline",
        "Dolma1.7",
    ],
}

PPL_PERFORMANCE_RECIPE_CHUNKS = {
    "best_ppl_performance": [
        "DCLM-Baseline 25% / Dolma 75%",
        "Dolma1.7 (no code)",
        "Dolma1.7",
        "Dolma1.7 (no Flan)",
        "DCLM-Baseline 50% / Dolma 50%",
        "Dolma1.6++",
        "Dolma1.7 (no Reddit)",
    ],
    "good_ppl_performance": [
        "DCLM-Baseline 75% / Dolma 25%",
        "Dolma1.7 (no math, code)",
        "Falcon+CC (QC Tulu 10%)",
        "Falcon+CC (QC 20%)",
        "Falcon+CC",
        "Falcon+CC (QC Orig 10%)",
    ],
    "medium_ppl_performance": [
        "DCLM-Baseline",
        "Falcon+CC (QC 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 7%, FW2)",
        "Falcon",
        "DCLM-Baseline (QC 10%)",
    ],
    "poor_ppl_performance": [
        "DCLM-Baseline (QC FW 10%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "FineWeb-Edu",
        "FineWeb-Pro",
        "DCLM-Baseline (QC FW 3%)",
        "C4",
    ],
}

OLMES_PERFORMANCE_RECIPE_CHUNKS = {
    "best_olmes_performance": [
        "DCLM-Baseline (QC 7%, FW2)",
        "DCLM-Baseline (QC FW 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 10%)",
        "Falcon+CC (QC Orig 10%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "Falcon+CC (QC 10%)",
    ],
    "good_olmes_performance": [
        "FineWeb-Pro",
        "FineWeb-Edu",
        "DCLM-Baseline",
        "Falcon+CC (QC 20%)",
        "Falcon+CC (QC Tulu 10%)",
        "DCLM-Baseline (QC FW 3%)",
    ],
    "medium_olmes_performance": [
        "DCLM-Baseline 25% / Dolma 75%",
        "DCLM-Baseline 75% / Dolma 25%",
        "C4",
        "Dolma1.7 (no code)",
        "Dolma1.7 (no Reddit)",
        "Falcon",
    ],
    "poor_olmes_performance": [
        "Dolma1.7 (no math, code)",
        "Dolma1.7 (no Flan)",
        "DCLM-Baseline 50% / Dolma 50%",
        "Falcon+CC",
        "Dolma1.7",
        "Dolma1.6++",
    ],
}


def get_available_data_info() -> tuple[list[str], list[str], list[str], list[str]]:
    dd = DataDecide()
    df = dd.full_eval
    available_recipes = sorted(df["data"].unique())
    available_sizes = sorted(df["params"].unique())

    ppl_metrics = [
        col
        for col in df.columns
        if col in datadec.constants.PPL_TYPES and df[col].notna().sum() > 0
    ]
    olmes_metrics = [
        col
        for col in df.columns
        if any(task in col for task in datadec.constants.OLMES_TASKS)
        and df[col].notna().sum() > 0
    ]

    return available_recipes, available_sizes, ppl_metrics, olmes_metrics


def load_and_prepare_data(include_seeds: bool = False) -> pd.DataFrame:
    filter_types = ["ppl", "max_steps"]
    if include_seeds:
        filter_types.append("seed")

    try:
        dd = DataDecide()
        return dd.full_eval
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)


def prepare_systematic_data(
    df: pd.DataFrame,
    target_recipes: list[str],
    model_sizes: list[str],
    target_metrics: list[str],
    include_seeds: bool = False,
) -> pd.DataFrame:
    filtered_df = df[
        df["data"].isin(target_recipes) & df["params"].isin(model_sizes)
    ].copy()

    id_vars = ["params", "data", "step"]
    if include_seeds:
        id_vars.append("seed")

    keep_columns = id_vars + target_metrics
    filtered_df = filtered_df[keep_columns].copy()

    melted_df = filtered_df.melt(
        id_vars=id_vars,
        value_vars=target_metrics,
        var_name="metric",
        value_name="value",
    )

    melted_df = melted_df.dropna(subset=["value"])

    melted_df["params"] = pd.Categorical(
        melted_df["params"], categories=model_sizes, ordered=True
    )
    melted_df["data"] = pd.Categorical(
        melted_df["data"], categories=target_recipes, ordered=True
    )

    return melted_df.sort_values(["metric", "data", "params", "step"])


def create_metric_labels(metrics: list[str]) -> dict[str, str]:
    labels = {}
    for metric in metrics:
        if "pile-valppl" in metric:
            labels[metric] = "Pile Validation Perplexity"
        elif "wikitext" in metric and "valppl" in metric:
            labels[metric] = "WikiText-103 Validation Perplexity"
        elif "c4_en-valppl" in metric:
            labels[metric] = "C4 English Validation Perplexity"
        elif "mmlu_average" in metric:
            if "acc_raw" in metric:
                labels[metric] = "MMLU Average Accuracy"
            elif "correct_prob" in metric:
                labels[metric] = "MMLU Average Correct Probability"
        elif "arc_challenge" in metric and "acc_raw" in metric:
            labels[metric] = "ARC Challenge Accuracy"
        elif "hellaswag" in metric and "acc_raw" in metric:
            labels[metric] = "HellaSwag Accuracy"
        else:
            labels[metric] = metric.replace("_", " ").title()

    return labels


def create_single_metric_plots(
    metric_name: str,
    target_recipes: list[str],
    model_sizes: list[str],
    output_dir: str = "plots/systematic",
    mean_and_seeds: bool = True,
    show_plots: bool = True,
) -> None:
    print(f"Creating plots for single metric: {metric_name}")

    df = load_and_prepare_data(include_seeds=mean_and_seeds)

    if metric_name not in df.columns:
        print(f"Error: Metric '{metric_name}' not found in data")
        return

    melted_df = prepare_systematic_data(
        df, target_recipes, model_sizes, [metric_name], include_seeds=mean_and_seeds
    )

    if len(melted_df) == 0:
        print(f"No data found for metric '{metric_name}' with given recipes/sizes")
        return

    metric_labels = create_metric_labels([metric_name])
    melted_df["metric_label"] = melted_df["metric"].map(metric_labels)

    # Use wrapped layout for correct legend colors, fix visual issues
    figwidth = len(model_sizes) * 4.5
    figheight = 6.0  # Fixed height for single row

    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,  # Single row
                "cols": len(model_sizes),
                "figsize": (figwidth, figheight),
                "tight_layout_pad": 0.8,
                "subplot_kwargs": {"sharey": True},
            },
            legend={
                "strategy": "figure",
                "ncol": min(len(target_recipes), 4),  # Reduce columns
                "layout_top_margin": 0.15,  # More space for suptitle
                "layout_bottom_margin": 0.25,  # Adjust legend space
                # "bbox_y_offset" is no longer supported, use positioning_config instead
                # Configure layout margins to properly position the legend
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"{metric_labels[metric_name]}: "
            f"{len(target_recipes)} Recipes × {len(model_sizes)} Model Sizes",
            fontsize=16,
            y=0.95,
        )

        if mean_and_seeds and "seed" in melted_df.columns:
            mean_df = (
                melted_df.groupby(["params", "data", "metric", "step"])["value"]
                .mean()
                .reset_index()
            )
            mean_df["data"] = pd.Categorical(
                mean_df["data"], categories=target_recipes, ordered=True
            )
            mean_df["params"] = pd.Categorical(
                mean_df["params"], categories=model_sizes, ordered=True
            )

            fm.plot_faceted(
                data=melted_df,
                plot_type="line",
                rows="data",
                cols="params",
                lines="seed",
                x="step",
                y="value",
                alpha=0.3,
                linewidth=0.8,
            )

            fm.plot_faceted(
                data=mean_df,
                plot_type="line",
                rows="data",
                cols="params",
                lines="data",
                x="step",
                y="value",
                alpha=0.9,
                linewidth=2.0,
            )
        else:
            fm.plot_faceted(
                data=melted_df,
                plot_type="line",
                cols="params",  # Model sizes across columns (single row)
                lines="data",  # Color by recipes (works correctly)
                x="step",
                y="value",
                alpha=0.8,
                linewidth=1.5,
            )

        # Single row layout - just label columns
        for col_idx in range(len(model_sizes)):
            ax = fm.get_axes(0, col_idx)  # Only one row (index 0)

            ax.set_xlabel("Training Steps")

            if col_idx == 0:
                ax.set_ylabel(metric_labels[metric_name])
            else:
                ax.set_ylabel("")

            ax.set_title(f"{model_sizes[col_idx]} Parameters", pad=10)

            ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))
            ax.grid(visible=True, alpha=0.3)

        # FigureManager now handles legend finalization in finalize_layout(), called on context exit
        # Nothing needed here anymore

        safe_metric_name = metric_name.replace("-", "_").replace(" ", "_")
        metric_type = (
            "ppl"
            if any(ppl in metric_name for ppl in ["ppl", "Perplexity"])
            else "olmes"
        )
        output_path = get_nested_output_path(
            "single_metrics", metric_type, f"{safe_metric_name}.png", output_dir
        )

        plt.savefig(output_path, dpi=150, bbox_inches="tight")

        if show_plots:
            plt.show()
            time.sleep(5)

        plt.close()
        print(f"Saved plot to: {output_path}")


def create_ppl_group_plots(
    target_recipes: list[str],
    model_sizes: list[str],
    output_dir: str = "plots/systematic",
    ppl_metrics: list[str] | None = None,
    show_plots: bool = True,
) -> None:
    print("Creating PPL group plots...")

    df = load_and_prepare_data()

    if ppl_metrics is None:
        ppl_metrics = [
            col
            for col in df.columns
            if col in datadec.constants.PPL_TYPES and df[col].notna().sum() > 0
        ][:4]

    ppl_metrics = [m for m in ppl_metrics if m in df.columns]

    if not ppl_metrics:
        print("No PPL metrics found")
        return

    melted_df = prepare_systematic_data(df, target_recipes, model_sizes, ppl_metrics)

    if len(melted_df) == 0:
        print("No data found for PPL metrics")
        return

    metric_labels = create_metric_labels(ppl_metrics)
    melted_df["metric_label"] = melted_df["metric"].map(metric_labels)

    figwidth = len(target_recipes) * 5.0  # No max limit - scale indefinitely
    figheight = len(model_sizes) * 5.5  # No max limit - scale indefinitely

    with FigureManager(
        PlotConfig(
            layout={
                "rows": len(model_sizes),
                "cols": len(target_recipes),
                "figsize": (figwidth, figheight),
                "tight_layout_pad": 0.5,
                "subplot_kwargs": {"sharey": "row"},
            },
            legend={
                "strategy": "figure",
                "ncol": min(len(ppl_metrics), 4),
                "layout_top_margin": 0.05,
                "layout_bottom_margin": 0.4,
                # "bbox_y_offset" is no longer supported, use positioning_config instead
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"Perplexity Metrics: "
            f"{len(model_sizes)} Model Sizes × {len(target_recipes)} Recipes",
            fontsize=16,
            y=0.96,
        )

        fm.plot_faceted(
            data=melted_df,
            plot_type="line",
            rows="params",
            cols="data",
            lines="metric",
            x="step",
            y="value",
            linewidth=1.5,
            alpha=0.8,
        )

        for row_idx in range(len(model_sizes)):
            for col_idx in range(len(target_recipes)):
                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == len(model_sizes) - 1:
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:
                    ax.set_ylabel(f"{model_sizes[row_idx]} - Perplexity")
                else:
                    ax.set_ylabel("")

                if row_idx == 0:
                    ax.set_title(target_recipes[col_idx], pad=10)

                ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))
                ax.grid(visible=True, alpha=0.3)

    output_path = get_nested_output_path(
        "grouped_metrics", "ppl_groups", "ppl_group_metrics.png", output_dir
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plots:
        plt.show()
        time.sleep(5)

    plt.close()
    print(f"Saved plot to: {output_path}")


def create_olmes_group_plots(
    target_recipes: list[str],
    model_sizes: list[str],
    output_dir: str = "plots/systematic",
    olmes_metrics: list[str] | None = None,
    show_plots: bool = True,
) -> None:
    print("Creating OLMES group plots...")

    df = load_and_prepare_data()

    if olmes_metrics is None:
        olmes_metrics = []
        for task in [
            "mmlu_average_acc_raw",
            "arc_challenge_acc_raw",
            "hellaswag_acc_raw",
            "boolq_acc_raw",
        ][:4]:
            if task in df.columns and df[task].notna().sum() > 0:
                olmes_metrics.append(task)

    olmes_metrics = [m for m in olmes_metrics if m in df.columns]

    if not olmes_metrics:
        print("No OLMES metrics found")
        return

    melted_df = prepare_systematic_data(df, target_recipes, model_sizes, olmes_metrics)

    if len(melted_df) == 0:
        print("No data found for OLMES metrics")
        return

    metric_labels = create_metric_labels(olmes_metrics)
    melted_df["metric_label"] = melted_df["metric"].map(metric_labels)

    figwidth = len(target_recipes) * 5.0  # No max limit - scale indefinitely
    figheight = len(model_sizes) * 5.5  # No max limit - scale indefinitely

    with FigureManager(
        PlotConfig(
            layout={
                "rows": len(model_sizes),
                "cols": len(target_recipes),
                "figsize": (figwidth, figheight),
                "tight_layout_pad": 0.5,
                "subplot_kwargs": {"sharey": "row"},
            },
            legend={
                "strategy": "figure",
                "ncol": min(len(olmes_metrics), 4),
                "layout_top_margin": 0.05,
                "layout_bottom_margin": 0.4,
                # "bbox_y_offset" is no longer supported, use positioning_config instead
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"OLMES Task Metrics: "
            f"{len(model_sizes)} Model Sizes × {len(target_recipes)} Recipes",
            fontsize=16,
            y=0.96,
        )

        fm.plot_faceted(
            data=melted_df,
            plot_type="line",
            rows="params",
            cols="data",
            lines="metric",
            x="step",
            y="value",
            linewidth=1.5,
            alpha=0.8,
        )

        for row_idx in range(len(model_sizes)):
            for col_idx in range(len(target_recipes)):
                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == len(model_sizes) - 1:
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:
                    ax.set_ylabel(f"{model_sizes[row_idx]} - Accuracy")
                else:
                    ax.set_ylabel("")

                if row_idx == 0:
                    ax.set_title(target_recipes[col_idx], pad=10)

                ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))
                ax.grid(visible=True, alpha=0.3)

    output_path = get_nested_output_path(
        "grouped_metrics", "olmes_groups", "olmes_group_metrics.png", output_dir
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plots:
        plt.show()
        time.sleep(5)

    plt.close()
    print(f"Saved plot to: {output_path}")


def get_nested_output_path(
    plot_type: str, subtype: str, filename: str, base_dir: str = "plots/systematic"
) -> str:
    nested_dir = Path(base_dir) / plot_type / subtype
    nested_dir.mkdir(parents=True, exist_ok=True)
    return str(nested_dir / filename)


def create_recipe_family_chunk_plots(  # noqa: C901, PLR0912
    family_name: str,
    model_sizes: list[str],
    output_dir: str = "plots/systematic",
    chunk_source: str = "custom",
    show_plots: bool = True,
) -> None:
    print(f"Creating recipe family chunk plots for: {family_name}")

    if chunk_source == "custom":
        if family_name not in CUSTOM_RECIPE_FAMILIES:
            print(f"Error: Family '{family_name}' not found in custom families")
            print(f"Available families: {list(CUSTOM_RECIPE_FAMILIES.keys())}")
            return
        target_recipes = CUSTOM_RECIPE_FAMILIES[family_name]
    elif chunk_source == "ppl_performance":
        if family_name not in PPL_PERFORMANCE_RECIPE_CHUNKS:
            print(f"Error: PPL performance chunk '{family_name}' not found")
            print(f"Available PPL chunks: {list(PPL_PERFORMANCE_RECIPE_CHUNKS.keys())}")
            return
        target_recipes = PPL_PERFORMANCE_RECIPE_CHUNKS[family_name]
    elif chunk_source == "olmes_performance":
        if family_name not in OLMES_PERFORMANCE_RECIPE_CHUNKS:
            print(f"Error: OLMES performance chunk '{family_name}' not found")
            print(
                f"Available OLMES chunks: "
                f"{list(OLMES_PERFORMANCE_RECIPE_CHUNKS.keys())}"
            )
            return
        target_recipes = OLMES_PERFORMANCE_RECIPE_CHUNKS[family_name]
    else:
        print(f"Error: Unknown chunk source '{chunk_source}'")
        return

    available_recipes, available_sizes, ppl_metrics, olmes_metrics = (
        get_available_data_info()
    )

    target_recipes = [r for r in target_recipes if r in available_recipes]
    model_sizes = [s for s in model_sizes if s in available_sizes]

    if not target_recipes:
        print("No valid recipes found")
        return

    if not model_sizes:
        print("No valid model sizes found")
        return

    selected_metrics = (ppl_metrics[:2] + olmes_metrics[:2])[:4]

    df = load_and_prepare_data()
    melted_df = prepare_systematic_data(
        df, target_recipes, model_sizes, selected_metrics
    )

    if len(melted_df) == 0:
        print(f"No data found for recipe family '{family_name}'")
        return

    metric_labels = create_metric_labels(selected_metrics)
    melted_df["metric_label"] = melted_df["metric"].map(metric_labels)

    figwidth = len(target_recipes) * 4.0  # No max limit - scale indefinitely
    figheight = len(model_sizes) * 4.5  # No max limit - scale indefinitely

    with FigureManager(
        PlotConfig(
            layout={
                "rows": len(model_sizes),
                "cols": len(target_recipes),
                "figsize": (figwidth, figheight),
                "tight_layout_pad": 0.5,
                "subplot_kwargs": {"sharey": "row"},
            },
            legend={
                "strategy": "figure",
                "ncol": min(len(selected_metrics), 4),
                "layout_top_margin": 0.05,
                "layout_bottom_margin": 0.4,
                # "bbox_y_offset" is no longer supported, use positioning_config instead
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"Recipe Family '{family_name}': "
            f"{len(model_sizes)} Model Sizes × {len(target_recipes)} Recipes",
            fontsize=16,
            y=0.96,
        )

        fm.plot_faceted(
            data=melted_df,
            plot_type="line",
            rows="params",
            cols="data",
            lines="metric",
            x="step",
            y="value",
            linewidth=1.5,
            alpha=0.8,
        )

        for row_idx in range(len(model_sizes)):
            for col_idx in range(len(target_recipes)):
                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == len(model_sizes) - 1:
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:
                    ax.set_ylabel(f"{model_sizes[row_idx]} Parameters")
                else:
                    ax.set_ylabel("")

                if row_idx == 0:
                    recipe = target_recipes[col_idx]
                    short_name = recipe.replace("DCLM-Baseline", "DCLM").replace(
                        "Dolma1.7", "D1.7"
                    )
                    ax.set_title(short_name, pad=10, fontsize=10)

                ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))
                ax.grid(visible=True, alpha=0.3)

    if chunk_source == "custom":
        subtype = "custom_families"
    elif chunk_source == "ppl_performance":
        subtype = "ppl_performance_chunks"
    else:  # olmes_performance
        subtype = "olmes_performance_chunks"
    output_path = get_nested_output_path(
        "recipe_chunks", subtype, f"{family_name}.png", output_dir
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plots:
        plt.show()
        time.sleep(5)

    plt.close()
    print(f"Saved plot to: {output_path}")


def create_size_chunk_plots(
    chunk_idx: int,
    target_recipes: list[str],
    chunk_size: int = 4,
    output_dir: str = "plots/systematic",
    show_plots: bool = True,
) -> None:
    print(f"Creating size chunk plots (chunk {chunk_idx})...")

    available_recipes, available_sizes, ppl_metrics, olmes_metrics = (
        get_available_data_info()
    )

    start_idx = chunk_idx * chunk_size
    end_idx = start_idx + chunk_size
    size_chunk = available_sizes[start_idx:end_idx]

    if not size_chunk:
        print(f"No model sizes available for chunk {chunk_idx}")
        return

    target_recipes = [r for r in target_recipes if r in available_recipes]
    if not target_recipes:
        print("No valid recipes provided")
        return

    selected_metrics = (ppl_metrics[:2] + olmes_metrics[:2])[:4]

    df = load_and_prepare_data()
    melted_df = prepare_systematic_data(
        df, target_recipes, size_chunk, selected_metrics
    )

    if len(melted_df) == 0:
        print(f"No data found for size chunk {chunk_idx}")
        return

    metric_labels = create_metric_labels(selected_metrics)
    melted_df["metric_label"] = melted_df["metric"].map(metric_labels)

    figwidth = max(15, len(size_chunk) * 3.5)

    with FigureManager(
        PlotConfig(
            layout={
                "rows": len(selected_metrics),
                "cols": len(size_chunk),
                "figsize": (figwidth, len(selected_metrics) * 3),
                "tight_layout_pad": 0.3,
                "subplot_kwargs": {"sharey": "row"},
            },
            legend={
                "strategy": "figure",
                "ncol": min(len(target_recipes), 6),
                "layout_top_margin": 0.1,
                "layout_bottom_margin": 0.4,
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"Model Size Chunk {chunk_idx}: "
            f"{len(selected_metrics)} Metrics × {len(size_chunk)} Sizes",
            fontsize=16,
            y=0.96,
        )

        fm.plot_faceted(
            data=melted_df,
            plot_type="line",
            rows="metric",
            cols="params",
            lines="data",
            x="step",
            y="value",
            linewidth=1.5,
            alpha=0.8,
        )

        for row_idx in range(len(selected_metrics)):
            for col_idx in range(len(size_chunk)):
                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == len(selected_metrics) - 1:
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:
                    metric_name = selected_metrics[row_idx]
                    ax.set_ylabel(metric_labels[metric_name])
                else:
                    ax.set_ylabel("")

                if row_idx == 0:
                    ax.set_title(f"{size_chunk[col_idx]} Parameters", pad=10)

                ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))
                ax.grid(visible=True, alpha=0.3)

    nested_dir = Path(output_dir) / f"size_chunk_{chunk_idx}"
    nested_dir.mkdir(parents=True, exist_ok=True)
    output_path = f"{output_dir}/size_chunk_{chunk_idx}.png"

    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plots:
        plt.show()
        time.sleep(5)

    plt.close()
    print(f"Saved plot to: {output_path}")


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Systematic ML Evaluation Plotting using dr_plotter faceting system"
    )

    parser.add_argument(
        "plot_type",
        choices=[
            "single",
            "ppl-group",
            "olmes-group",
            "size-chunk",
            "recipe-family",
            "recipe-performance",
            "info",
        ],
        help="Type of plot to create",
    )

    parser.add_argument(
        "--metric",
        help="Specific metric for single metric plots "
        "(e.g., pile-valppl, mmlu_average_acc_raw)",
    )

    parser.add_argument(
        "--recipes",
        nargs="+",
        default=["C4", "Dolma1.7"],
        help="Data recipes to include",
    )

    parser.add_argument(
        "--model-sizes",
        nargs="+",
        default=["10M", "20M", "60M", "90M"],
        help="Model sizes to include",
    )

    parser.add_argument(
        "--family-name",
        help="Family name for recipe-family or recipe-performance plots",
    )

    parser.add_argument(
        "--performance-type",
        choices=["ppl", "olmes"],
        default="ppl",
        help="Performance metric type for recipe-performance plots (ppl or olmes)",
    )

    parser.add_argument(
        "--chunk-idx", type=int, default=0, help="Chunk index for size-chunk plots"
    )

    parser.add_argument(
        "--chunk-size", type=int, default=4, help="Number of model sizes per chunk"
    )

    parser.add_argument(
        "--output-dir", default="plots/systematic", help="Output directory for plots"
    )

    parser.add_argument(
        "--mean-and-seeds",
        action="store_true",
        help="Include individual seed data with mean overlay",
    )

    parser.add_argument(
        "--no-show", action="store_true", help="Don't display plots interactively"
    )

    return parser


def main() -> None:  # noqa: C901
    parser = create_arg_parser()
    args = parser.parse_args()

    if args.plot_type == "info":
        print("Getting available data info...")
        available_recipes, available_sizes, ppl_metrics, olmes_metrics = (
            get_available_data_info()
        )
        print(f"\nAvailable recipes ({len(available_recipes)}):")
        for recipe in available_recipes:
            print(f"  - {recipe}")
        print(f"\nAvailable model sizes ({len(available_sizes)}):")
        for size in available_sizes:
            print(f"  - {size}")
        print(f"\nAvailable PPL metrics ({len(ppl_metrics)}):")
        for metric in ppl_metrics:
            print(f"  - {metric}")
        print(f"\nAvailable OLMES metrics ({len(olmes_metrics)}):")
        for metric in olmes_metrics:
            print(f"  - {metric}")

        print("\nCustom Recipe Families:")
        for family_name in CUSTOM_RECIPE_FAMILIES:
            print(f"  - {family_name}")

        print("\nPPL Performance Chunks:")
        for chunk_name in PPL_PERFORMANCE_RECIPE_CHUNKS:
            print(f"  - {chunk_name}")

        print("\nOLMES Performance Chunks:")
        for chunk_name in OLMES_PERFORMANCE_RECIPE_CHUNKS:
            print(f"  - {chunk_name}")
        return

    try:
        validated_recipes = args.recipes
        validated_model_sizes = args.model_sizes
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)

    show_plots = not args.no_show

    if args.plot_type == "single":
        if not args.metric:
            print("Error: --metric is required for single metric plots")
            sys.exit(1)
        create_single_metric_plots(
            args.metric,
            validated_recipes,
            validated_model_sizes,
            args.output_dir,
            args.mean_and_seeds,
            show_plots,
        )

    elif args.plot_type == "ppl-group":
        create_ppl_group_plots(
            validated_recipes,
            validated_model_sizes,
            args.output_dir,
            show_plots=show_plots,
        )

    elif args.plot_type == "olmes-group":
        create_olmes_group_plots(
            validated_recipes,
            validated_model_sizes,
            args.output_dir,
            show_plots=show_plots,
        )

    elif args.plot_type == "size-chunk":
        create_size_chunk_plots(
            args.chunk_idx,
            validated_recipes,
            args.chunk_size,
            args.output_dir,
            show_plots,
        )

    elif args.plot_type == "recipe-family":
        if not args.family_name:
            print("Error: --family-name is required for recipe-family plots")
            sys.exit(1)
        create_recipe_family_chunk_plots(
            args.family_name,
            validated_model_sizes,
            args.output_dir,
            "custom",
            show_plots,
        )

    elif args.plot_type == "recipe-performance":
        if not args.family_name:
            print("Error: --family-name is required for recipe-performance plots")
            sys.exit(1)
        chunk_source = f"{args.performance_type}_performance"
        create_recipe_family_chunk_plots(
            args.family_name,
            validated_model_sizes,
            args.output_dir,
            chunk_source,
            show_plots,
        )


if __name__ == "__main__":
    main()
