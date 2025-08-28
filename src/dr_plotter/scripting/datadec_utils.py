"""Utilities for DataDecide integration (optional dependency)."""

from typing import Tuple, Any, List


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


def safe_import_datadec() -> Tuple[Any, Any, Any]:
    """Import DataDecide with helpful error if not available."""
    check_datadec_available()
    from datadec import DataDecide
    from datadec.script_utils import select_params, select_data

    return DataDecide, select_params, select_data


def validate_cli_params(
    param_args: List[str], exclude_params: List[str] = None
) -> List[str]:
    """Validate model parameter arguments using DataDecide utilities."""
    _, select_params, _ = safe_import_datadec()
    return select_params(param_args, exclude=exclude_params or [])


def validate_cli_data(data_args: List[str]) -> List[str]:
    """Validate data recipe arguments using DataDecide utilities."""
    _, _, select_data = safe_import_datadec()
    return select_data(data_args)


def get_clean_datadec_df(filter_types: List[str] = None, **kwargs):
    """Get clean, pre-filtered DataFrame from DataDecide."""
    DataDecide, _, _ = safe_import_datadec()
    dd = DataDecide(**kwargs)
    return dd.get_filtered_df(filter_types=filter_types or ["ppl", "max_steps"])
