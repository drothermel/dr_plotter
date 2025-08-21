"""Scatter plot data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ScatterPlotData(PlotData):
    """Validated scatter plot data."""

    x: str
    y: str

    _validation_rules = {"x": "numeric", "y": "numeric"}
