#!/usr/bin/env python3
"""
Dimensional plotting demo with synthetic scaling data.

This demonstrates the dr_plotter CLI framework and dimensional plotting
capabilities using fake ML scaling data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import click

from dr_plotter import FigureManager
from dr_plotter.scripting import (
    CLIConfig,
    dimensional_plotting_cli,
    validate_layout_options,
    build_faceting_config,
    build_plot_config,
    validate_dimensions_interactive,
)
from dr_plotter.scripting.utils import show_or_save_plot
from dr_plotter.theme import BASE_THEME, Theme, FigureStyles


# 🎨 DEMO THEME - Shows customization patterns
DEMO_THEME = Theme(
    name="scaling_demo",
    parent=BASE_THEME,
    figure_styles=FigureStyles(
        legend_position=(0.5, 0.02),
        multi_legend_positions=[(0.3, 0.02), (0.7, 0.02)],
        subplot_width=3.5,
        subplot_height=3.0,
        row_title_rotation=90,
        legend_frameon=True,
        legend_tight_layout_rect=(0, 0.08, 1, 1),
    ),
)


def generate_scaling_data(n_points: int = 100) -> pd.DataFrame:
    """Generate synthetic ML scaling data for demonstration."""
    np.random.seed(42)  # Reproducible data

    # Model parameters and datasets
    model_sizes = ["1B", "7B", "30B", "70B", "180B"]
    datasets = ["CommonCrawl", "Wikipedia", "Books", "ArXiv"]
    metrics = ["loss", "accuracy", "bleu"]
    seeds = [0, 1, 2]

    data = []
    for model in model_sizes:
        for dataset in datasets:
            for metric in metrics:
                for seed in seeds:
                    # Generate realistic scaling curves
                    steps = np.logspace(1, 5, n_points)  # 10 to 100k steps

                    # Model size effects (larger models perform better)
                    size_multiplier = {
                        "1B": 1.0,
                        "7B": 0.8,
                        "30B": 0.6,
                        "70B": 0.4,
                        "180B": 0.3,
                    }[model]

                    # Dataset effects
                    dataset_offset = {
                        "CommonCrawl": 0.0,
                        "Wikipedia": 0.1,
                        "Books": 0.05,
                        "ArXiv": 0.15,
                    }[dataset]

                    # Metric-specific scaling
                    if metric == "loss":
                        # Loss decreases with training (lower is better)
                        base_values = (
                            size_multiplier
                            * (2.0 + dataset_offset)
                            * np.power(steps, -0.1)
                        )
                        base_values += np.random.normal(0, 0.05, n_points)  # Add noise
                    elif metric == "accuracy":
                        # Accuracy increases with training (higher is better)
                        base_values = (
                            (1 - size_multiplier) * 0.95 * (1 - np.exp(-steps / 10000))
                        )
                        base_values -= dataset_offset * 0.1
                        base_values += np.random.normal(0, 0.02, n_points)
                    else:  # BLEU
                        # BLEU score improvement
                        base_values = (
                            (1 - size_multiplier) * 50 * (1 - np.exp(-steps / 15000))
                        )
                        base_values -= dataset_offset * 2
                        base_values += np.random.normal(0, 1, n_points)

                    # Add seed variation
                    seed_offset = np.random.RandomState(seed).normal(0, 0.02, n_points)
                    values = base_values + seed_offset

                    # Create records
                    for step, value in zip(steps, values):
                        data.append(
                            {
                                "step": int(step),
                                "value": float(value),
                                "model_size": model,
                                "dataset": dataset,
                                "metric": metric,
                                "seed": seed,
                            }
                        )

    return pd.DataFrame(data)


@click.command()
@dimensional_plotting_cli(["model_size", "dataset", "metric", "seed"])
@click.option(
    "--n-points", type=int, default=50, help="Number of data points to generate"
)
def main(**kwargs):
    """Generate and plot synthetic ML scaling data with dimensional faceting."""

    # Load configuration
    config = CLIConfig()
    if kwargs.get("config"):
        try:
            config = CLIConfig.from_yaml(kwargs["config"])
            click.echo(f"✅ Loaded configuration from {kwargs['config']}")
        except Exception as e:
            click.echo(f"❌ Error loading config: {e}")
            return

    # Remove config file path from kwargs since we pass CLIConfig object separately
    cli_kwargs = {k: v for k, v in kwargs.items() if k != "config"}

    # Merge config with CLI args for validation
    merged_args = config.merge_with_cli_args(cli_kwargs)

    # Validate layout with merged arguments
    validate_layout_options(click.get_current_context(), **merged_args)

    # Generate synthetic data
    click.echo(f"Generating {kwargs['n_points']} data points per combination...")
    df = generate_scaling_data(kwargs["n_points"])
    click.echo(f"Generated {len(df)} total data points")

    # Create faceting configuration using framework
    # Remove config file path from kwargs since we pass CLIConfig object separately
    cli_kwargs = {k: v for k, v in kwargs.items() if k != "config"}
    faceting_config = build_faceting_config(
        config,
        x="step",
        y="value",
        exterior_x_label="Training Steps",
        exterior_y_label="Metric Value",
        **cli_kwargs,
    )

    # Validate dimensional usage
    if not validate_dimensions_interactive(df, faceting_config):
        return

    # Create plot configuration using framework
    plot_config = build_plot_config(config, theme=DEMO_THEME, **cli_kwargs)

    # Generate plot
    click.echo("Creating dimensional plot...")
    with FigureManager(plot_config) as fm:
        fm.plot_faceted(df, "line", faceting=faceting_config, linewidth=1.5)

    # Handle output
    class Args:
        save_dir = kwargs["save_dir"]
        pause = kwargs["pause"]

    show_or_save_plot(fm.fig, Args(), "scaling_demo")
    click.echo("✅ Plot completed!")


if __name__ == "__main__":
    main()
