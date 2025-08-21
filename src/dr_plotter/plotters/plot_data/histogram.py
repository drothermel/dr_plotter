"""Histogram data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class HistogramData(PlotData):
    """Validated histogram data."""

    x: str

    _validation_rules = {"x": "numeric"}
