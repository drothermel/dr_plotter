import itertools
from typing import Any, Dict, Tuple

from dr_plotter.theme import Theme
from dr_plotter.types import VisualChannel


class CycleConfig:
    def __init__(self, theme: Theme) -> None:
        self.theme = theme
        self._cycles = self._create_cycles()
        self._value_assignments: Dict[Tuple[VisualChannel, Any], Any] = {}

    def _create_cycles(self) -> Dict[str, Any]:
        return {
            "color": itertools.cycle(self.theme.get("color_cycle")),
            "linestyle": itertools.cycle(self.theme.get("linestyle_cycle")),
            "marker": itertools.cycle(self.theme.get("marker_cycle")),
            "size": itertools.cycle([1.0, 1.5, 2.0, 2.5]),
            "alpha": itertools.cycle([1.0, 0.7, 0.5, 0.3]),
        }

    def get_style_for(self, channel: VisualChannel, value: Any) -> Any:
        cache_key = (channel, value)

        if cache_key in self._value_assignments:
            return self._value_assignments[cache_key]

        style_attr = self._get_style_attribute_for_channel(channel)
        assigned_style = next(self._cycles[style_attr])
        self._value_assignments[cache_key] = assigned_style
        return assigned_style

    def _get_style_attribute_for_channel(self, channel: VisualChannel) -> str:
        channel_to_attr = {
            "hue": "color",
            "style": "linestyle",
            "marker": "marker",
            "size": "size",
            "alpha": "alpha",
        }
        return channel_to_attr[channel]

    def get_default_styles(self) -> Dict[str, Any]:
        return {
            "color": self.get_style_for("hue", "default"),
            "linestyle": self.get_style_for("style", "default"),
        }

    def get_styled_value_for_channel(
        self, channel: VisualChannel, value: Any
    ) -> Dict[str, Any]:
        if channel == "hue":
            return {"color": self.get_style_for("hue", value)}
        elif channel == "style":
            return {"linestyle": self.get_style_for("style", value)}
        elif channel == "marker":
            return {"marker": self.get_style_for("marker", value)}
        elif channel == "size":
            return {"size_mult": self.get_style_for("size", value)}
        elif channel == "alpha":
            return {"alpha": self.get_style_for("alpha", value)}
        return {}
