"""
Configuration schema and examples for dimensional plotting CLI.

Provides structured YAML configuration support with validation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

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


def validate_config(config_data: dict[str, Any]) -> list[str]:
    from dr_plotter.scripting.cli_framework import build_configs

    try:
        configs, unused_kwargs = build_configs(config_data)

        # Any remaining unused kwargs are invalid
        if unused_kwargs:
            return [f"Unknown configuration key: {key}" for key in unused_kwargs]

        return []

    except Exception as e:
        return [f"Configuration validation failed: {e!s}"]


def load_and_validate_config(config_path: str | Path) -> dict[str, Any]:
    config_path = Path(config_path)
    with config_path.open() as f:
        config_data = yaml.safe_load(f)
    errors = validate_config(config_data)
    assert len(errors) == 0, " ".join(errors)
    return config_data
