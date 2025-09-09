#!/usr/bin/env python3
"""
Global dr-plotter CLI entry point.

Provides a global command for creating dimensional plots from data files
using the dr_plotter CLI framework.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import pandas as pd

from dr_plotter import FigureManager
from dr_plotter.scripting import (
    CLIConfig,
    build_faceting_config,
    build_plot_config,
    dimensional_plotting_cli,
    validate_layout_options,
)
from dr_plotter.scripting.utils import show_or_save_plot
from dr_plotter.theme import BASE_THEME, FigureStyles, Theme

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
    path = Path(file_path).expanduser()
    assert path.suffix == ".parquet", "Only parquet files are supported"
    assert path.exists(), f"Dataset not found: {path}"
    df = pd.read_parquet(path)
    return df


def validate_columns(df: pd.DataFrame, merged_args: Any) -> None:
    faceting_options = [
        ("rows", merged_args.get("rows")),
        ("cols", merged_args.get("cols")),
        ("rows_and_cols", merged_args.get("rows_and_cols")),
        ("hue_by", merged_args.get("hue_by")),
        ("alpha_by", merged_args.get("alpha_by")),
        ("size_by", merged_args.get("size_by")),
        ("marker_by", merged_args.get("marker_by")),
        ("style_by", merged_args.get("style_by")),
    ]
    for option_name, column_name in faceting_options:
        if column_name and column_name not in df.columns:
            available_cols = ", ".join(sorted(df.columns))
            raise click.UsageError(
                f"Column '{column_name}' for --{option_name.replace('_', '-')} "
                f"not found in dataset. Available columns: {available_cols}"
            )


@click.command()
@click.argument("dataset_path", type=click.Path())
@click.option(
    "--x",
    "x_column",
    help="Column name for x-axis (default: auto-detect from step/time/x)",
)
@click.option(
    "--y", "y_column", help="Column name for y-axis (default: auto-detect from value/y)"
)
@click.option(
    "--plot-type",
    type=click.Choice(["line", "scatter"]),
    default="scatter",
    help="Type of plot to create (default: scatter)",
)
@dimensional_plotting_cli([])  # Always validate faceting columns
def main(
    dataset_path: str,
    x_column: str | None,
    y_column: str | None,
    plot_type: str,
    **kwargs: Any,
) -> None:
    df = load_dataset(dataset_path)
    if not x_column:
        for col in ["step", "time", "x"]:
            if col in df.columns:
                x_column = col
                break
        if not x_column:
            click.echo("❌ Could not auto-detect x column. Please specify with --x")
            return

    if not y_column:
        for col in ["value", "y", "loss", "accuracy"]:
            if col in df.columns:
                y_column = col
                break
        if not y_column:
            click.echo("❌ Could not auto-detect y column. Please specify with --y")
            return

    click.echo(f"Using x='{x_column}', y='{y_column}'")
    if kwargs.get("config"):
        config = CLIConfig.from_yaml(kwargs["config"])
        click.echo(f"✅ Loaded configuration from {kwargs['config']}")
    else:
        config = CLIConfig()
    cli_kwargs = {k: v for k, v in kwargs.items() if k != "config"}
    merged_args = config.merge_with_cli_args(cli_kwargs)
    validate_columns(df, merged_args)
    validate_layout_options(click.get_current_context(), **merged_args)
    faceting_config = build_faceting_config(
        config,
        x=x_column,
        y=y_column,
        exterior_x_label=x_column.title(),
        exterior_y_label=y_column.title(),
        **cli_kwargs,
    )
    plot_config = build_plot_config(config, theme=CLI_THEME, **cli_kwargs)

    with FigureManager(plot_config) as fm:
        if plot_type == "line":
            fm.plot_faceted(df, "line", faceting=faceting_config, linewidth=1.5)
        else:
            fm.plot_faceted(df, "scatter", faceting=faceting_config, s=50, alpha=0.7)

    class Args:
        save_dir = kwargs["save_dir"]
        pause = kwargs["pause"]

    dataset_name = Path(dataset_path).stem
    show_or_save_plot(fm.fig, Args(), f"dr_plotter_{dataset_name}")
    click.echo("✅ dr-plotter completed!")


if __name__ == "__main__":
    main()
