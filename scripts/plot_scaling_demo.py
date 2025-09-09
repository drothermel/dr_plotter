#!/usr/bin/env python3
"""
Dimensional plotting demo with synthetic scaling data.

This demonstrates the dr_plotter CLI framework and dimensional plotting
capabilities using fake ML scaling data.
"""

from __future__ import annotations

import click

from dr_plotter import FigureManager
from dr_plotter.scripting import (
    CLIConfig,
    ExampleData,
    build_faceting_config,
    build_plot_config,
    dimensional_plotting_cli,
    validate_dimensions_interactive,
    validate_layout_options,
)
from dr_plotter.scripting.utils import show_or_save_plot
from dr_plotter.theme import BASE_THEME, FigureStyles, Theme

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
    df = ExampleData.ml_scaling_data(kwargs["n_points"])
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
