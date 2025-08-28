#!/usr/bin/env python3
"""
Plot model scaling for any DataDecide metric.

Requires DataDecide integration:
    uv add "dr_plotter[datadec]"

Usage:
    python scripts/plot_metric_scaling.py wikitext_103-valppl
    python scripts/plot_metric_scaling.py pile-valppl
    python scripts/plot_metric_scaling.py primary_metric --min-params 150M
"""

import argparse
import os
import sys
import matplotlib.pyplot as plt
from dr_plotter.plotters.curve import CurvePlotter
from dr_plotter.scripting.datadec_utils import safe_import_datadec, get_clean_datadec_df


def load_datadec_data(data_dir="./test_data", verbose=False):
    """Load clean DataDecide data with error handling."""
    try:
        return get_clean_datadec_df(filter_types=["ppl", "max_steps"], data_dir=data_dir, verbose=verbose)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)


def prepare_scaling_data(df, metric_name, min_params=None):
    """Prepare data for scaling analysis."""
    DataDecide, _, _ = safe_import_datadec()
    from datadec import model_utils  # Import here to handle optional dependency
    
    analysis_df = df

    # DataDecide guarantees metric availability, but check anyway
    if metric_name not in analysis_df.columns:
        available_metrics = [
            col for col in analysis_df.columns 
            if any(keyword in col.lower() for keyword in ["ppl", "acc", "metric", "prob", "correct"])
        ]
        raise ValueError(
            f"Metric '{metric_name}' not found. Available: {available_metrics[:10]}..."
        )

    # DataDecide provides clean data, but apply min_params filter if needed
    clean_df = analysis_df
    if min_params:
        min_params_numeric = model_utils.param_to_numeric(min_params)
        clean_df["params_numeric"] = clean_df["params"].apply(model_utils.param_to_numeric)
        clean_df = clean_df[clean_df["params_numeric"] >= min_params_numeric]
    
    if len(clean_df) == 0:
        raise ValueError(f"No data available for metric '{metric_name}' with min_params={min_params}")

    # Group by model size and data recipe, average across seeds
    scaling_data = (
        clean_df.groupby(["params", "data"]).agg({metric_name: "mean"}).reset_index()
    )

    # Convert model size to numeric for proper ordering
    scaling_data["params_numeric"] = scaling_data["params"].apply(
        model_utils.param_to_numeric
    )
    scaling_data = scaling_data.sort_values("params_numeric")

    return scaling_data


def create_scaling_plot(scaling_data, metric_name):
    """Create scaling plot using dr_plotter's curve comparison."""

    # Sort data for proper line connections
    scaling_data = scaling_data.sort_values("params_numeric")

    # Use CurvePlotter's built-in comparison method
    plotter = CurvePlotter(scaling_data)
    fig, ax = plotter.plot_curve_comparison(
        x_col="params_numeric",
        y_col=metric_name,
        group_by="data",
        marker="o",  # Add markers to make it look more like scatter
    )

    # Only add what dr_plotter doesn't handle
    ax.set_xscale("log")  # Log scale for model sizes
    ax.set_xlabel("Model Size (M parameters)")
    ax.set_ylabel(metric_name.replace("_", " ").replace("-", " ").title())
    ax.set_title(
        f"Model Scaling: {metric_name.replace('_', ' ').replace('-', ' ').title()}"
    )

    plt.show()
    return fig, ax


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Plot model scaling for DataDecide metrics"
    )
    parser.add_argument(
        "metric", help="Metric name to plot (e.g., wikitext_103-valppl, pile-valppl)"
    )
    parser.add_argument("--min-params", help="Minimum model size (e.g., 10M, 150M)")
    parser.add_argument(
        "--data-dir",
        default="./test_data",
        help="Data directory for DataDecide cache (default: ./test_data)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        print("Loading DataDecide data...")
        df = load_datadec_data(args.data_dir, args.verbose)
        print(f"Loaded {len(df):,} rows")

        print(f"Preparing scaling data for metric: {args.metric}")
        scaling_data = prepare_scaling_data(df, args.metric, args.min_params)

        print(f"Found {len(scaling_data)} model-recipe combinations")
        print(f"Model sizes: {sorted(scaling_data['params'].unique())}")
        print(f"Data recipes: {sorted(scaling_data['data'].unique())}")

        print("Creating scaling plot...")
        fig, ax = create_scaling_plot(scaling_data, args.metric)

        print("✅ Plot displayed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
