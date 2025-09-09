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


def validate_args(
    df: pd.DataFrame, x_column: str, y_column: str, merged_args: Any
) -> None:
    validate_columns(df, x_column, y_column, merged_args)
    validate_layout_options(click.get_current_context(), **merged_args)


def validate_columns(
    df: pd.DataFrame, x_column: str, y_column: str, merged_args: Any
) -> None:
    column_options = [
        ("x", x_column),
        ("y", y_column),
        ("rows", merged_args.get("rows")),
        ("cols", merged_args.get("cols")),
        ("rows_and_cols", merged_args.get("rows_and_cols")),
        ("hue_by", merged_args.get("hue_by")),
        ("alpha_by", merged_args.get("alpha_by")),
        ("size_by", merged_args.get("size_by")),
        ("marker_by", merged_args.get("marker_by")),
        ("style_by", merged_args.get("style_by")),
    ]
    for option_name, column_name in column_options:
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
    required=True,
    help="Column name for x-axis",
)
@click.option("--y", "y_column", required=True, help="Column name for y-axis")
@click.option(
    "--plot-type",
    type=click.Choice(["line", "scatter"]),
    default="scatter",
    help="Type of plot to create (default: scatter)",
)
@dimensional_plotting_cli()  # Always validate faceting columns in validate_columns()
def main(
    dataset_path: str,
    x_column: str,
    y_column: str,
    plot_type: str,
    **kwargs: Any,
) -> None:
    df = load_dataset(dataset_path)
    config = (
        CLIConfig.from_yaml(kwargs["config"]) if kwargs.get("config") else CLIConfig()
    )
    cli_kwargs = {k: v for k, v in kwargs.items() if k != "config"}
    merged_args = config.merge_with_cli_args(cli_kwargs)
    validate_args(df, x_column, y_column, merged_args)
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

    dataset_name = Path(dataset_path).stem
    show_or_save_plot(
        fm.fig, kwargs["save_dir"], kwargs["pause"], f"dr_plotter_{dataset_name}"
    )
    click.echo("✅ dr-plotter completed!")


if __name__ == "__main__":
    main()
