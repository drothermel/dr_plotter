from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dr_plotter.configs.positioning_config import PositioningConfig


class LegendStrategy(Enum):
    PER_AXES = "per_axes"
    FIGURE_BELOW = "figure_below"
    GROUPED_BY_CHANNEL = "grouped_by_channel"
    NONE = "none"


@dataclass
class LegendConfig:
    strategy: str = "subplot"
    layout_hint: Optional[str] = None
    collect_strategy: str = "smart"
    position: str = "lower center"
    deduplication: bool = True
    ncol: Optional[int] = None
    max_col: int = 4
    spacing: float = 0.1
    remove_axes_legends: bool = True
    channel_titles: Optional[dict[str, str]] = None
    layout_left_margin: float = 0.0
    layout_bottom_margin: float = 0.15
    layout_right_margin: float = 1.0
    layout_top_margin: float = 0.95
    positioning_config: Optional[PositioningConfig] = None

    def __post_init__(self) -> None:
        self.strategy = self._validate_and_convert_strategy(self.strategy)
        if self.positioning_config is None:
            self.positioning_config = PositioningConfig()

    def _validate_and_convert_strategy(self, strategy: str) -> LegendStrategy:
        string_to_enum = {
            "grouped": LegendStrategy.GROUPED_BY_CHANNEL,
            "subplot": LegendStrategy.PER_AXES,
            "figure": LegendStrategy.FIGURE_BELOW,
            "none": LegendStrategy.NONE,
        }
        assert strategy in string_to_enum, (
            f"Invalid legend strategy '{strategy}'. Valid options: {list(string_to_enum.keys())}"
        )
        return string_to_enum[strategy]
