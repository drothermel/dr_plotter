from .utils import setup_arg_parser, show_or_save_plot, create_and_render_plot
from .cli_framework import (
    CLIConfig,
    dimensional_plotting_cli,
    common_faceting_options,
    dimensional_control_options,
    layout_options,
    legend_options,
    output_options,
    config_option,
    validate_layout_options,
    build_faceting_config,
    build_plot_config,
    validate_dimensions_interactive,
)
from .config_schema import (
    EXAMPLE_CONFIG,
    MINIMAL_CONFIG,
    write_example_config,
    validate_config,
    load_and_validate_config,
)

__all__ = [
    # Legacy utils
    "create_and_render_plot",
    "setup_arg_parser",
    "show_or_save_plot",
    # CLI Framework
    "CLIConfig",
    "dimensional_plotting_cli",
    "common_faceting_options",
    "dimensional_control_options",
    "layout_options",
    "legend_options",
    "output_options",
    "config_option",
    "validate_layout_options",
    "build_faceting_config",
    "build_plot_config",
    "validate_dimensions_interactive",
    # Config support
    "EXAMPLE_CONFIG",
    "MINIMAL_CONFIG",
    "write_example_config",
    "validate_config",
    "load_and_validate_config",
]
