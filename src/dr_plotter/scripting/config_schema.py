"""
Configuration schema and examples for dimensional plotting CLI.

Provides structured YAML configuration support with validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Union
from pathlib import Path
import yaml

# Example configuration that mirrors dr_plotter config objects
EXAMPLE_CONFIG = {
    "faceting": {
        "rows": None,
        "cols": None,
        "rows_and_cols": "model_size",
        "max_cols": 4,
        "hue_by": "dataset",
        "alpha_by": "seed",
        "size_by": None,
        "marker_by": None,
        "style_by": None,
        "fixed_dimensions": {"metric": "loss"},
        "ordered_dimensions": {"model_size": ["1B", "7B", "30B", "70B", "180B"]},
        "exclude_dimensions": {"dataset": ["deprecated_data"]},
    },
    "layout": {"subplot_width": 3.5, "subplot_height": 3.0, "auto_titles": True},
    "legend": {"strategy": "grouped"},
    "output": {"save_dir": "./plots", "pause": 5},
}

MINIMAL_CONFIG = {
    "faceting": {
        "rows_and_cols": "params",
        "hue_by": "data",
        "fixed_dimensions": {"metric": "pile-valppl"},
    },
    "legend": {"strategy": "figure"},
}


def write_example_config(path: Union[str, Path], minimal: bool = False) -> None:
    """Write an example configuration file."""
    config = MINIMAL_CONFIG if minimal else EXAMPLE_CONFIG

    with open(path, "w") as f:
        f.write("# dr_plotter dimensional plotting configuration\n")
        f.write("# This file demonstrates the YAML config structure\n\n")
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def validate_config(config_data: Dict[str, Any]) -> List[str]:
    """Validate configuration structure and return any errors."""
    errors = []

    # Check top-level sections
    valid_sections = {"faceting", "layout", "legend", "output"}
    for section in config_data:
        if section not in valid_sections:
            errors.append(f"Unknown configuration section: {section}")

    # Validate faceting section
    if "faceting" in config_data:
        faceting = config_data["faceting"]

        # Check for conflicting layout options
        layout_options = [
            faceting.get("rows"),
            faceting.get("cols"),
            faceting.get("rows_and_cols"),
        ]
        specified = [opt for opt in layout_options if opt is not None]
        if len(specified) > 1:
            errors.append(
                "Cannot specify multiple layout options (rows, cols, rows_and_cols)"
            )

        # Validate dimensional control types
        for dim_control in [
            "fixed_dimensions",
            "ordered_dimensions",
            "exclude_dimensions",
        ]:
            if dim_control in faceting and not isinstance(faceting[dim_control], dict):
                errors.append(f"{dim_control} must be a dictionary")

    # Validate legend section
    if "legend" in config_data:
        legend = config_data["legend"]
        if "strategy" in legend:
            valid_strategies = ["subplot", "figure", "grouped", "none"]
            if legend["strategy"] not in valid_strategies:
                errors.append(
                    f"Invalid legend strategy: {legend['strategy']}. Must be one of {valid_strategies}"
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
