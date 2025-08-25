from typing import Any, Callable, Dict, Optional, Set, TYPE_CHECKING

from dr_plotter.consts import VISUAL_CHANNELS
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.legend_manager import LegendEntry
from dr_plotter.theme import Theme
from dr_plotter.types import ComponentSchema, Phase

if TYPE_CHECKING:
    from dr_plotter.plotters.style_engine import StyleEngine

type ComponentStyles = Dict[str, Dict[str, Any]]


class StyleApplicator:
    def __init__(
        self,
        theme: Theme,
        kwargs: Dict[str, Any],
        grouping_cfg: Optional[GroupingConfig] = None,
        group_values: Optional[Dict[str, Any]] = None,
        figure_manager: Optional[Any] = None,
        plot_type: Optional[str] = None,
        style_engine: Optional["StyleEngine"] = None,
    ) -> None:
        self.theme = theme
        self.kwargs = kwargs
        self.grouping_cfg = grouping_cfg
        self.group_values = group_values or {}
        self.figure_manager = figure_manager
        self.plot_type = plot_type
        self.style_engine = style_engine
        self._component_schemas = self._load_component_schemas()
        self._post_processors: Dict[str, Callable] = {}

    def get_component_styles(
        self, plot_type: str, phase: Phase = "plot"
    ) -> ComponentStyles:
        schema = self._get_component_schema(plot_type, phase)
        component_styles = {}

        for component_name, component_attrs in schema.items():
            styles = self._resolve_component_styles(
                plot_type, component_name, component_attrs, phase
            )
            component_styles[component_name] = styles

        return component_styles

    def get_single_component_styles(
        self, plot_type: str, component: str, phase: Phase = "plot"
    ) -> Dict[str, Any]:
        schema = self._get_component_schema(plot_type, phase)
        if component not in schema:
            return {}

        return self._resolve_component_styles(
            plot_type, component, schema[component], phase
        )

    def register_post_processor(
        self, plot_type: str, component: str, processor: Callable
    ) -> None:
        key = f"{plot_type}.{component}"
        self._post_processors[key] = processor

    def set_group_context(self, group_values: Dict[str, Any]) -> None:
        self.group_values = group_values if group_values is not None else {}

    def clear_group_context(self) -> None:
        self.group_values = {}

    def apply_post_processing(self, plot_type: str, artists: Dict[str, Any]) -> None:
        axes_styles = self.get_component_styles(plot_type, phase="axes")

        for component, styles in axes_styles.items():
            processor_key = f"{plot_type}.{component}"
            if processor_key in self._post_processors:
                processor = self._post_processors[processor_key]
                if component in artists:
                    processor(artists[component], styles)

    def create_legend_entry(
        self,
        artist: Any,
        label: str,
        axis: Any = None,
        artist_type: str = "main",
        explicit_channel: Optional[str] = None,
    ) -> Optional[LegendEntry]:
        if not label:
            return None

        if explicit_channel:
            channel = explicit_channel
            column_name = (
                getattr(self.grouping_cfg, channel, None) if self.grouping_cfg else None
            )
            channel_value = self.group_values.get(column_name) if column_name else None

            if self._should_use_split_legend_label():
                label = str(channel_value) if channel_value is not None else label

        else:
            channel = None
            if self.grouping_cfg and self.grouping_cfg.active_channels:
                channel = (
                    self.grouping_cfg.active_channels_ordered[0]
                    if self.grouping_cfg.active_channels
                    else None
                )
            channel_value = self.group_values.get(channel) if channel else None

        return LegendEntry(
            artist=artist,
            label=label,
            axis=axis,
            visual_channel=channel,
            channel_value=channel_value,
            group_key=self.group_values.copy(),
            plotter_type=self.plot_type or "unknown",
            artist_type=artist_type,
        )

    def _resolve_component_styles(
        self, plot_type: str, component: str, attrs: Set[str], phase: Phase = "plot"
    ) -> Dict[str, Any]:
        resolved_styles = {}

        base_theme_styles = {}
        base_theme_styles.update(self.theme.general_styles)

        if phase == "plot":
            base_theme_styles.update(self.theme.plot_styles)
        elif phase == "post":
            base_theme_styles.update(self.theme.post_styles)
        elif phase == "axes":
            base_theme_styles.update(self.theme.axes_styles)
        elif phase == "figure":
            base_theme_styles.update(self.theme.figure_styles)

        plot_styles = {}
        if plot_type in self._get_plot_specific_themes():
            plot_theme = self._get_plot_specific_themes()[plot_type]
            plot_styles.update(plot_theme.general_styles)

            if phase == "plot":
                plot_styles.update(plot_theme.plot_styles)
            elif phase == "post":
                plot_styles.update(plot_theme.post_styles)
            elif phase == "axes":
                plot_styles.update(plot_theme.axes_styles)
            elif phase == "figure":
                plot_styles.update(plot_theme.figure_styles)

        group_styles = self._get_group_styles_for_component(plot_type, component, phase)

        component_kwargs = self._extract_component_kwargs(component, attrs, phase)

        for attr in attrs:
            if attr in component_kwargs:
                resolved_styles[attr] = component_kwargs[attr]
            elif attr in group_styles:
                resolved_styles[attr] = group_styles[attr]
            elif attr in plot_styles:
                resolved_styles[attr] = plot_styles[attr]
            elif attr in base_theme_styles:
                resolved_styles[attr] = base_theme_styles[attr]
            elif attr == "s" and "size_mult" in group_styles and plot_type == "scatter":
                base_size = base_theme_styles.get("marker_size", 50)
                resolved_styles[attr] = base_size * group_styles["size_mult"]
            elif attr == "color":
                if component == "main":
                    resolved_styles[attr] = base_theme_styles["default_color"]
                else:
                    resolved_styles[attr] = base_theme_styles["text_color"]
            elif attr == "fontsize":
                resolved_styles[attr] = base_theme_styles["text_fontsize"]
            elif attr == "ha":
                resolved_styles[attr] = base_theme_styles["text_ha"]
            elif attr == "va":
                resolved_styles[attr] = base_theme_styles["text_va"]

        for key, value in component_kwargs.items():
            if key not in attrs:
                resolved_styles[key] = value

        if "cmap" in resolved_styles and "c" not in resolved_styles:
            del resolved_styles["cmap"]

        return resolved_styles

    def _should_use_split_legend_label(self) -> bool:
        return (
            self.figure_manager
            and hasattr(self.figure_manager, "legend_config")
            and self.figure_manager.legend_config.strategy.value == "grouped_by_channel"
        )

    def _extract_component_kwargs(
        self, component: str, attrs: Set[str], phase: Phase = "plot"
    ) -> Dict[str, Any]:
        if component == "main":
            extracted = {}
            for k, v in self.kwargs.items():
                if k in attrs and not self._is_reserved_kwarg(k):
                    extracted[k] = v
                elif not self._is_reserved_kwarg(k) and not k.endswith("_by"):
                    extracted[k] = v
            return extracted

        component_prefix = f"{component}_"
        extracted = {}

        for key, value in self.kwargs.items():
            if key.startswith(component_prefix):
                clean_key = key[len(component_prefix) :]
                extracted[clean_key] = value
            elif key in attrs and not any(
                key.startswith(f"{other}_")
                for other in ["contour", "scatter", "violin", "text", "line"]
            ):
                extracted[key] = value

        return extracted

    def _is_reserved_kwarg(self, key: str) -> bool:
        visual_channel_names = set(VISUAL_CHANNELS)
        visual_channel_by_names = {f"{ch}_by" for ch in VISUAL_CHANNELS}
        reserved = {
            "x",
            "y",
            "data",
            "theme",
            "title",
            "xlabel",
            "ylabel",
            "legend",
            "grid",
            "colorbar_label",
            "time_col",
            "category_col",
            "value_col",
            "grouping_cfg",
        }
        reserved.update(visual_channel_by_names)

        if key in visual_channel_names and key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, str):
                return True
            return False

        return key in reserved

    def _get_group_styles_for_component(
        self, plot_type: str, component: str, phase: Phase = "plot"
    ) -> Dict[str, Any]:
        if not self.grouping_cfg or not self.group_values:
            return {}

        group_styled_components = self._get_group_styled_components(plot_type)
        if component not in group_styled_components:
            return {}

        if not self.style_engine:
            from dr_plotter.plotters.style_engine import StyleEngine

            self.style_engine = StyleEngine(self.theme, self.figure_manager)

        return self.style_engine.get_styles_for_group(
            self.group_values, self.grouping_cfg
        )

    def _get_component_schema(
        self, plot_type: str, phase: Phase = "plot"
    ) -> ComponentSchema:
        from dr_plotter.plotters import BasePlotter

        plotter_cls = BasePlotter.get_plotter(plot_type)
        if plotter_cls and hasattr(plotter_cls, "component_schema"):
            return plotter_cls.component_schema.get(phase, {})

        plot_schemas = self._component_schemas.get(plot_type, {})
        if isinstance(plot_schemas, dict) and phase in plot_schemas:
            return plot_schemas[phase]
        elif phase == "plot" and isinstance(plot_schemas, dict):
            if "plot" not in plot_schemas and "main" in plot_schemas:
                return plot_schemas
        return {"main": set()}

    def _get_group_styled_components(self, plot_type: str) -> Set[str]:
        group_styled_map = {
            "scatter": {"main"},
            "line": {"main"},
            "bar": {"main"},
            "histogram": {"main"},
            "violin": {"bodies"},
            "heatmap": {"main"},
            "contour": {"scatter"},
            "bump": {"line"},
        }
        return group_styled_map.get(plot_type, {"main"})

    def _get_plot_specific_themes(self) -> Dict[str, Theme]:
        from dr_plotter.theme import (
            LINE_THEME,
            SCATTER_THEME,
            BAR_THEME,
            HISTOGRAM_THEME,
            VIOLIN_THEME,
            HEATMAP_THEME,
            BUMP_PLOT_THEME,
            CONTOUR_THEME,
        )

        return {
            "line": LINE_THEME,
            "scatter": SCATTER_THEME,
            "bar": BAR_THEME,
            "histogram": HISTOGRAM_THEME,
            "violin": VIOLIN_THEME,
            "heatmap": HEATMAP_THEME,
            "bump": BUMP_PLOT_THEME,
            "contour": CONTOUR_THEME,
        }

    def _load_component_schemas(self) -> Dict[str, Dict[Phase, ComponentSchema]]:
        return {}
