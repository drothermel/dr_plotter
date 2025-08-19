"""Heatmap data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData
from .base_validation import validate_columns_exist, validate_numeric_columns, validate_categorical_columns


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class HeatmapData(PlotData):
    """Validated heatmap data (tidy format)."""
    x: str
    y: str
    values: str
    
    def __post_init__(self):
        """Validate columns exist with proper types and pivot compatibility."""
        validate_columns_exist(self.data, [self.x, self.y, self.values])
        validate_categorical_columns(self.data, [self.x, self.y])
        validate_numeric_columns(self.data, [self.values])
        self._validate_pivot_compatibility()
    
    def _validate_pivot_compatibility(self):
        """Validate that data can be pivoted successfully."""
        duplicates = self.data.duplicated(subset=[self.x, self.y])
        if duplicates.any():
            dup_count = duplicates.sum()
            sample_dups = self.data[duplicates].head(3)[[self.x, self.y]]
            raise ValueError(
                f"Found {dup_count} duplicate x,y combinations that will conflict during pivot. "
                f"Sample duplicates:\n{sample_dups}\n"
                f"Consider aggregating with data.groupby(['{self.x}', '{self.y}']).agg({{'{self.values}': 'mean'}}).reset_index()"
            )