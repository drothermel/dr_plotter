from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union


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
    source_column: Optional[str] = None
    group_key: Dict[str, Any] = field(default_factory=dict)
    plotter_type: str = "unknown"
    artist_type: str = "main"


class LegendRegistry:
    def __init__(self, strategy: Optional[LegendStrategy] = None) -> None:
        self._entries: List[LegendEntry] = []
        self._seen_keys: Set[tuple] = set()
        self.strategy = strategy

    def add_entry(self, entry: LegendEntry) -> None:
        if self._should_use_channel_based_deduplication():
            key = (entry.visual_channel, entry.channel_value)
        else:
            key = (entry.label, id(entry.axis))

        if key not in self._seen_keys:
            self._entries.append(entry)
            self._seen_keys.add(key)

    def _should_use_channel_based_deduplication(self) -> bool:
        if self.strategy is None:
            return False
        shared_strategies = {
            LegendStrategy.GROUPED_BY_CHANNEL,
            LegendStrategy.FIGURE_BELOW,
        }
        return self.strategy in shared_strategies

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
    max_col: int = 4
    spacing: float = 0.1
    remove_axes_legends: bool = True
    channel_titles: Optional[Dict[str, str]] = None

    layout_left_margin: float = 0.0
    layout_bottom_margin: float = 0.15
    layout_right_margin: float = 1.0
    layout_top_margin: float = 0.95

    bbox_y_offset: float = 0.08

    single_legend_x: float = 0.5
    two_legend_left_x: float = 0.25
    two_legend_right_x: float = 0.75
    multi_legend_start_x: float = 0.15
    multi_legend_spacing: float = 0.35


def resolve_legend_config(legend_input: Union[str, LegendConfig]) -> LegendConfig:
    if isinstance(legend_input, str):
        string_mappings = {
            "grouped": LegendConfig(
                strategy=LegendStrategy.GROUPED_BY_CHANNEL, layout_bottom_margin=0.2
            ),
            "subplot": LegendConfig(strategy=LegendStrategy.PER_AXES),
            "figure": LegendConfig(strategy=LegendStrategy.FIGURE_BELOW),
            "none": LegendConfig(strategy=LegendStrategy.NONE),
        }
        assert legend_input in string_mappings, (
            f"Invalid legend string '{legend_input}'. Valid options: {list(string_mappings.keys())}"
        )
        return string_mappings[legend_input]
    return legend_input


class LegendManager:
    def __init__(
        self, figure_manager: Any, config: Optional[LegendConfig] = None
    ) -> None:
        self.fm = figure_manager
        self.config = config or LegendConfig()
        self.registry = LegendRegistry(self.config.strategy)

    def _calculate_ncol(self, num_handles: int) -> int:
        if self.config.ncol is not None:
            return self.config.ncol
        return min(self.config.max_col, num_handles)

    def _contextualize_column_name(self, column_name: str) -> str:
        if column_name.endswith("_by"):
            column_name = column_name[:-3]

        if "_" in column_name:
            words = column_name.split("_")
            return " ".join(word.capitalize() for word in words)

        return column_name.capitalize()

    def generate_channel_title(self, channel: str, entries: List[LegendEntry]) -> str:
        if self.config.channel_titles and channel in self.config.channel_titles:
            return self.config.channel_titles[channel]

        source_columns = [
            e.source_column for e in entries if e.source_column is not None
        ]
        if source_columns:
            unique_sources = list(set(source_columns))
            if len(unique_sources) == 1:
                return self._contextualize_column_name(unique_sources[0])

        return channel.title()

    def calculate_optimal_ncol(
        self, legend_entries: List[LegendEntry], figure_width: Optional[float] = None
    ) -> int:
        if self.config.ncol is not None:
            return self.config.ncol

        num_entries = len(legend_entries)
        if num_entries <= 1:
            return 1

        if figure_width is None:
            figure_width = getattr(self.fm.fig, "get_figwidth", lambda: 10)()

        if num_entries <= 3:
            return num_entries
        elif figure_width >= 12:
            return min(5, num_entries)
        elif figure_width >= 8:
            return min(4, num_entries)
        else:
            return min(3, num_entries)

    def calculate_optimal_positioning(
        self, num_legends: int, legend_index: int, figure_width: Optional[float] = None
    ) -> Tuple[float, float]:
        if figure_width is None:
            figure_width = getattr(self.fm.fig, "get_figwidth", lambda: 10)()

        if num_legends == 1:
            return (self.config.single_legend_x, self.config.bbox_y_offset)
        elif num_legends == 2:
            if legend_index == 0:
                return (self.config.two_legend_left_x, self.config.bbox_y_offset)
            else:
                return (self.config.two_legend_right_x, self.config.bbox_y_offset)
        else:
            if figure_width >= 16:
                spacing = min(0.35, 0.8 / (num_legends - 1))
                start_x = 0.5 - (num_legends - 1) * spacing / 2
            elif figure_width >= 12:
                spacing = min(0.3, 0.7 / (num_legends - 1))
                start_x = 0.5 - (num_legends - 1) * spacing / 2
            else:
                spacing = self.config.multi_legend_spacing
                start_x = self.config.multi_legend_start_x

            bbox_x = start_x + (legend_index * spacing)
            return (bbox_x, self.config.bbox_y_offset)

    def get_error_color(
        self, color_type: str = "face", theme: Optional[Any] = None
    ) -> str:
        assert False, (
            f"Legend proxy creation failed for {color_type}. "
            f"This indicates a problem with legend configuration that should be fixed."
        )

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
            ncol = self._calculate_ncol(len(handles))
            bbox_to_anchor = (self.config.single_legend_x, self.config.bbox_y_offset)
            self.fm.figure.legend(
                handles,
                labels,
                loc=self.config.position,
                bbox_to_anchor=bbox_to_anchor,
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
                legend_position = (
                    "best"
                    if self.config.position == "lower center"
                    else self.config.position
                )
                axis.legend(handles, labels, loc=legend_position)

    def _create_grouped_legends(self) -> None:
        channels = set()
        for entry in self.registry.get_unique_entries():
            if entry.visual_channel:
                channels.add(entry.visual_channel)

        channel_list = sorted(list(channels))

        if self.config.strategy == LegendStrategy.GROUPED_BY_CHANNEL:
            num_legends = len(channel_list)
            legends_to_create = [(i, channel) for i, channel in enumerate(channel_list)]
        elif self.config.strategy == LegendStrategy.FIGURE_BELOW:
            num_legends = 1
            legends_to_create = [(0, None)]
        else:
            return

        for legend_index, channel in legends_to_create:
            if channel is not None:
                entries = self.registry.get_by_channel(channel)
            else:
                entries = self.registry.get_unique_entries()

            if not entries:
                continue

            entries = self._process_entries_by_channel_type(entries)

            handles = []
            labels = []

            for entry in entries:
                handles.append(entry.artist)
                labels.append(entry.label)

            if hasattr(self.fm, "figure") and self.fm.figure and self.fm.figure.axes:
                bbox_to_anchor = self.calculate_optimal_positioning(
                    num_legends, legend_index
                )

                title = None
                if channel:
                    title = self.generate_channel_title(channel, entries)

                legend = self.fm.figure.legend(
                    handles,
                    labels,
                    title=title,
                    loc="upper center",
                    bbox_to_anchor=bbox_to_anchor,
                    ncol=self.calculate_optimal_ncol(entries),
                    frameon=True,
                )
