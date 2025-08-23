from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from dr_plotter.channel_metadata import ChannelRegistry


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
        self._seen_labels: Set[str] = set()

    def add_entry(self, entry: LegendEntry) -> None:
        if entry.label not in self._seen_labels:
            self._entries.append(entry)
            self._seen_labels.add(entry.label)

    def get_unique_entries(self) -> List[LegendEntry]:
        return self._entries.copy()

    def get_by_channel(self, channel: str) -> List[LegendEntry]:
        return [e for e in self._entries if e.visual_channel == channel]

    def clear(self) -> None:
        self._entries.clear()
        self._seen_labels.clear()


@dataclass
class LegendConfig:
    mode: str = "auto"
    collect_strategy: str = "smart"
    position: str = "best"
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

    def finalize(self) -> None:
        if self.config.mode == "none":
            return

        strategy = self._determine_strategy()

        if strategy == "figure_below":
            self._create_figure_legend()
        elif strategy == "grouped_by_channel":
            self._create_grouped_legends()
        elif strategy == "per_axes":
            self._create_per_axes_legends()

    def _determine_strategy(self) -> str:
        if self.config.mode != "auto":
            return self.config.mode

        unique_channels = self._get_unique_channels()

        if hasattr(self.fm, "rows") and hasattr(self.fm, "cols"):
            if self.fm.rows > 1 or self.fm.cols > 1:
                if len(unique_channels) > 1:
                    return "per_axes"
                else:
                    return "figure_below"

        if len(unique_channels) > 1:
            return "grouped_by_channel"

        return "per_axes"

    def _get_unique_channels(self) -> Set[str]:
        channels = set()
        for entry in self.registry.get_unique_entries():
            if entry.visual_channel:
                channels.add(entry.visual_channel)
        return channels

    def _process_entries_by_channel_type(
        self, entries: List[LegendEntry]
    ) -> List[LegendEntry]:
        processed = []
        continuous_channels = {}

        for entry in entries:
            if not entry.visual_channel:
                processed.append(entry)
                continue

            spec = ChannelRegistry.get_spec(entry.visual_channel)

            if spec.channel_type == "continuous":
                if entry.visual_channel not in continuous_channels:
                    continuous_channels[entry.visual_channel] = []
                continuous_channels[entry.visual_channel].append(entry)
            else:
                processed.append(entry)

        for channel, channel_entries in continuous_channels.items():
            spec = ChannelRegistry.get_spec(channel)

            if spec.legend_behavior == "min_max":
                processed.extend(self._create_min_max_entries(channel, channel_entries))
            elif spec.legend_behavior == "none":
                pass

        return processed

    def _create_min_max_entries(
        self, channel: str, entries: List[LegendEntry]
    ) -> List[LegendEntry]:
        values = [
            float(e.channel_value) for e in entries if e.channel_value is not None
        ]
        if not values:
            return []

        min_val = min(values)
        max_val = max(values)

        sample_entry = entries[0]
        channel_name = channel.title()

        min_entry = LegendEntry(
            artist=sample_entry.artist,
            label=f"Min {channel_name} ({min_val:.2f})",
            axis=sample_entry.axis,
            visual_channel=channel,
            channel_value=min_val,
            group_key=sample_entry.group_key,
            plotter_type=sample_entry.plotter_type,
            artist_type=sample_entry.artist_type,
        )

        max_entry = LegendEntry(
            artist=sample_entry.artist,
            label=f"Max {channel_name} ({max_val:.2f})",
            axis=sample_entry.axis,
            visual_channel=channel,
            channel_value=max_val,
            group_key=sample_entry.group_key,
            plotter_type=sample_entry.plotter_type,
            artist_type=sample_entry.artist_type,
        )

        return [min_entry, max_entry]

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
                loc="lower center",
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

        # Group entries by axis
        entries_by_axis = {}
        for entry in entries:
            axis = entry.axis
            if axis is not None:
                if axis not in entries_by_axis:
                    entries_by_axis[axis] = []
                entries_by_axis[axis].append(entry)

        # Create legend for each axis with its specific entries
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
                axis.legend(handles, labels)

    def _create_grouped_legends(self) -> None:
        channels = self._get_unique_channels()

        for i, channel in enumerate(channels):
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
                ax = self.fm.figure.axes[0]

                y_offset = -0.15 - (i * self.config.spacing)
                legend = ax.legend(
                    handles,
                    labels,
                    title=channel.title() if channel else None,
                    loc="upper center",
                    bbox_to_anchor=(0.5, y_offset),
                    ncol=min(4, len(handles)),
                    frameon=False,
                )
