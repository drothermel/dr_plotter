"""Utilities for DataDecide integration (optional dependency)."""

from typing import Tuple, Any


def check_datadec_available() -> bool:
    """Check if DataDecide is available and provide helpful error."""
    try:
        import datadec  # noqa: F401

        return True
    except ImportError:
        raise ImportError(
            "DataDecide integration requires the 'datadec' optional dependency.\n"
            "Install with: uv add 'dr_plotter[datadec]' or pip install 'dr_plotter[datadec]'"
        ) from None


def get_datadec_functions() -> Tuple[Any, Any, Any]:
    """Get DataDecide functions for direct usage (recommended approach).

    Returns:
        Tuple of (DataDecide, select_params, select_data) for direct usage.

    Example usage:
        DataDecide, select_params, select_data = get_datadec_functions()
        validated_params = select_params(["150M", "1B"])
        validated_data = select_data(["C4", "DCLM-Baseline"])
        dd = DataDecide()
        df = dd.full_eval
    """
    check_datadec_available()
    from datadec import DataDecide
    from datadec.script_utils import select_params, select_data

    return DataDecide, select_params, select_data
