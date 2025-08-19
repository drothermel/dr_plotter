"""Violin plot data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData
from .base_validation import validate_columns_exist, validate_numeric_columns, validate_categorical_columns


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ViolinPlotData(PlotData):
    """Validated violin plot data."""
    x: str
    y: str
    
    def __post_init__(self):
        """Validate columns exist with proper types."""
        validate_columns_exist(self.data, [self.x, self.y])
        validate_categorical_columns(self.data, [self.x])
        validate_numeric_columns(self.data, [self.y])