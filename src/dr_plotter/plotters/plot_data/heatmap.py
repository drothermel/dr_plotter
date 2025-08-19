"""Heatmap data validation."""

from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from .base import PlotData


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class HeatmapData(PlotData):
    """Validated heatmap data (tidy format)."""

    x: str
    y: str
    values: str

    _validation_rules = {"x": "categorical", "y": "categorical", "values": "numeric"}

    def __post_init__(self):
        """Validate columns and pivot compatibility after all fields are set."""
        # First run base validation
        super().__post_init__()
        
        # Then check pivot compatibility
        if self.x and self.y and self.x in self.data.columns and self.y in self.data.columns:
            duplicates = self.data.duplicated(subset=[self.x, self.y])
            if duplicates.any():
                dup_count = duplicates.sum()
                sample_dups = self.data[duplicates].head(3)[[self.x, self.y]]
                raise ValueError(
                    f"Found {dup_count} duplicate x,y combinations that will conflict during pivot. "
                    f"Sample duplicates:\n{sample_dups}\n"
                    f"Consider aggregating with data.groupby(['{self.x}', '{self.y}']).agg({{'{self.values}': 'mean'}}).reset_index()"
                )
