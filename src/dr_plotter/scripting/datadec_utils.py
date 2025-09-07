import importlib.util
from typing import Any

import pandas as pd


def check_datadec_available() -> bool:
    if importlib.util.find_spec("datadec") is not None:
        return True
    else:
        raise ImportError(
            "DataDecide integration requires the 'datadec' optional dependency.\n"
            "Install with: uv add 'dr_plotter[datadec]' or "
            "pip install 'dr_plotter[datadec]'"
        ) from None


def get_datadec_functions() -> tuple[Any, Any, Any]:
    check_datadec_available()
    from datadec import DataDecide
    from datadec.script_utils import select_params, select_data

    return DataDecide, select_params, select_data


def get_datadec_constants() -> tuple[
    list[str], list[str], list[str], str, str, list[str]
]:
    check_datadec_available()
    import datadec.constants

    ppl_metrics = datadec.constants.PPL_TYPES
    olmes_tasks = datadec.constants.OLMES_TASKS
    metric_names = datadec.constants.METRIC_NAMES
    primary_metric_name = "primary_metric"
    default_proxy_metric_name = "correct_prob"
    id_cols = ["params", "data", "step", "tokens", "seed"]

    return (
        ppl_metrics,
        olmes_tasks,
        metric_names,
        primary_metric_name,
        default_proxy_metric_name,
        id_cols,
    )


BASE_RECIPES = [
    "C4",
    "Falcon",
    "Falcon+CC",
    "Dolma1.6++",
    "Dolma1.7",
    "FineWeb-Pro",
    "FineWeb-Edu",
    "DCLM-Baseline",
]

BASE_AND_QC = [
    "C4",
    "Falcon",
    "Falcon+CC",
    "Falcon+CC (QC 10%)",
    "Falcon+CC (QC 20%)",
    "Falcon+CC (QC Orig 10%)",
    "Falcon+CC (QC Tulu 10%)",
    "Dolma1.6++",
    "Dolma1.7",
    "DCLM-Baseline 25% / Dolma 75%",
    "DCLM-Baseline 50% / Dolma 50%",
    "DCLM-Baseline 75% / Dolma 25%",
    "FineWeb-Pro",
    "FineWeb-Edu",
    "DCLM-Baseline",
    "DCLM-Baseline (QC 10%)",
    "DCLM-Baseline (QC 20%)",
    "DCLM-Baseline (QC 7%, FW3)",
    "DCLM-Baseline (QC 7%, FW2)",
    "DCLM-Baseline (QC FW 3%)",
    "DCLM-Baseline (QC FW 10%)",
]

RECIPES_WITHOUT_ABLATIONS = [
    "C4",
    "Falcon",
    "Falcon+CC",
    "Falcon+CC (QC 10%)",
    "Falcon+CC (QC 20%)",
    "Falcon+CC (QC Orig 10%)",
    "Falcon+CC (QC Tulu 10%)",
    "Dolma1.6++",
    "Dolma1.7",
    "FineWeb-Pro",
    "FineWeb-Edu",
    "DCLM-Baseline",
    "DCLM-Baseline (QC 10%)",
    "DCLM-Baseline (QC 20%)",
    "DCLM-Baseline (QC 7%, FW3)",
    "DCLM-Baseline (QC 7%, FW2)",
    "DCLM-Baseline (QC FW 3%)",
    "DCLM-Baseline (QC FW 10%)",
]

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
        "Dolma1.7",
        "DCLM-Baseline 25% / Dolma 75%",
        "DCLM-Baseline 50% / Dolma 50%",
        "DCLM-Baseline 75% / Dolma 25%",
        "DCLM-Baseline",
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


def build_olmes_metric_list(tasks: list[str], metric_names: list[str]) -> list[str]:
    return [f"{task}_{metric_name}" for task in tasks for metric_name in metric_names]


def all_metrics() -> list[str]:
    ppl_metrics, olmes_tasks, metric_names, _, _, _ = get_datadec_constants()
    return ppl_metrics + build_olmes_metric_list(olmes_tasks, metric_names)


def primary_olmes_metrics() -> list[str]:
    _, olmes_tasks, _, primary_metric_name, _, _ = get_datadec_constants()
    return build_olmes_metric_list(olmes_tasks, [primary_metric_name])


def default_olmes_proxy_metrics() -> list[str]:
    _, olmes_tasks, _, _, default_proxy_metric_name, _ = get_datadec_constants()
    return build_olmes_metric_list(olmes_tasks, [default_proxy_metric_name])


def primary_metrics() -> list[str]:
    ppl_metrics, _, _, _, _, _ = get_datadec_constants()
    return ppl_metrics + primary_olmes_metrics()


def prepare_plot_data(
    dd: Any,
    params: list[str],
    data: list[str],
    metrics: list[str],
    aggregate_seeds: bool = False,
) -> pd.DataFrame:
    ppl_metrics, _, _, _, _, id_cols = get_datadec_constants()

    filter_types = ["max_steps"]

    # Smart filtering: only add ppl/olmes filter if ALL metrics fall into one category
    ppl_metrics_filtered = [m for m in metrics if m in ppl_metrics]
    olmes_metrics_filtered = [m for m in metrics if m not in ppl_metrics]

    if ppl_metrics_filtered and not olmes_metrics_filtered:
        filter_types.append("ppl")
    elif olmes_metrics_filtered and not ppl_metrics_filtered:
        filter_types.append("olmes")
    # If mixed, use no additional filtering

    df = dd.get_filtered_df(
        filter_types=filter_types,
        return_means=False,
        min_params=None,
        verbose=True,
    )

    # Filter by params/data and keep only needed columns
    df = df[df["params"].isin(params) & df["data"].isin(data)]
    keep_columns = id_cols + metrics
    df = df[keep_columns].copy()

    # Optionally aggregate across seeds first (prevents NaN gaps in mean plotting)
    if aggregate_seeds:
        # Remove 'seed' from id_cols for grouping
        group_cols = [col for col in id_cols if col != "seed"]
        df = df.groupby(group_cols, observed=False)[metrics].mean().reset_index()
        # Use group_cols as new id_cols for melting
        melt_id_cols = group_cols
    else:
        # Use original id_cols for individual seed plotting
        melt_id_cols = id_cols

    # Melt and drop NaN values (same logic for both cases)
    melted_df = df.melt(
        id_vars=melt_id_cols,
        value_vars=metrics,
        var_name="metric",
        value_name="value",
    )
    melted_df = melted_df.dropna(subset=["value"])

    # Set categorical ordering and sort
    melted_df["params"] = pd.Categorical(
        melted_df["params"], categories=params, ordered=True
    )
    melted_df["data"] = pd.Categorical(melted_df["data"], categories=data, ordered=True)

    return melted_df.sort_values(["params", "data", "step"])
