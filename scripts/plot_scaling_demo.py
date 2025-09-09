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
from pathlib import Path
from typing import Any

from dr_plotter import FigureManager
from dr_plotter.configs import FacetingConfig, LayoutConfig, LegendConfig, PlotConfig, StyleConfig
from dr_plotter.scripting.utils import parse_key_value_args, show_or_save_plot
from dr_plotter.theme import BASE_THEME, Theme, FigureStyles
from dr_plotter.faceting.dimension_validation import interactive_dimension_validation


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
                    size_multiplier = {"1B": 1.0, "7B": 0.8, "30B": 0.6, "70B": 0.4, "180B": 0.3}[model]
                    
                    # Dataset effects  
                    dataset_offset = {"CommonCrawl": 0.0, "Wikipedia": 0.1, "Books": 0.05, "ArXiv": 0.15}[dataset]
                    
                    # Metric-specific scaling
                    if metric == "loss":
                        # Loss decreases with training (lower is better)
                        base_values = size_multiplier * (2.0 + dataset_offset) * np.power(steps, -0.1)
                        base_values += np.random.normal(0, 0.05, n_points)  # Add noise
                    elif metric == "accuracy":
                        # Accuracy increases with training (higher is better)  
                        base_values = (1 - size_multiplier) * 0.95 * (1 - np.exp(-steps / 10000))
                        base_values -= dataset_offset * 0.1
                        base_values += np.random.normal(0, 0.02, n_points)
                    else:  # BLEU
                        # BLEU score improvement
                        base_values = (1 - size_multiplier) * 50 * (1 - np.exp(-steps / 15000))
                        base_values -= dataset_offset * 2
                        base_values += np.random.normal(0, 1, n_points)
                    
                    # Add seed variation
                    seed_offset = np.random.RandomState(seed).normal(0, 0.02, n_points)
                    values = base_values + seed_offset
                    
                    # Create records
                    for step, value in zip(steps, values):
                        data.append({
                            'step': int(step),
                            'value': float(value), 
                            'model_size': model,
                            'dataset': dataset,
                            'metric': metric,
                            'seed': seed,
                        })
    
    return pd.DataFrame(data)


@click.command()
@click.option('--config', type=click.Path(exists=True), help='YAML configuration file')
@click.option('--rows', type=click.Choice(['model_size', 'dataset', 'metric']), help='Facet by rows')
@click.option('--cols', type=click.Choice(['model_size', 'dataset', 'metric']), help='Facet by columns')  
@click.option('--rows-and-cols', type=click.Choice(['model_size', 'dataset']), help='Wrap dimension across grid')
@click.option('--max-cols', type=int, default=4, help='Max columns for wrapped layout')
@click.option('--hue-by', type=click.Choice(['model_size', 'dataset', 'metric', 'seed']), help='Color grouping')
@click.option('--alpha-by', type=click.Choice(['model_size', 'dataset', 'metric', 'seed']), help='Transparency grouping')
@click.option('--size-by', type=click.Choice(['model_size', 'dataset', 'metric', 'seed']), help='Size grouping')
@click.option('--fixed', multiple=True, help='Fixed dimensions: key=value (e.g., --fixed seed=0)')
@click.option('--order', multiple=True, help='Ordered dimensions: key=val1,val2 (e.g., --order dataset=Wikipedia,Books)')
@click.option('--exclude', multiple=True, help='Exclude values: key=val1,val2')
@click.option('--subplot-width', type=float, default=3.5, help='Subplot width')
@click.option('--subplot-height', type=float, default=3.0, help='Subplot height')
@click.option('--no-auto-titles', is_flag=True, help='Disable automatic titles')
@click.option('--legend-strategy', type=click.Choice(['subplot', 'figure', 'grouped', 'none']), default='subplot')
@click.option('--save-dir', help='Save plots to directory')
@click.option('--pause', type=int, default=5, help='Display duration')
@click.option('--n-points', type=int, default=50, help='Number of data points to generate')
def main(**kwargs):
    """Generate and plot synthetic ML scaling data with dimensional faceting."""
    
    # Handle config file loading (placeholder for now)
    if kwargs.get('config'):
        click.echo(f"Config file support coming soon: {kwargs['config']}")
    
    # Validate layout
    layout_options = [kwargs['rows'], kwargs['cols'], kwargs['rows_and_cols']]
    specified_layouts = [opt for opt in layout_options if opt is not None]
    if len(specified_layouts) == 0:
        raise click.UsageError("Must specify one of: --rows, --cols, or --rows-and-cols")
    if len(specified_layouts) > 1:
        raise click.UsageError("Specify only one layout option")
    
    # Generate synthetic data
    click.echo(f"Generating {kwargs['n_points']} data points per combination...")
    df = generate_scaling_data(kwargs['n_points'])
    click.echo(f"Generated {len(df)} total data points")
    
    # Parse dimensional control arguments
    fixed_dimensions = parse_key_value_args(kwargs['fixed'])
    ordered_dimensions = parse_key_value_args(kwargs['order'])  
    exclude_dimensions = parse_key_value_args(kwargs['exclude'])
    
    # Create faceting configuration
    faceting_config = FacetingConfig(
        x="step",
        y="value", 
        rows=kwargs['rows'],
        cols=kwargs['cols'],
        rows_and_cols=kwargs['rows_and_cols'],
        max_cols=kwargs['max_cols'] if kwargs['rows_and_cols'] else None,
        hue_by=kwargs['hue_by'],
        alpha_by=kwargs['alpha_by'], 
        size_by=kwargs['size_by'],
        fixed_dimensions=fixed_dimensions if fixed_dimensions else None,
        ordered_dimensions=ordered_dimensions if ordered_dimensions else None,
        exclude_dimensions=exclude_dimensions if exclude_dimensions else None,
        subplot_width=kwargs['subplot_width'],
        subplot_height=kwargs['subplot_height'],
        auto_titles=not kwargs['no_auto_titles'],
        row_titles=(not kwargs['no_auto_titles']) if kwargs['rows'] else False,
        col_titles=(not kwargs['no_auto_titles']) if kwargs['cols'] else False,
        exterior_x_label="Training Steps",
        exterior_y_label="Metric Value",
    )
    
    # Validate dimensional usage
    click.echo("Validating dimensional configuration...")
    if not interactive_dimension_validation(df, faceting_config):
        click.echo("Aborted by user.")
        return
    
    # Create plot configuration  
    plot_config = PlotConfig(
        layout=LayoutConfig(
            rows=1, cols=1,
            tight_layout=True,
            tight_layout_pad=1.0,
        ),
        legend=LegendConfig(strategy=kwargs['legend_strategy']),
        style=StyleConfig(theme=DEMO_THEME),
    )
    
    # Generate plot
    click.echo("Creating dimensional plot...")
    with FigureManager(plot_config) as fm:
        fm.plot_faceted(df, "line", faceting=faceting_config, linewidth=1.5)
    
    # Handle output
    class Args:
        save_dir = kwargs['save_dir']
        pause = kwargs['pause']
    
    show_or_save_plot(fm.fig, Args(), "scaling_demo")
    click.echo("✅ Plot completed!")


if __name__ == "__main__":
    main()