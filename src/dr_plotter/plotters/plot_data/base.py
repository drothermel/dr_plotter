"""Base plot data class."""

from typing import Any, Dict, ClassVar
import pandas as pd
from pydantic.dataclasses import dataclass
from pydantic import field_validator, ConfigDict


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PlotData:
    """Base validated plot data container with configurable column validation."""

    data: pd.DataFrame

    # Subclasses override this class variable to specify validation requirements
    _validation_rules: ClassVar[Dict[str, str]] = {}

    @field_validator("data", mode="after")
    @classmethod
    def validate_dataframe_and_columns(cls, v: Any) -> pd.DataFrame:
        """Validate DataFrame - basic validation only since we can't access other fields yet."""
        # Basic DataFrame validation
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

    def __post_init__(self):
        """Validate columns after all fields are set."""
        # Apply validation rules from subclass
        for field_name, rule in self._validation_rules.items():
            # Get the field value from the instance
            field_value = getattr(self, field_name, None)

            # Skip if field is None (for Optional fields)
            if field_value is None:
                continue

            # Check column exists
            if field_value not in self.data.columns:
                raise ValueError(
                    f"Column '{field_value}' not found in data. "
                    f"Available columns: {list(self.data.columns)}. "
                    f"Check your column names for typos or case sensitivity."
                )

            # Apply type validation based on rule
            if rule == "any":
                # Skip validation - any type allowed
                continue
            elif rule == "numeric":
                if not pd.api.types.is_numeric_dtype(self.data[field_value]):
                    sample = self.data[field_value].head(3).tolist()
                    raise ValueError(
                        f"Column '{field_value}' should be numeric but contains: {sample}. "
                        f"Try converting with pd.to_numeric(data['{field_value}'], errors='coerce')."
                    )
            elif rule == "categorical":
                # Categorical validation - check if suitable for categorical plotting based on uniqueness
                unique_count = self.data[field_value].nunique()
                if unique_count > 20:
                    sample = self.data[field_value].head(3).tolist()
                    raise ValueError(
                        f"Column '{field_value}' has {unique_count} unique values, too many for categorical plotting. "
                        f"Sample values: {sample}. Consider binning or grouping the data first."
                    )
