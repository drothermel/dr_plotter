"""Violin plot data validation."""

from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData
from .base_validation import validate_columns_exist, validate_numeric_columns, validate_categorical_columns


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ViolinPlotData(PlotData):
    """Validated violin plot data."""
    x: Optional[str]
    y: str
    
    def __post_init__(self):
        """Validate columns exist with proper types."""
        columns_to_validate = [self.y]
        if self.x is not None:
            columns_to_validate.append(self.x)
            validate_categorical_columns(self.data, [self.x])
        
        validate_columns_exist(self.data, columns_to_validate)
        validate_numeric_columns(self.data, [self.y])