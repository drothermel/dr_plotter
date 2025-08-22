from dataclasses import dataclass, fields
from typing import Any, Dict, List, Optional, Set

from dr_plotter.types import ColName, VisualChannel


@dataclass
class GroupingConfig:
    hue: Optional[ColName] = None
    style: Optional[ColName] = None
    size: Optional[ColName] = None
    marker: Optional[ColName] = None
    alpha: Optional[ColName] = None

    @property
    def channel_strs(self) -> List[str]:
        return [f"{field.name}_by" for field in fields(self)]

    @property
    def active_channels(self) -> Set[VisualChannel]:
        return {
            field.name
            for field in fields(self)
            if getattr(self, field.name) is not None
        }

    @property
    def active(self) -> Dict[VisualChannel, ColName]:
        return {channel: getattr(self, channel) for channel in self.active_channels}

    def set_kwargs(self, kwargs: Dict[str, Any]) -> None:
        for field in fields(self):
            col_name = kwargs.get(f"{field.name}_by")
            if col_name is not None:
                setattr(self, field.name, col_name)

    def validate_against_enabled(self, enabled_channels: Set[VisualChannel]) -> None:
        unsupported = self.active_channels - enabled_channels
        assert len(unsupported) == 0, f"Unsupported groupings: {unsupported}"
