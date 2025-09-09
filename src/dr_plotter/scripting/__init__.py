from .utils import show_or_save_plot, create_and_render_plot
from .cli_framework import (
    CLIConfig,
    dimensional_plotting_cli,
    validate_layout_options,
    build_configs,
)
from .config_schema import (
    EXAMPLE_CONFIG,
    MINIMAL_CONFIG,
    write_example_config,
    validate_config,
    load_and_validate_config,
)
from .plot_data import experimental_data, matrix_data

__all__ = [
    # Legacy utils
    "create_and_render_plot",
    "show_or_save_plot",
    # CLI Framework
    "CLIConfig",
    "dimensional_plotting_cli",
    "validate_layout_options",
    "build_configs",
    # Config support
    "EXAMPLE_CONFIG",
    "MINIMAL_CONFIG",
    "write_example_config",
    "validate_config",
    "load_and_validate_config",
    # Data generators
    "experimental_data",
    "matrix_data",
]
