from typing import Any, Dict, Optional

from dr_plotter.cycle_config import CycleConfig
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.theme import Theme


class StyleEngine:
    def __init__(self, theme: Theme, figure_manager: Optional[Any] = None) -> None:
        self.theme = theme
        self.figure_manager = figure_manager
        self._local_cycle_config = CycleConfig(theme)

    @property
    def cycle_cfg(self) -> CycleConfig:
        if self.figure_manager and self.figure_manager.shared_cycle_config:
            return self.figure_manager.shared_cycle_config
        return self._local_cycle_config

    def get_styles_for_group(
        self, group_values: Dict[str, Any], grouping_cfg: GroupingConfig
    ) -> Dict[str, Any]:
        styles = {}
        for channel, column in grouping_cfg.active.items():
            value = group_values.get(column)
            if value is not None:
                styles.update(
                    self.cycle_cfg.get_styled_value_for_channel(channel, value)
                )
        return styles
