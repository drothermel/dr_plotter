"""
Professional CLI framework for dimensional plotting with dr_plotter.

This module provides reusable Click-based CLI components that can be extended
by applications like datadec while maintaining consistency and best practices.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union, TypeVar
import click
import yaml
from pathlib import Path

from dr_plotter.configs import (
    FacetingConfig,
    LayoutConfig,
    LegendConfig,
    PlotConfig,
    StyleConfig,
)
from dr_plotter.scripting.utils import parse_key_value_args
from dr_plotter.faceting.dimension_validation import interactive_dimension_validation

F = TypeVar("F", bound=Callable[..., Any])


class CLIConfig:
    """Container for CLI configuration with YAML support."""

    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        self.data = config_data or {}

    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> CLIConfig:
        """Load configuration from YAML file."""
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return cls(data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def merge_with_cli_args(self, cli_args: Dict[str, Any]) -> Dict[str, Any]:
        """Merge config with CLI arguments, giving precedence to CLI."""
        # Start with config values
        merged = {}

        # Map config sections to CLI argument names
        config_mappings = {
            "faceting.rows": "rows",
            "faceting.cols": "cols",
            "faceting.rows_and_cols": "rows_and_cols",
            "faceting.max_cols": "max_cols",
            "faceting.hue_by": "hue_by",
            "faceting.alpha_by": "alpha_by",
            "faceting.size_by": "size_by",
            "faceting.marker_by": "marker_by",
            "faceting.style_by": "style_by",
            "faceting.fixed_dimensions": "fixed",
            "faceting.ordered_dimensions": "order",
            "faceting.exclude_dimensions": "exclude",
            "layout.subplot_width": "subplot_width",
            "layout.subplot_height": "subplot_height",
            "layout.auto_titles": "auto_titles",
            "legend.strategy": "legend_strategy",
            "output.save_dir": "save_dir",
            "output.pause": "pause",
        }

        # Apply config defaults
        for config_key, cli_key in config_mappings.items():
            config_value = self.get(config_key)
            if config_value is not None:
                merged[cli_key] = config_value

        # Override with CLI arguments (only if not None and not empty)
        for key, value in cli_args.items():
            if value is not None and value != () and value != [] and value != "":
                merged[key] = value

        return merged


def common_faceting_options(valid_dimensions: List[str]) -> Callable[[F], F]:
    """Add common faceting options to a Click command."""

    def decorator(f: F) -> F:
        # Layout options
        f = click.option(
            "--rows",
            type=click.Choice(valid_dimensions),
            help="Dimension to use for row faceting",
        )(f)
        f = click.option(
            "--cols",
            type=click.Choice(valid_dimensions),
            help="Dimension to use for column faceting",
        )(f)
        f = click.option(
            "--rows-and-cols",
            type=click.Choice(valid_dimensions),
            help="Dimension to wrap across rows and columns",
        )(f)
        f = click.option(
            "--max-cols",
            type=int,
            default=4,
            help="Maximum columns for wrapping layout",
        )(f)

        # Visual channels
        f = click.option(
            "--hue-by",
            type=click.Choice(valid_dimensions),
            help="Dimension for color/line grouping",
        )(f)
        f = click.option(
            "--alpha-by",
            type=click.Choice(valid_dimensions),
            help="Dimension for transparency grouping",
        )(f)
        f = click.option(
            "--size-by",
            type=click.Choice(valid_dimensions),
            help="Dimension for size grouping",
        )(f)
        f = click.option(
            "--marker-by",
            type=click.Choice(valid_dimensions),
            help="Dimension for marker style grouping",
        )(f)
        f = click.option(
            "--style-by",
            type=click.Choice(valid_dimensions),
            help="Dimension for line style grouping",
        )(f)

        return f

    return decorator


def dimensional_control_options() -> Callable[[F], F]:
    """Add dimensional control options to a Click command."""

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
    """Add layout and styling options to a Click command."""

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
    """Add legend configuration options to a Click command."""

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
    """Add output control options to a Click command."""

    def decorator(f: F) -> F:
        f = click.option("--save-dir", help="Directory to save plots")(f)
        f = click.option(
            "--pause", type=int, default=5, help="Display duration in seconds"
        )(f)

        return f

    return decorator


def config_option() -> Callable[[F], F]:
    """Add YAML config file support to a Click command."""

    def decorator(f: F) -> F:
        f = click.option(
            "--config", type=click.Path(exists=True), help="YAML configuration file"
        )(f)

        return f

    return decorator


def validate_layout_options(ctx: click.Context, **kwargs) -> None:
    """Validate that exactly one layout option is specified."""
    layout_options = [
        kwargs.get("rows"),
        kwargs.get("cols"),
        kwargs.get("rows_and_cols"),
    ]
    specified_layouts = [opt for opt in layout_options if opt is not None]

    if len(specified_layouts) == 0:
        raise click.UsageError(
            "Must specify one of: --rows, --cols, or --rows-and-cols"
        )
    if len(specified_layouts) > 1:
        raise click.UsageError("Specify only one layout option")


def build_faceting_config(
    config: CLIConfig,
    x: str = "step",
    y: str = "value",
    exterior_x_label: str = "Steps",
    exterior_y_label: str = "Value",
    **cli_overrides,
) -> FacetingConfig:
    """Build FacetingConfig from CLI arguments and config file."""
    # Merge config with CLI overrides
    merged = config.merge_with_cli_args(cli_overrides)

    # Parse dimensional control arguments (handle both CLI strings and config dicts)
    def parse_dimension_value(value):
        if isinstance(value, dict):
            return value  # Already parsed from config file
        elif isinstance(value, (list, tuple)) and value:
            return parse_key_value_args(value)  # Parse CLI arguments
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


def build_plot_config(config: CLIConfig, theme=None, **cli_overrides) -> PlotConfig:
    """Build PlotConfig from CLI arguments and config file."""
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


def validate_dimensions_interactive(
    data, faceting_config, allow_skip: bool = True
) -> bool:
    """Wrapper for interactive dimension validation with consistent messaging."""
    click.echo("🔍 Validating dimensional configuration...")

    if not interactive_dimension_validation(
        data, faceting_config, allow_skip=allow_skip
    ):
        click.echo("❌ Aborted by user.")
        return False

    click.echo("✅ Dimensional validation passed.")
    return True


# Complete decorator for standard dimensional plotting CLIs
def dimensional_plotting_cli(valid_dimensions: List[str]) -> Callable[[F], F]:
    """Complete decorator that adds all standard dimensional plotting options."""

    def decorator(f: F) -> F:
        # Apply all option decorators in reverse order (Click requirement)
        f = output_options()(f)
        f = legend_options()(f)
        f = layout_options()(f)
        f = dimensional_control_options()(f)
        f = common_faceting_options(valid_dimensions)(f)
        f = config_option()(f)

        return f

    return decorator
