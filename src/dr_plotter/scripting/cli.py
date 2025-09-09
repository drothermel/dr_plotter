#!/usr/bin/env python3
"""
Global dr-plotter CLI entry point.

Provides a global command for creating dimensional plots from data files
using the dr_plotter CLI framework.
"""

from __future__ import annotations

import click
import pandas as pd
from pathlib import Path

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


# Global CLI theme for dr-plotter command
CLI_THEME = Theme(
    name="dr_plotter_cli",
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


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load dataset from file."""
    path = Path(file_path).expanduser()
    
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    
    # Load based on file extension
    if path.suffix == '.parquet':
        df = pd.read_parquet(path)
    elif path.suffix == '.csv':
        df = pd.read_csv(path)
    elif path.suffix == '.json':
        df = pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    click.echo(f"Loaded {len(df)} rows from {path}")
    click.echo(f"Columns: {list(df.columns)}")
    
    return df


@click.command()
@click.argument('dataset_path', type=click.Path())
@click.option(
    '--x', 'x_column', 
    help="Column name for x-axis (default: auto-detect from step/time/x)"
)
@click.option(
    '--y', 'y_column',
    help="Column name for y-axis (default: auto-detect from value/y)"
)
@click.option(
    '--dimensions',
    help="Comma-separated list of valid dimension column names (enables validation)"
)
@dimensional_plotting_cli([])  # Empty list - validation handled conditionally
def main(dataset_path: str, x_column: str | None, y_column: str | None, dimensions: str | None, **kwargs):
    """Create dimensional plots from data files using dr_plotter framework.
    
    DATASET_PATH: Path to your data file (.parquet, .csv, or .json)
    
    Examples:
    
        # Basic usage with config file
        dr-plotter ~/data/results.parquet --config my_config.yaml
        
        # Specify columns and dimensions explicitly
        dr-plotter data.parquet --x step --y loss --dimensions "model,dataset,seed" --rows-and-cols model --hue-by dataset
        
        # DataDec example
        dr-plotter ~/drotherm/repos/datadec/data/datadecide/full_eval_melted.parquet --rows-and-cols params --hue-by data
    """
    
    try:
        # Load the dataset
        df = load_dataset(dataset_path)
    except Exception as e:
        click.echo(f"❌ Error loading dataset: {e}")
        return
    
    # Determine x and y columns
    if not x_column:
        for col in ['step', 'time', 'x']:
            if col in df.columns:
                x_column = col
                break
        if not x_column:
            click.echo("❌ Could not auto-detect x column. Please specify with --x")
            return
    
    if not y_column:
        for col in ['value', 'y', 'loss', 'accuracy']:
            if col in df.columns:
                y_column = col
                break
        if not y_column:
            click.echo("❌ Could not auto-detect y column. Please specify with --y")
            return
    
    click.echo(f"Using x='{x_column}', y='{y_column}'")
    
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
    
    # Conditional validation based on --dimensions
    if dimensions:
        # User provided dimensions - do full validation
        valid_dims = [d.strip() for d in dimensions.split(',')]
        click.echo(f"Validating dimensions: {valid_dims}")
        
        # Validate dimensions exist in data
        for dim in valid_dims:
            if dim not in df.columns:
                click.echo(f"❌ Dimension '{dim}' not found in dataset columns: {list(df.columns)}")
                return
        
        # Validate CLI args use valid dimensions
        for key, value in cli_kwargs.items():
            if key in ['rows', 'cols', 'rows_and_cols', 'hue_by', 'alpha_by', 'size_by'] and value:
                if value not in valid_dims:
                    click.echo(f"❌ '{value}' not in specified dimensions: {valid_dims}")
                    return
        
        # Merge config with CLI args for validation  
        merged_args = config.merge_with_cli_args(cli_kwargs)
        
        # Validate layout with merged arguments
        validate_layout_options(click.get_current_context(), **merged_args)
    else:
        # No dimensions specified - skip validation, let faceting crash naturally
        click.echo("⚠️  No --dimensions specified. Skipping validation - errors will crash with clear messages.")
        merged_args = config.merge_with_cli_args(cli_kwargs)

    # Create faceting configuration using framework
    faceting_config = build_faceting_config(
        config,
        x=x_column,
        y=y_column,
        exterior_x_label=x_column.title(),
        exterior_y_label=y_column.title(),
        **cli_kwargs,
    )

    # Skip validate_dimensions_interactive - too many false positives for general use
    # Let natural errors from bad column names provide feedback instead

    # Create plot configuration using framework
    plot_config = build_plot_config(config, theme=CLI_THEME, **cli_kwargs)

    # Generate plot - use line plot for time-series like data, scatter otherwise
    plot_type = "line" if x_column in ['step', 'time', 'epoch'] else "scatter"
    click.echo(f"Creating dimensional {plot_type} plot...")
    
    with FigureManager(plot_config) as fm:
        if plot_type == "line":
            fm.plot_faceted(df, "line", faceting=faceting_config, linewidth=1.5)
        else:
            fm.plot_faceted(df, "scatter", faceting=faceting_config, s=50, alpha=0.7)

    # Handle output
    class Args:
        save_dir = kwargs["save_dir"]
        pause = kwargs["pause"]

    dataset_name = Path(dataset_path).stem
    show_or_save_plot(fm.fig, Args(), f"dr_plotter_{dataset_name}")
    click.echo("✅ dr-plotter completed!")


if __name__ == "__main__":
    main()