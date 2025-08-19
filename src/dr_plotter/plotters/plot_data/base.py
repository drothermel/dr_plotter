"""Base plot data class."""

from typing import Any
import pandas as pd
from pydantic.dataclasses import dataclass
from pydantic import field_validator, ConfigDict


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PlotData:
    """Base validated plot data container."""
    data: pd.DataFrame
    
    @field_validator('data')
    @classmethod
    def validate_dataframe(cls, v: Any) -> pd.DataFrame:
        """Validate that data is a non-empty pandas DataFrame."""
        if not isinstance(v, pd.DataFrame):
            raise ValueError(
                f"Data must be a pandas DataFrame, got {type(v).__name__}. "
                f"Try converting your data with pd.DataFrame(data)."
            )
        
        if v.empty:
            raise ValueError(
                "DataFrame cannot be empty. Check your data source or filtering logic."
            )
        
        return v