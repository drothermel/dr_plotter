"""Violin plot data validation."""

from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ViolinPlotData(PlotData):
    """Validated violin plot data."""

    x: Optional[str]
    y: str

    _validation_rules = {"x": "categorical", "y": "numeric"}
