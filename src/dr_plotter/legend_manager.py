from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from matplotlib.lines import Line2D


@dataclass
class LegendEntry:
    artist: Any
    label: str
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


class ProxyArtistFactory:
    @staticmethod
    def create_for_channel(entry: LegendEntry) -> Any:
        if entry.visual_channel == "hue":
            if hasattr(entry.artist, "get_color"):
                return Line2D(
                    [0],
                    [0],
                    color=entry.artist.get_color(),
                    linewidth=2,
                    linestyle="-",
                    label=entry.label,
                )
        elif entry.visual_channel == "style":
            if hasattr(entry.artist, "get_linestyle"):
                return Line2D(
                    [0],
                    [0],
                    color="black",
                    linestyle=entry.artist.get_linestyle(),
                    linewidth=2,
                    label=entry.label,
                )
        elif entry.visual_channel == "size":
            marker_size = 8
            if entry.channel_value is not None:
                try:
                    marker_size = float(entry.channel_value) * 2
                except (ValueError, TypeError):
                    pass
            return Line2D(
                [0],
                [0],
                marker="o",
                markersize=marker_size,
                color="black",
                linestyle="",
                label=entry.label,
            )

        return entry.artist


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

        if hasattr(self.fm, "rows") and hasattr(self.fm, "cols"):
            if self.fm.rows > 1 or self.fm.cols > 1:
                return "figure_below"

        unique_channels = self._get_unique_channels()
        if len(unique_channels) > 1:
            return "grouped_by_channel"

        return "per_axes"

    def _get_unique_channels(self) -> Set[str]:
        channels = set()
        for entry in self.registry.get_unique_entries():
            if entry.visual_channel:
                channels.add(entry.visual_channel)
        return channels

    def _create_figure_legend(self) -> None:
        entries = self.registry.get_unique_entries()
        if not entries:
            return

        handles = []
        labels = []

        for entry in entries:
            proxy = ProxyArtistFactory.create_for_channel(entry)
            handles.append(proxy)
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

        handles = []
        labels = []

        for entry in entries:
            proxy = ProxyArtistFactory.create_for_channel(entry)
            handles.append(proxy)
            labels.append(entry.label)

        if hasattr(self.fm, "axes"):
            if hasattr(self.fm.axes, "flat"):
                for ax in self.fm.axes.flat:
                    if handles:
                        ax.legend(handles, labels)
            else:
                if handles:
                    self.fm.axes.legend(handles, labels)

    def _create_grouped_legends(self) -> None:
        channels = self._get_unique_channels()

        for i, channel in enumerate(channels):
            entries = self.registry.get_by_channel(channel)
            if not entries:
                continue

            handles = []
            labels = []

            for entry in entries:
                proxy = ProxyArtistFactory.create_for_channel(entry)
                handles.append(proxy)
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
