import importlib.util
from typing import Any


def check_datadec_available() -> bool:
    if importlib.util.find_spec("datadec") is not None:
        return True
    else:
        raise ImportError(
            "DataDecide integration requires the 'datadec' optional dependency.\n"
            "Install with: uv add 'dr_plotter[datadec]' or pip install 'dr_plotter[datadec]'"
        ) from None


def get_datadec_functions() -> tuple[Any, Any, Any]:
    check_datadec_available()
    from datadec import DataDecide
    from datadec.script_utils import select_params, select_data

    return DataDecide, select_params, select_data
