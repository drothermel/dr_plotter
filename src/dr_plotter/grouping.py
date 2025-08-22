from dataclasses import dataclass, fields
from typing import Any, Dict, List, Optional

from dr_plotter.types import ColName, VisualChannel


@dataclass
class GroupingConfig:
    hue: Optional[ColName] = None
    style: Optional[ColName] = None
    size: Optional[ColName] = None
    marker: Optional[ColName] = None
    alpha: Optional[ColName] = None

    @property
    def channels(self) -> List[VisualChannel]:
        return [field.name for field in fields(self)]

    @property
    def channel_strs(self) -> List[str]:
        return [self.channel_str(channel) for channel in self.channels]

    @property
    def active_channels(self) -> List[VisualChannel]:
        return [channel for channel in self.channels if self[channel] is not None]

    @property
    def active(self) -> Dict[VisualChannel, ColName]:
        return {channel: self[channel] for channel in self.active_channels}

    def channel_str(self, channel: VisualChannel) -> str:
        return f"{channel}_by"

    def get(self, channel: VisualChannel) -> Optional[ColName]:
        return getattr(self, channel, None)

    def set_kwargs(self, kwargs: Dict[str, Any]):
        for channel in self.channels:
            col_name = kwargs.get(self.channel_str(channel))
            if col_name is not None:
                self[channel] = col_name

    def __getitem__(self, channel: VisualChannel) -> Optional[ColName]:
        return self.get(channel)

    def __setitem__(self, channel: VisualChannel, value: Optional[ColName]):
        setattr(self, channel, value)
