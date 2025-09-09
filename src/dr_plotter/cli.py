from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig
from dr_plotter.scripting import (
    CLIConfig,
    build_configs,
    dimensional_plotting_cli,
    load_dataset,
    validate_args,
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
@dimensional_plotting_cli(skip_fields={"x", "y"})
def main(
    dataset_path: str,
    x_column: str,
    y_column: str,
    plot_type: str,
    **kwargs: Any,
) -> None:
    df = load_dataset(dataset_path)
    config = CLIConfig()
    if kwargs.get("config"):
        config = CLIConfig.from_yaml(kwargs["config"])
    cli_kwargs = {k: v for k, v in kwargs.items() if k != "config"}
    cli_kwargs.update({"x": x_column, "y": y_column})
    merged_args = config.merge_with_cli_args(cli_kwargs)
    validate_args(df, merged_args)
    configs, unused_kwargs = build_configs(merged_args)
    # Check for invalid parameters
    if unused_kwargs:
        unused_params = ", ".join(unused_kwargs.keys())
        raise click.UsageError(f"Unknown parameters: {unused_params}")

    plot_config = PlotConfig(
        layout=configs["layout"],
        legend=configs["legend"],
        style=configs["style"] if configs["style"].theme else None,
    )

    with FigureManager(plot_config) as fm:
        fm.plot_faceted(df, plot_type, faceting=configs["faceting"])

    dataset_name = Path(dataset_path).stem
    show_or_save_plot(
        fm.fig, kwargs["save_dir"], kwargs["pause"], f"dr_plotter_{dataset_name}"
    )


if __name__ == "__main__":
    main()
