"""Bump plot data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BumpPlotData(PlotData):
    """Validated bump plot data."""

    x: str
    y: str
    group: str

    _validation_rules = {"x": "any", "y": "numeric", "group": "categorical"}
