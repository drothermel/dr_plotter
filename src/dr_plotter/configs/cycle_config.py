from typing import Any

from dr_plotter.consts import (
    CHANNEL_TO_ATTR,
    VISUAL_CHANNELS,
    get_cycle_key,
)
from dr_plotter.theme import Theme
from dr_plotter.types import StyleAttrName, VisualChannel, StyleCacheKey


class CycleConfig:
    def __init__(self, theme: Theme) -> None:
        self.theme = theme
        self._cycles: dict[VisualChannel, Any] = {
            ch: self.theme.get(get_cycle_key(ch)) for ch in VISUAL_CHANNELS
        }
        self._value_assignments: dict[StyleCacheKey, Any] = {}

    def get_styled_value_for_channel(
        self, channel: VisualChannel, value: Any
    ) -> dict[StyleAttrName, Any]:
        cache_key: StyleCacheKey = (channel, value)
        attr: StyleAttrName = CHANNEL_TO_ATTR[channel]
        if cache_key in self._value_assignments:
            return {attr: self._value_assignments[cache_key]}

        style_value = next(self._cycles[channel])
        self._value_assignments[cache_key] = style_value
        return {attr: style_value}
