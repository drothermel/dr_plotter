from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class LegendStrategy(Enum):
    PER_AXES = "per_axes"
    FIGURE_BELOW = "figure_below"
    GROUPED_BY_CHANNEL = "grouped_by_channel"
    NONE = "none"


@dataclass
class LegendEntry:
    artist: Any
    label: str
    axis: Any = None
    visual_channel: Optional[str] = None
    channel_value: Any = None
    group_key: Dict[str, Any] = field(default_factory=dict)
    plotter_type: str = "unknown"
    artist_type: str = "main"


class LegendRegistry:
    def __init__(self) -> None:
        self._entries: List[LegendEntry] = []
        self._seen_keys: Set[tuple] = set()

    def add_entry(self, entry: LegendEntry) -> None:
        key = (entry.label, id(entry.axis))
        if key not in self._seen_keys:
            self._entries.append(entry)
            self._seen_keys.add(key)

    def get_unique_entries(self) -> List[LegendEntry]:
        return self._entries.copy()

    def get_by_channel(self, channel: str) -> List[LegendEntry]:
        return [e for e in self._entries if e.visual_channel == channel]

    def clear(self) -> None:
        self._entries.clear()
        self._seen_keys.clear()


@dataclass
class LegendConfig:
    strategy: LegendStrategy = LegendStrategy.PER_AXES
    collect_strategy: str = "smart"
    position: str = "lower center"
    deduplication: bool = True
    ncol: Optional[int] = None
    spacing: float = 0.1
    remove_axes_legends: bool = True


class LegendManager:
    def __init__(
        self, figure_manager: Any, config: Optional[LegendConfig] = None
    ) -> None:
        self.fm = figure_manager
        self.config = config or LegendConfig()
        self.registry = LegendRegistry()

    def get_error_color(self, color_type: str = "face", theme: Optional[Any] = None) -> str:
        import warnings

        warnings.warn(
            f"Legend proxy creation failed - using error color for {color_type}"
        )

        assert theme is not None, "Theme must be provided for error color access"
        
        if color_type == "edge":
            return theme.general_styles.get("error_edge_color", "#FF0000")
        else:
            return theme.general_styles.get("error_color", "#FF0000")

    def finalize(self) -> None:
        if self.config.strategy == LegendStrategy.NONE:
            return

        strategy = self.config.strategy.value

        if strategy == "figure_below":
            self._create_figure_legend()
        elif strategy == "grouped_by_channel":
            self._create_grouped_legends()
        elif strategy == "per_axes":
            self._create_per_axes_legends()

    def _process_entries_by_channel_type(
        self, entries: List[LegendEntry]
    ) -> List[LegendEntry]:
        return entries

    def _create_figure_legend(self) -> None:
        entries = self.registry.get_unique_entries()

        if not entries:
            return

        entries = self._process_entries_by_channel_type(entries)

        handles = []
        labels = []

        for entry in entries:
            handles.append(entry.artist)
            labels.append(entry.label)

        if hasattr(self.fm, "figure") and self.fm.figure:
            ncol = self.config.ncol or min(4, len(handles))
            self.fm.figure.legend(
                handles,
                labels,
                loc=self.config.position,
                bbox_to_anchor=(0.5, -0.05),
                ncol=ncol,
                frameon=False,
            )

            if self.config.remove_axes_legends:
                for ax in self.fm.figure.axes:
                    legend = ax.get_legend()
                    if legend:
                        legend.remove()

    def _create_per_axes_legends(self) -> None:
        entries = self.registry.get_unique_entries()
        if not entries:
            return

        entries = self._process_entries_by_channel_type(entries)

        entries_by_axis = {}
        for entry in entries:
            axis = entry.axis
            if axis is not None:
                if axis not in entries_by_axis:
                    entries_by_axis[axis] = []
                entries_by_axis[axis].append(entry)

        for axis, axis_entries in entries_by_axis.items():
            if not axis_entries:
                continue

            handles = []
            labels = []
            for entry in axis_entries:
                if entry.artist:
                    handles.append(entry.artist)
                    labels.append(entry.label)

            if handles:
                legend_position = "best" if self.config.position == "lower center" else self.config.position
                axis.legend(handles, labels, loc=legend_position)

    def _create_grouped_legends(self) -> None:
        channels = set()
        for entry in self.registry.get_unique_entries():
            if entry.visual_channel:
                channels.add(entry.visual_channel)

        channel_list = sorted(list(channels))
        
        for i, channel in enumerate(channel_list):
            entries = self.registry.get_by_channel(channel)
            if not entries:
                continue

            entries = self._process_entries_by_channel_type(entries)

            handles = []
            labels = []

            for entry in entries:
                handles.append(entry.artist)
                labels.append(entry.label)

            if hasattr(self.fm, "figure") and self.fm.figure and self.fm.figure.axes:
                if len(channel_list) == 1:
                    bbox_to_anchor = (0.5, -0.1)
                elif len(channel_list) == 2:
                    if i == 0:
                        bbox_to_anchor = (0.25, -0.1)
                    else:
                        bbox_to_anchor = (0.75, -0.1)
                else:
                    bbox_x = 0.15 + (i * 0.35)
                    bbox_to_anchor = (bbox_x, -0.1)
                
                legend = self.fm.figure.legend(
                    handles,
                    labels,
                    title=channel.title() if channel else None,
                    loc="upper center",
                    bbox_to_anchor=bbox_to_anchor,
                    ncol=min(4, len(handles)),
                    frameon=True,
                )
