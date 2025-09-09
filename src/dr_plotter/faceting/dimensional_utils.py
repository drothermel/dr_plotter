from __future__ import annotations

import re
from typing import Any

import pandas as pd

from dr_plotter.configs import FacetingConfig


def smart_sort_key(value: Any) -> tuple[float, str]:
    """Create sort key that handles numeric strings with units (e.g., 7B, 30B, 70B).
    
    Returns tuple of (numeric_value, original_string) for proper sorting.
    Falls back to string sorting if no numeric pattern is detected.
    """
    str_value = str(value)
    
    # Pattern to match numbers with optional units (7B, 30M, 1.5B, etc.)
    match = re.match(r'^(\d+(?:\.\d+)?)([A-Za-z]*)$', str_value.strip())
    if match:
        numeric_part = float(match.group(1))
        unit_part = match.group(2).upper()
        
        # Apply multipliers for common units
        unit_multipliers = {
            'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12,
            'KB': 1e3, 'MB': 1e6, 'GB': 1e9, 'TB': 1e12
        }
        multiplier = unit_multipliers.get(unit_part, 1)
        
        return (numeric_part * multiplier, str_value)
    
    # Fallback to string sorting
    return (float('inf'), str_value)


def smart_sort_values(values: list[Any]) -> list[Any]:
    """Sort values using smart numeric sorting that handles model sizes like 7B, 30B, 70B."""
    return sorted(values, key=smart_sort_key)


def apply_dimensional_filters(data: pd.DataFrame, config: FacetingConfig) -> pd.DataFrame:
    # Apply fixed dimensions filtering
    if config.fixed_dimensions is not None:
        for dim, value in config.fixed_dimensions.items():
            if dim in data.columns:
                data = data[data[dim] == value]
    
    # Apply ordered dimensions filtering (ordered_dimensions acts as an inclusion filter)
    if config.ordered_dimensions is not None:
        for dim, values in config.ordered_dimensions.items():
            if dim in data.columns:
                data = data[data[dim].isin(values)]
    
    # Apply exclude dimensions filtering
    if config.exclude_dimensions is not None:
        for dim, values in config.exclude_dimensions.items():
            if dim in data.columns:
                data = data[~data[dim].isin(values)]
    
    return data


def resolve_dimension_values(
    data: pd.DataFrame,
    dim: str,
    config: FacetingConfig,
) -> list[str]:
    if config.fixed_dimensions is not None and dim in config.fixed_dimensions:
        return [config.fixed_dimensions[dim]]
    if config.ordered_dimensions is not None and dim in config.ordered_dimensions:
        vals = config.ordered_dimensions[dim]
    else:
        # Use smart sorting for better handling of numeric strings with units
        vals = smart_sort_values(data[dim].unique())
    if config.exclude_dimensions is not None and dim in config.exclude_dimensions:
        vals = [v for v in vals if v not in config.exclude_dimensions[dim]]
    return vals


def generate_dimensional_title(config: FacetingConfig) -> str:
    if config.fixed_dimensions:
        return " ".join(f"{k}={v}" for k, v in config.fixed_dimensions.items())
    return f"{config.y} by {config.x}"
