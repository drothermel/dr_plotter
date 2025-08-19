"""Contour plot data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData
from .base_validation import validate_columns_exist, validate_numeric_columns


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ContourPlotData(PlotData):
    """Validated contour plot data."""
    x: str
    y: str
    
    def __post_init__(self):
        """Validate columns exist and are numeric."""
        validate_columns_exist(self.data, [self.x, self.y])
        validate_numeric_columns(self.data, [self.x, self.y])