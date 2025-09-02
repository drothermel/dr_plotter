from typing import Optional
import math

from dr_plotter.types import ColorTuple, ComparisonValue


DEFAULT_TOLERANCES = {
    "float": 1e-6,
    "color": 1e-6,
    "size": 0.1,
    "alpha": 0.05,
    "position": 1e-6,
}


def get_default_tolerance_for_channel(channel: str) -> float:
    channel_lower = channel.lower()
    if channel_lower in ["size"]:
        return DEFAULT_TOLERANCES["size"]
    elif channel_lower in ["alpha"]:
        return DEFAULT_TOLERANCES["alpha"]
    elif channel_lower in ["hue", "color"]:
        return DEFAULT_TOLERANCES["color"]
    else:
        return DEFAULT_TOLERANCES["float"]


def values_are_equal(
    a: ComparisonValue, b: ComparisonValue, tolerance: Optional[float] = None
) -> bool:
    if tolerance is None:
        tolerance = _get_default_tolerance(a, b)

    if isinstance(a, str):
        return isinstance(b, str) and a == b

    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        return _tuples_are_equal(a, b, tolerance)

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return _floats_are_equal(float(a), float(b), tolerance)

    if type(a) is not type(b):
        return False

    return a == b


def count_unique_values(
    values: list[ComparisonValue], tolerance: Optional[float] = None
) -> set[ComparisonValue]:
    if not values:
        return set()

    if tolerance is None:
        tolerance = _get_default_tolerance(
            values[0], values[0] if len(values) > 1 else values[0]
        )

    unique = set()
    for value in values:
        is_duplicate = False
        for existing in unique:
            if values_are_equal(value, existing, tolerance):
                is_duplicate = True
                break
        if not is_duplicate:
            unique.add(value)
    return unique


def floats_are_equal(val1: float, val2: float, tolerance: Optional[float] = None) -> bool:
    if tolerance is None:
        tolerance = DEFAULT_TOLERANCES["float"]
    return _floats_are_equal(val1, val2, tolerance)


def colors_are_equal(
    color1: ColorTuple, color2: ColorTuple, tolerance: Optional[float] = None
) -> bool:
    if tolerance is None:
        tolerance = DEFAULT_TOLERANCES["color"]
    return _tuples_are_equal(color1, color2, tolerance)


def count_unique_floats(values: list[float], tolerance: Optional[float] = None) -> set[float]:
    if tolerance is None:
        tolerance = DEFAULT_TOLERANCES["float"]
    return count_unique_values(values, tolerance)


def count_unique_colors(
    values: list[ColorTuple], tolerance: Optional[float] = None
) -> set[ColorTuple]:
    if tolerance is None:
        tolerance = DEFAULT_TOLERANCES["color"]
    return count_unique_values(values, tolerance)


def _floats_are_equal(val1: float, val2: float, tolerance: float) -> bool:
    if math.isnan(val1) and math.isnan(val2):
        return True
    if math.isnan(val1) or math.isnan(val2):
        return False
    if math.isinf(val1) and math.isinf(val2):
        return val1 == val2
    if math.isinf(val1) or math.isinf(val2):
        return False
    return abs(val1 - val2) < tolerance


def _tuples_are_equal(
    tuple1: tuple[float, ...], tuple2: tuple[float, ...], tolerance: float
) -> bool:
    if len(tuple1) != len(tuple2):
        return False
    return all(_floats_are_equal(a, b, tolerance) for a, b in zip(tuple1, tuple2))


def _get_default_tolerance(a: ComparisonValue, b: ComparisonValue) -> float:
    if isinstance(a, str):
        return 0.0

    if isinstance(a, (tuple, list)):
        if len(a) >= 3 and all(isinstance(x, (int, float)) for x in a):
            return DEFAULT_TOLERANCES["color"]
        return DEFAULT_TOLERANCES["float"]

    if isinstance(a, (int, float)):
        return DEFAULT_TOLERANCES["float"]

    return 0.0
