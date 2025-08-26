from typing import Any, Dict, List
import pandas as pd


def load_parquet_data() -> pd.DataFrame:
    return pd.read_parquet("data/mean_eval.parquet")


def validate_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
    expected_key_columns = ["params", "data", "step"]
    validation_results = {
        "expected_columns_present": all(
            col in df.columns for col in expected_key_columns
        ),
        "missing_key_columns": [
            col for col in expected_key_columns if col not in df.columns
        ],
        "total_columns": len(df.columns),
        "total_rows": len(df),
        "data_types": dict(df.dtypes),
        "has_metric_columns": len(
            [
                col
                for col in df.columns
                if col
                not in expected_key_columns
                + [
                    "seed",
                    "tokens",
                    "compute",
                    "total_steps",
                    "warmup_steps",
                    "lr_max",
                    "batch_size",
                    "lr_at_step",
                    "cumulative_lr",
                ]
            ]
        )
        > 0,
    }
    return validation_results


def extract_available_metrics(df: pd.DataFrame) -> List[str]:
    non_metric_columns = [
        "params",
        "data",
        "step",
        "seed",
        "tokens",
        "compute",
        "total_steps",
        "warmup_steps",
        "lr_max",
        "batch_size",
        "lr_at_step",
        "cumulative_lr",
    ]
    metric_columns = [col for col in df.columns if col not in non_metric_columns]
    return sorted(metric_columns)


def extract_data_recipes(df: pd.DataFrame) -> List[str]:
    return sorted(df["data"].unique().tolist())


def extract_model_sizes(df: pd.DataFrame) -> List[str]:
    return sorted(df["params"].unique().tolist())


def analyze_data_completeness(df: pd.DataFrame) -> Dict[str, Any]:
    model_sizes = extract_model_sizes(df)
    data_recipes = extract_data_recipes(df)
    metrics = extract_available_metrics(df)

    total_combinations = len(model_sizes) * len(data_recipes)
    existing_combinations = len(df[["params", "data"]].drop_duplicates())

    missing_combinations = []
    for model_size in model_sizes:
        for recipe in data_recipes:
            combo_exists = (
                len(df[(df["params"] == model_size) & (df["data"] == recipe)]) > 0
            )
            if not combo_exists:
                missing_combinations.append((model_size, recipe))

    step_distribution = df.groupby(["params", "data"])["step"].count().describe()

    metric_completeness = {}
    for metric in metrics[:10]:
        null_count = df[metric].isnull().sum()
        metric_completeness[metric] = {
            "null_count": null_count,
            "null_percentage": (null_count / len(df)) * 100,
        }

    return {
        "total_expected_combinations": total_combinations,
        "existing_combinations": existing_combinations,
        "missing_combinations_count": len(missing_combinations),
        "missing_combinations": missing_combinations[:20],
        "data_density_percentage": (existing_combinations / total_combinations) * 100,
        "steps_per_combination_stats": step_distribution.to_dict(),
        "sample_metric_completeness": metric_completeness,
        "total_metrics_analyzed": len(metrics),
    }


def main() -> None:
    print("=" * 80)
    print("DATA EXPLORATION: MEAN_EVAL.PARQUET ANALYSIS")
    print("=" * 80)

    df = load_parquet_data()
    print(
        f"Successfully loaded dataset with {len(df):,} rows and {len(df.columns):,} columns"
    )

    print("\n" + "=" * 50)
    print("DATA STRUCTURE VALIDATION")
    print("=" * 50)
    validation = validate_data_structure(df)

    print(f"Expected key columns present: {validation['expected_columns_present']}")
    if validation["missing_key_columns"]:
        print(f"Missing key columns: {validation['missing_key_columns']}")

    print(f"Total columns: {validation['total_columns']:,}")
    print(f"Total rows: {validation['total_rows']:,}")
    print(f"Has metric columns: {validation['has_metric_columns']}")

    key_column_types = {
        col: str(validation["data_types"][col])
        for col in ["params", "data", "step"]
        if col in validation["data_types"]
    }
    print(f"Key column types: {key_column_types}")

    print("\n" + "=" * 50)
    print("AVAILABLE DIMENSIONS")
    print("=" * 50)

    metrics = extract_available_metrics(df)
    data_recipes = extract_data_recipes(df)
    model_sizes = extract_model_sizes(df)

    print(f"Available metrics ({len(metrics)} total):")
    for i, metric in enumerate(metrics[:15]):
        print(f"  {i + 1:2d}. {metric}")
    if len(metrics) > 15:
        print(f"  ... and {len(metrics) - 15} more metrics")

    print(f"\nData recipes ({len(data_recipes)} total):")
    for i, recipe in enumerate(data_recipes):
        print(f"  {i + 1:2d}. {recipe}")

    print(f"\nModel sizes ({len(model_sizes)} total):")
    for i, size in enumerate(model_sizes):
        print(f"  {i + 1:2d}. {size}")

    print("\n" + "=" * 50)
    print("DATA COMPLETENESS ANALYSIS")
    print("=" * 50)

    completeness = analyze_data_completeness(df)

    print(
        f"Total expected combinations (model_size × data_recipe): {completeness['total_expected_combinations']:,}"
    )
    print(f"Existing combinations: {completeness['existing_combinations']:,}")
    print(f"Missing combinations: {completeness['missing_combinations_count']:,}")
    print(f"Data density: {completeness['data_density_percentage']:.1f}%")

    if completeness["missing_combinations_count"] > 0:
        print(
            f"\nFirst {min(10, len(completeness['missing_combinations']))} missing combinations:"
        )
        for i, (model_size, recipe) in enumerate(
            completeness["missing_combinations"][:10]
        ):
            print(f"  {i + 1:2d}. {model_size} × {recipe}")

    steps_stats = completeness["steps_per_combination_stats"]
    print("\nSteps per combination statistics:")
    print(f"  Mean: {steps_stats['mean']:.1f}")
    print(f"  Median: {steps_stats['50%']:.1f}")
    print(f"  Min: {steps_stats['min']:.0f}")
    print(f"  Max: {steps_stats['max']:.0f}")

    print("\nSample metric completeness (first 10 metrics):")
    for metric, stats in list(completeness["sample_metric_completeness"].items())[:10]:
        print(
            f"  {metric}: {stats['null_count']:,} nulls ({stats['null_percentage']:.1f}%)"
        )

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    print(
        f"Dataset contains {len(metrics):,} metrics across {len(data_recipes)} data recipes and {len(model_sizes)} model sizes"
    )
    print(
        f"Data coverage is {completeness['data_density_percentage']:.1f}% with {completeness['missing_combinations_count']} missing combinations"
    )

    step_range = sorted(df["step"].unique())
    print(f"Training steps range from {step_range[0]:.0f} to {step_range[-1]:.0f}")

    if completeness["data_density_percentage"] < 100:
        print("\nLIMITATIONS DISCOVERED:")
        print(
            f"- {completeness['missing_combinations_count']} model_size × data_recipe combinations missing"
        )
        print("- May impact plotting for specific combinations")

    null_metrics = [
        metric
        for metric, stats in completeness["sample_metric_completeness"].items()
        if stats["null_count"] > 0
    ]
    if null_metrics:
        print(
            f"- Some metrics have null values: {len(null_metrics)} of sampled metrics"
        )

    print("\nREADY FOR PHASE 2:")
    print(f"- {len(metrics)} metrics available for row faceting")
    print(f"- {len(data_recipes)} data recipes available for column faceting")
    print(f"- {len(model_sizes)} model sizes available for line styling")
    print("- Data structure validated and suitable for faceted plotting")


if __name__ == "__main__":
    main()
