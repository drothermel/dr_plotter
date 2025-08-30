from typing import Any, Tuple


def check_datadec_available() -> bool:
    try:
        import datadec

        return True
    except ImportError:
        raise ImportError(
            "DataDecide integration requires the 'datadec' optional dependency.\n"
            "Install with: uv add 'dr_plotter[datadec]' or pip install 'dr_plotter[datadec]'"
        ) from None


def get_datadec_functions() -> Tuple[Any, Any, Any]:
    check_datadec_available()
    from datadec import DataDecide
    from datadec.script_utils import select_params, select_data

    return DataDecide, select_params, select_data
