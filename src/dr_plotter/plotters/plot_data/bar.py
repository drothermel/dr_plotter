"""Bar plot data validation."""

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from .base import PlotData


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BarPlotData(PlotData):
    """Validated bar plot data."""

    x: str
    y: str

    _validation_rules = {"x": "categorical", "y": "numeric"}
