"""
Automatic dimension discovery and validation for dimensional plotting.

Prevents common UX issues like overlapping series from unused dimensions.
"""

from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dr_plotter.configs import FacetingConfig


def discover_categorical_dimensions(
    data: pd.DataFrame, config: FacetingConfig
) -> set[str]:
    """Automatically discover categorical dimensions in the data.

    Uses heuristics to identify columns that should be treated as categorical
    dimensions for plotting purposes.

    Args:
        data: The DataFrame to analyze
        config: Faceting configuration (to exclude x/y axes)

    Returns:
        Set of column names that appear to be categorical dimensions
    """
    dimensions = set()

    # Skip x/y axes - these are continuous plotting dimensions
    skip_columns = {config.x, config.y}

    for col in data.columns:
        if col in skip_columns:
            continue

        unique_count = data[col].nunique()
        total_count = len(data)

        # Heuristics for categorical detection
        is_categorical = (
            data[col].dtype == "object"  # String columns
            or data[col].dtype.name == "category"  # Explicit categorical dtype
            or unique_count < 20  # Low cardinality (configurable threshold)
            or unique_count / total_count < 0.05  # Less than 5% unique values
        )

        if is_categorical:
            dimensions.add(col)

    return dimensions


def get_used_dimensions(config: FacetingConfig) -> set[str]:
    """Extract all dimensions that are explicitly used in the faceting config."""
    used = set()

    # Layout dimensions
    if config.rows:
        used.add(config.rows)
    if config.cols:
        used.add(config.cols)
    if config.rows_and_cols:
        used.add(config.rows_and_cols)

    # Visual channel dimensions
    if config.hue_by:
        used.add(config.hue_by)
    if config.alpha_by:
        used.add(config.alpha_by)
    if config.size_by:
        used.add(config.size_by)
    if config.marker_by:
        used.add(config.marker_by)
    if config.style_by:
        used.add(config.style_by)

    # Fixed/filtered dimensions are also "used"
    if config.fixed_dimensions:
        used.update(config.fixed_dimensions.keys())
    if config.ordered_dimensions:
        used.update(config.ordered_dimensions.keys())
    if config.exclude_dimensions:
        used.update(config.exclude_dimensions.keys())

    return used


def suggest_handling(unused_dimensions: set[str]) -> str:
    """Generate helpful suggestions for handling unused dimensions."""
    if not unused_dimensions:
        return ""

    dim = sorted(unused_dimensions)[0]  # Pick first unused dimension
    suggestions = []

    # Common dimension name patterns
    if "seed" in dim.lower() or "run" in dim.lower():
        suggestions.append(f"--alpha-by {dim} (show variance across seeds)")
        suggestions.append(f"--fixed {dim}=0 (filter to single seed)")
        suggestions.append("--aggregate-seeds (if available in your data loader)")
    elif "batch" in dim.lower() or "step" in dim.lower():
        suggestions.append(f"--fixed {dim}=<value> (filter to specific batch/step)")
    else:
        suggestions.append(f"--alpha-by {dim} (use transparency to show groups)")
        suggestions.append(f"--fixed {dim}=<value> (filter to specific value)")

    return "Consider: " + " or ".join(suggestions)


def validate_dimensions(
    data: pd.DataFrame, config: FacetingConfig
) -> tuple[set[str], set[str]]:
    """Validate dimensional usage and return discovered vs unused dimensions.

    Args:
        data: The DataFrame to validate
        config: Faceting configuration

    Returns:
        Tuple of (all_discovered_dimensions, unused_dimensions)

    Raises:
        ValueError: If critical validation issues are found
    """
    # Discover categorical dimensions automatically
    discovered = discover_categorical_dimensions(data, config)

    # Find what's being used
    used = get_used_dimensions(config)

    # Check for unused dimensions
    unused = discovered - used

    # Validate we found reasonable dimensions
    if not discovered:
        # This might be fine - could be purely continuous data
        pass

    # Check for typos in config (using dimension names not in data)
    invalid_used = used - set(data.columns)
    if invalid_used:
        available = ", ".join(sorted(data.columns))
        raise ValueError(
            f"Configuration references non-existent columns: {invalid_used}. "
            f"Available columns: {available}"
        )

    return discovered, unused


def interactive_dimension_validation(
    data: pd.DataFrame, config: FacetingConfig, allow_skip: bool = True
) -> bool:
    """Perform interactive validation with user prompts.

    Args:
        data: DataFrame to validate
        config: Faceting configuration
        allow_skip: Whether to allow user to skip validation warnings

    Returns:
        True if validation passes or user chooses to continue

    Raises:
        ValueError: For critical validation errors
        SystemExit: If user chooses to abort
    """
    try:
        import click

        has_click = True
    except ImportError:
        has_click = False

    discovered, unused = validate_dimensions(data, config)

    if unused:
        message = f"⚠️  Found unused dimensions: {sorted(unused)}"
        suggestion = suggest_handling(unused)

        if has_click:
            click.echo(message)
            click.echo("These will create overlapping series that may look confusing.")
            if suggestion:
                click.echo(suggestion)

            if allow_skip:
                return click.confirm("Continue anyway?", default=False)
            else:
                click.echo("Please handle these dimensions before proceeding.")
                raise SystemExit(1)
        else:
            # Fallback for non-interactive environments
            warning = f"{message}. These will create overlapping series. {suggestion}"
            if not allow_skip:
                raise ValueError(warning)

    return True
