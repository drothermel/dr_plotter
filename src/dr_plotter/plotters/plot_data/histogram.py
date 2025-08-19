"""Histogram data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData
from .base_validation import validate_columns_exist, validate_numeric_columns


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class HistogramData(PlotData):
    """Validated histogram data."""
    x: str
    
    def __post_init__(self):
        """Validate column exists and is numeric."""
        validate_columns_exist(self.data, [self.x])
        validate_numeric_columns(self.data, [self.x])