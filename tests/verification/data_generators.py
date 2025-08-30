import pandas as pd
import numpy as np
from typing import List, Dict


def create_synthetic_faceting_data(
    n_points: int,
    metrics: List[str],
    datasets: List[str],
    models: List[str],
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)

    data_rows = []

    for metric in metrics:
        for dataset in datasets:
            for model in models:
                steps = np.arange(n_points)

                # Create predictable but varied curves for each combination
                base_value = hash(f"{metric}_{dataset}_{model}") % 100
                noise_scale = 0.1 + (hash(f"{metric}_{model}") % 10) * 0.05

                if metric in ["loss", "perplexity"]:
                    # Decreasing curves for loss-like metrics
                    values = base_value * np.exp(
                        -steps / (n_points * 0.5)
                    ) + np.random.normal(0, noise_scale, n_points)
                elif metric in ["accuracy", "f1", "precision"]:
                    # Increasing curves for performance metrics
                    values = (
                        1 - np.exp(-steps / (n_points * 0.3))
                    ) * base_value + np.random.normal(0, noise_scale, n_points)
                else:
                    # General oscillating pattern
                    values = (
                        base_value
                        + 10 * np.sin(steps / (n_points * 0.1))
                        + np.random.normal(0, noise_scale, n_points)
                    )

                for step, value in zip(steps, values):
                    data_rows.append(
                        {
                            "step": step,
                            "value": value,
                            "metric": metric,
                            "dataset": dataset,
                            "model": model,
                            "seed": seed,
                        }
                    )

    return pd.DataFrame(data_rows)


def create_reference_dataset() -> pd.DataFrame:
    return create_synthetic_faceting_data(
        n_points=50,
        metrics=["loss", "accuracy"],
        datasets=["train", "val", "test"],
        models=["A", "B", "C", "D"],
        seed=42,
    )


def create_benchmark_dataset(size: str = "medium") -> pd.DataFrame:
    size_configs = {
        "small": {
            "n_points": 100,
            "metrics": ["loss", "acc"],
            "datasets": ["train", "val"],
            "models": ["A", "B"],
        },
        "medium": {
            "n_points": 1000,
            "metrics": ["loss", "acc", "f1"],
            "datasets": ["train", "val", "test"],
            "models": ["A", "B", "C", "D"],
        },
        "large": {
            "n_points": 10000,
            "metrics": ["loss", "acc", "f1", "precision"],
            "datasets": ["train", "val", "test"] * 10,
            "models": ["A", "B", "C", "D", "E"],
        },
    }

    config = size_configs.get(size, size_configs["medium"])
    return create_synthetic_faceting_data(**config, seed=42)


def create_single_dimension_data() -> Dict[str, pd.DataFrame]:
    # For rows-only testing
    rows_data = create_synthetic_faceting_data(
        n_points=30,
        metrics=["loss", "accuracy", "f1", "precision"],
        datasets=["mixed"],  # Single dataset
        models=["A", "B", "C"],
        seed=42,
    )

    # For cols-only testing
    cols_data = create_synthetic_faceting_data(
        n_points=30,
        metrics=["performance"],  # Single metric
        datasets=["train", "val", "test"],
        models=["A", "B", "C"],
        seed=42,
    )

    return {"rows_only": rows_data, "cols_only": cols_data}


def create_plot_type_test_data() -> Dict[str, pd.DataFrame]:
    # Line plot data
    line_data = create_synthetic_faceting_data(
        n_points=20,
        metrics=["metric_a", "metric_b"],
        datasets=["dataset_1", "dataset_2"],
        models=["model_x", "model_y"],
        seed=42,
    )

    # Scatter plot data
    np.random.seed(42)
    scatter_rows = []
    for metric in ["metric_a", "metric_b"]:
        for dataset in ["dataset_1", "dataset_2"]:
            for model in ["model_x", "model_y"]:
                n_points = 15
                x_pos = np.random.uniform(0, 10, n_points)
                y_pos = (
                    np.random.uniform(0, 10, n_points)
                    + hash(f"{metric}_{dataset}_{model}") % 5
                )

                for x, y in zip(x_pos, y_pos):
                    scatter_rows.append(
                        {
                            "x_pos": x,
                            "y_pos": y,
                            "metric": metric,
                            "dataset": dataset,
                            "model": model,
                        }
                    )

    scatter_data = pd.DataFrame(scatter_rows)

    # Bar plot data
    bar_rows = []
    for category in ["cat_a", "cat_b"]:
        for group in ["group_1", "group_2"]:
            for plot_type in ["type_x", "type_y"]:
                items = ["item_1", "item_2", "item_3"]
                for item in items:
                    count = (
                        np.random.randint(10, 50)
                        + hash(f"{category}_{group}_{plot_type}_{item}") % 20
                    )
                    bar_rows.append(
                        {
                            "item": item,
                            "count": count,
                            "category": category,
                            "group": group,
                            "type": plot_type,
                        }
                    )

    bar_data = pd.DataFrame(bar_rows)

    # Fill between data
    fill_rows = []
    for signal in ["signal_a", "signal_b"]:
        for condition in ["condition_1", "condition_2"]:
            for treatment in ["treatment_x", "treatment_y"]:
                time_points = np.linspace(0, 10, 20)
                base_amplitude = hash(f"{signal}_{condition}_{treatment}") % 5 + 1
                amplitude = (
                    base_amplitude
                    + np.sin(time_points)
                    + np.random.normal(0, 0.1, len(time_points))
                )

                for t, a in zip(time_points, amplitude):
                    fill_rows.append(
                        {
                            "time": t,
                            "amplitude": a,
                            "signal": signal,
                            "condition": condition,
                            "treatment": treatment,
                        }
                    )

    fill_data = pd.DataFrame(fill_rows)

    # Heatmap data
    heatmap_rows = []
    for matrix_type in ["matrix_a", "matrix_b"]:
        for scale in ["scale_1", "scale_2"]:
            for row_idx in range(5):
                for col_idx in range(5):
                    intensity = (
                        np.sin(row_idx * col_idx * 0.5)
                        + hash(f"{matrix_type}_{scale}") % 3
                    )
                    heatmap_rows.append(
                        {
                            "row_index": row_idx,
                            "col_index": col_idx,
                            "intensity": intensity,
                            "matrix_type": matrix_type,
                            "scale": scale,
                        }
                    )

    heatmap_data = pd.DataFrame(heatmap_rows)

    return {
        "line": line_data,
        "scatter": scatter_data,
        "bar": bar_data,
        "fill_between": fill_data,
        "heatmap": heatmap_data,
    }


def create_targeting_test_data() -> pd.DataFrame:
    return create_synthetic_faceting_data(
        n_points=25,
        metrics=["metric_1", "metric_2", "metric_3"],
        datasets=["dataset_1", "dataset_2", "dataset_3", "dataset_4"],
        models=["model_a", "model_b", "model_c"],
        seed=42,
    )


def create_large_performance_data() -> pd.DataFrame:
    return create_synthetic_faceting_data(
        n_points=100000,
        metrics=["loss", "acc", "f1", "precision"],
        datasets=["train", "val", "test"] * 10,  # 30 datasets
        models=["A", "B", "C", "D", "E"],
        seed=42,
    )
