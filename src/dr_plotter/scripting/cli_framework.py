"""
Professional CLI framework for dimensional plotting with dr_plotter.

This module provides reusable Click-based CLI components that can be extended
by applications like datadec while maintaining consistency and best practices.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypeVar

import click
import yaml

from dr_plotter.configs import (
    FacetingConfig,
    LayoutConfig,
    LegendConfig,
    PlotConfig,
    StyleConfig,
)
from dr_plotter.scripting.utils import parse_key_value_args

F = TypeVar("F", bound=Callable[..., Any])


class CLIConfig:
    def __init__(self, config_data: dict[str, Any] | None = None) -> None:
        self.data = config_data or {}

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> CLIConfig:
        if isinstance(config_path, str):
            config_path = Path(config_path)
        assert config_path.exists(), f"Config file not found: {config_path}"
        assert config_path.suffix == ".yaml", "Config file must be a YAML file"
        with config_path.open() as f:
            data = yaml.safe_load(f)
        return cls(data)

    def merge_with_cli_args(self, cli_args: dict[str, Any]) -> dict[str, Any]:
        """Simple merge: config provides defaults, CLI overrides when present."""
        merged = {}

        # Start with config values (flat structure matches CLI exactly)
        merged.update(self.data)

        # CLI arguments override config values
        for key, value in cli_args.items():
            if value is not None:
                merged[key] = value

        return merged


def common_faceting_options() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        # Always use str type - column validation happens in validate_columns()
        dimension_type = str
        f = click.option(
            "--rows",
            type=dimension_type,
            help="Dimension to use for row faceting",
        )(f)
        f = click.option(
            "--cols",
            type=dimension_type,
            help="Dimension to use for column faceting",
        )(f)
        f = click.option(
            "--rows-and-cols",
            type=dimension_type,
            help="Dimension to wrap across rows and columns",
        )(f)
        f = click.option(
            "--max-cols",
            type=int,
            default=4,
            help="Maximum columns for wrapping layout",
        )(f)

        f = click.option(
            "--hue-by",
            type=dimension_type,
            help="Dimension for color/line grouping",
        )(f)
        f = click.option(
            "--alpha-by",
            type=dimension_type,
            help="Dimension for transparency grouping",
        )(f)
        f = click.option(
            "--size-by",
            type=dimension_type,
            help="Dimension for size grouping",
        )(f)
        f = click.option(
            "--marker-by",
            type=dimension_type,
            help="Dimension for marker style grouping",
        )(f)
        f = click.option(
            "--style-by",
            type=dimension_type,
            help="Dimension for line style grouping",
        )(f)

        return f

    return decorator


def dimensional_control_options() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = click.option(
            "--fixed",
            multiple=True,
            help="Fixed dimensions: key=value (e.g., --fixed seed=0)",
        )(f)
        f = click.option(
            "--order",
            multiple=True,
            help="Ordered dimensions: key=val1,val2 (e.g., --order params=7B,30B,70B)",
        )(f)
        f = click.option(
            "--exclude",
            multiple=True,
            help="Exclude values: key=val1,val2 (e.g., --exclude params=1B,2B)",
        )(f)
        return f

    return decorator


def layout_options() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = click.option(
            "--subplot-width", type=float, default=3.5, help="Width of each subplot"
        )(f)
        f = click.option(
            "--subplot-height", type=float, default=3.0, help="Height of each subplot"
        )(f)
        f = click.option(
            "--no-auto-titles",
            is_flag=True,
            help="Disable automatic descriptive titles",
        )(f)
        return f

    return decorator


def legend_options() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = click.option(
            "--legend-strategy",
            type=click.Choice(["subplot", "figure", "grouped", "none"]),
            default="subplot",
            help="Legend placement strategy",
        )(f)
        return f

    return decorator


def output_options() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = click.option("--save-dir", help="Directory to save plots")(f)
        f = click.option(
            "--pause", type=int, default=5, help="Display duration in seconds"
        )(f)
        return f

    return decorator


def config_option() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = click.option(
            "--config", type=click.Path(exists=True), help="YAML configuration file"
        )(f)
        return f

    return decorator


def validate_layout_options(ctx: click.Context, **kwargs: Any) -> None:
    rows = kwargs.get("rows")
    cols = kwargs.get("cols")
    rows_and_cols = kwargs.get("rows_and_cols")

    if rows_and_cols is not None and (rows is not None or cols is not None):
        raise click.UsageError(
            "Cannot combine --rows-and-cols with --rows or --cols. Use either"
            " explicit grid (--rows + --cols) or wrapping (--rows-and-cols)."
        )


def build_faceting_config(
    config: CLIConfig,
    x: str = "step",
    y: str = "value",
    exterior_x_label: str = "Steps",
    exterior_y_label: str = "Value",
    **cli_overrides: Any,
) -> FacetingConfig:
    merged = config.merge_with_cli_args(cli_overrides)

    def parse_dimension_value(value: Any) -> Any:
        if isinstance(value, dict):
            return value
        elif isinstance(value, (list, tuple)) and value:
            return parse_key_value_args(value)
        else:
            return None

    fixed_dimensions = parse_dimension_value(merged.get("fixed"))
    ordered_dimensions = parse_dimension_value(merged.get("order"))
    exclude_dimensions = parse_dimension_value(merged.get("exclude"))

    return FacetingConfig(
        x=x,
        y=y,
        rows=merged.get("rows"),
        cols=merged.get("cols"),
        rows_and_cols=merged.get("rows_and_cols"),
        max_cols=merged.get("max_cols") if merged.get("rows_and_cols") else None,
        hue_by=merged.get("hue_by"),
        alpha_by=merged.get("alpha_by"),
        size_by=merged.get("size_by"),
        marker_by=merged.get("marker_by"),
        style_by=merged.get("style_by"),
        fixed_dimensions=fixed_dimensions if fixed_dimensions else None,
        ordered_dimensions=ordered_dimensions if ordered_dimensions else None,
        exclude_dimensions=exclude_dimensions if exclude_dimensions else None,
        subplot_width=merged.get("subplot_width", 3.5),
        subplot_height=merged.get("subplot_height", 3.0),
        auto_titles=not merged.get("no_auto_titles", False),
        row_titles=not merged.get("no_auto_titles", False)
        if merged.get("rows")
        else False,
        col_titles=not merged.get("no_auto_titles", False)
        if merged.get("cols")
        else False,
        exterior_x_label=exterior_x_label,
        exterior_y_label=exterior_y_label,
    )


def build_plot_config(
    config: CLIConfig, theme: str | None = None, **cli_overrides: Any
) -> PlotConfig:
    merged = config.merge_with_cli_args(cli_overrides)

    return PlotConfig(
        layout=LayoutConfig(
            rows=1,
            cols=1,
            tight_layout=True,
            tight_layout_pad=1.0,
        ),
        legend=LegendConfig(strategy=merged.get("legend_strategy", "subplot")),
        style=StyleConfig(theme=theme) if theme else None,
    )


def dimensional_plotting_cli() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = output_options()(f)
        f = legend_options()(f)
        f = layout_options()(f)
        f = dimensional_control_options()(f)
        f = common_faceting_options()(f)
        f = config_option()(f)
        return f

    return decorator
