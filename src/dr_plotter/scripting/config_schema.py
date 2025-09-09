"""
Configuration schema and examples for dimensional plotting CLI.

Provides structured YAML configuration support with validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Union
from pathlib import Path
import yaml

# Example configuration that mirrors dr_plotter config objects
# Flat configuration structure matching CLI parameters exactly
EXAMPLE_CONFIG = {
    # Faceting parameters (NEW NAMES)
    "rows_by": None,
    "cols_by": None,
    "wrap_by": "model_size",
    "max_cols": 4,
    "hue_by": "dataset",
    "alpha_by": "seed",
    "size_by": None,
    "marker_by": None,
    "style_by": None,
    "fixed": {"metric": "loss"},
    "order": {"model_size": ["1B", "7B", "30B", "70B", "180B"]},
    "exclude": {"dataset": ["deprecated_data"]},
    # Layout parameters (NOW CONNECTED)
    "rows": 1,
    "cols": 1,
    "figsize": [12.0, 8.0],
    "tight_layout": True,
    "tight_layout_pad": 1.0,
    # Subplot sizing parameters
    "subplot_width": 3.5,
    "subplot_height": 3.0,
    "auto_titles": True,
    # Legend parameters
    "legend_strategy": "grouped",
    # Output parameters
    "save_dir": "./plots",
    "pause": 5,
}

MINIMAL_CONFIG = {
    "wrap_by": "params",  # NEW NAME
    "hue_by": "data",
    "fixed": {"metric": "pile-valppl"},
    "legend_strategy": "figure",
}


def write_example_config(path: Union[str, Path], minimal: bool = False) -> None:
    """Write an example configuration file."""
    config = MINIMAL_CONFIG if minimal else EXAMPLE_CONFIG

    with open(path, "w") as f:
        f.write("# dr_plotter dimensional plotting configuration\n")
        f.write("# Flat structure matches CLI parameters exactly\n\n")
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def validate_config(config_data: Dict[str, Any]) -> List[str]:
    """Validate flat configuration structure and return any errors."""
    errors = []

    # Valid top-level keys in flat structure
    valid_keys = {
        # Faceting parameters (NEW NAMES)
        "rows_by",
        "cols_by",
        "wrap_by",
        "max_cols",
        "hue_by",
        "alpha_by",
        "size_by",
        "marker_by",
        "style_by",
        "fixed",
        "order",
        "exclude",
        # Layout parameters (NOW SUPPORTED)
        "rows",
        "cols",
        "figsize",
        "tight_layout",
        "tight_layout_pad",
        # Subplot sizing parameters
        "subplot_width",
        "subplot_height",
        "auto_titles",
        # Legend parameters
        "legend_strategy",
        # Output parameters
        "save_dir",
        "pause",
    }

    for key in config_data:
        if key not in valid_keys:
            errors.append(f"Unknown configuration key: {key}")

    # Check for conflicting layout options (UPDATED NAMES)
    layout_options = [
        config_data.get("rows_by"),
        config_data.get("cols_by"),
        config_data.get("wrap_by"),
    ]
    specified = [opt for opt in layout_options if opt is not None]
    if len(specified) > 1:
        errors.append(
            "Cannot specify multiple faceting options (rows_by, cols_by, wrap_by)"
        )

    # Validate dimensional control types
    for dim_control in ["fixed", "order", "exclude"]:
        if dim_control in config_data and not isinstance(
            config_data[dim_control], dict
        ):
            errors.append(f"{dim_control} must be a dictionary")

    # Validate legend strategy
    if "legend_strategy" in config_data:
        valid_strategies = ["subplot", "figure", "grouped", "none"]
        if config_data["legend_strategy"] not in valid_strategies:
            errors.append(
                f"Invalid legend strategy: {config_data['legend_strategy']}. "
                f"Must be one of {valid_strategies}"
            )

    return errors


def load_and_validate_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load and validate a configuration file."""
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
    except FileNotFoundError:
        raise ValueError(f"Config file not found: {config_path}")

    errors = validate_config(config_data)
    if errors:
        error_msg = "Configuration validation errors:\n" + "\n".join(
            f"  - {err}" for err in errors
        )
        raise ValueError(error_msg)

    return config_data
