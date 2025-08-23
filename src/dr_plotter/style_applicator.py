from typing import Any, Callable, Dict, Optional, Set

from dr_plotter.consts import VISUAL_CHANNELS
from dr_plotter.grouping_config import GroupingConfig
from dr_plotter.theme import Theme

type ComponentName = str
type AttributeName = str
type ComponentSchema = Dict[ComponentName, Set[AttributeName]]
type ComponentStyles = Dict[ComponentName, Dict[str, Any]]
type Phase = str


class StyleApplicator:
    def __init__(
        self,
        theme: Theme,
        kwargs: Dict[str, Any],
        grouping_cfg: Optional[GroupingConfig] = None,
        group_values: Optional[Dict[str, Any]] = None,
        figure_manager: Optional[Any] = None,
    ) -> None:
        self.theme = theme
        self.kwargs = kwargs
        self.grouping_cfg = grouping_cfg
        self.group_values = group_values or {}
        self.figure_manager = figure_manager
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

    def apply_post_processing(self, plot_type: str, artists: Dict[str, Any]) -> None:
        post_styles = self.get_component_styles(plot_type, phase="post")

        for component, styles in post_styles.items():
            processor_key = f"{plot_type}.{component}"
            if processor_key in self._post_processors:
                processor = self._post_processors[processor_key]
                if component in artists:
                    processor(artists[component], styles)

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

        for key, value in component_kwargs.items():
            if key not in attrs:
                resolved_styles[key] = value

        # Special handling: don't include cmap unless c is also present
        if "cmap" in resolved_styles and "c" not in resolved_styles:
            del resolved_styles["cmap"]

        return resolved_styles

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
        # Build visual channel names dynamically from constants
        visual_channel_names = set(VISUAL_CHANNELS)
        visual_channel_by_names = {f"{ch}_by" for ch in VISUAL_CHANNELS}

        # Note: We DON'T include raw visual channel names (hue, style, etc.)
        # when they're used as style values (e.g., alpha=0.6 for transparency)
        # Only the "_by" versions are reserved for grouping
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

        # Special case: if the value is a string, it might be a column name for grouping
        # If it's a number (like alpha=0.6), it's a style value
        if key in visual_channel_names and key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, str):
                # It's a column name for grouping, so it's reserved
                return True
            # It's a numeric value for styling, so it's not reserved
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

        from dr_plotter.plotters.style_engine import StyleEngine

        style_engine = StyleEngine(self.theme, self.figure_manager)
        return style_engine.get_styles_for_group(self.group_values, self.grouping_cfg)

    def _get_component_schema(
        self, plot_type: str, phase: Phase = "plot"
    ) -> ComponentSchema:
        plot_schemas = self._component_schemas.get(plot_type, {})
        if isinstance(plot_schemas, dict) and phase in plot_schemas:
            return plot_schemas[phase]
        elif phase == "plot" and isinstance(plot_schemas, dict):
            # For backward compatibility, if no phase specified, treat as plot phase
            if "plot" not in plot_schemas and "main" in plot_schemas:
                return plot_schemas
        return {"main": set()}

    def _get_group_styled_components(self, plot_type: str) -> Set[str]:
        group_styled_map = {
            "scatter": {"main"},
            "line": {"main"},
            "bar": {"main"},
            "histogram": {"main"},
            "violin": {"violin_body"},
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
        return {
            "scatter": {
                "plot": {
                    "main": {
                        "s",
                        "alpha",
                        "color",
                        "marker",
                        "edgecolors",
                        "linewidths",
                        "c",
                        "cmap",
                        "vmin",
                        "vmax",
                    }
                },
                "post": {
                    "collection": {
                        "sizes",
                        "facecolors",
                        "edgecolors",
                        "linewidths",
                        "alpha",
                    }
                },
            },
            "line": {
                "plot": {
                    "main": {
                        "color",
                        "linewidth",
                        "linestyle",
                        "marker",
                        "markersize",
                        "alpha",
                        "label",
                    }
                }
            },
            "bar": {
                "plot": {
                    "main": {
                        "color",
                        "alpha",
                        "edgecolor",
                        "linewidth",
                        "width",
                        "label",
                    }
                }
            },
            "histogram": {
                "plot": {
                    "main": {
                        "color",
                        "alpha",
                        "edgecolor",
                        "linewidth",
                        "bins",
                        "label",
                        "histtype",
                        "cumulative",
                        "density",
                        "weights",
                        "bottom",
                        "rwidth",
                    }
                },
                "post": {
                    # Histogram returns patches, we could style them post-creation if needed
                    "patches": {"facecolor", "edgecolor", "linewidth", "alpha"}
                },
                "axes": {"properties": {"xlim", "ylim", "xlabel", "ylabel", "title"}},
            },
            "violin": {
                "plot": {
                    "main": {
                        "showmeans",
                        "showmedians",
                        "showextrema",
                        "widths",
                        "points",
                    }
                },
                "post": {
                    "bodies": {"facecolor", "edgecolor", "alpha", "linewidth"},
                    "stats": {"color", "linewidth", "linestyle"},
                },
            },
            "heatmap": {
                "plot": {
                    "main": {
                        "cmap",
                        "vmin",
                        "vmax",
                        "center",
                        "robust",
                        "annot",
                        "fmt",
                        "linewidths",
                        "linecolor",
                        "cbar",
                    }
                }
            },
            "contour": {
                "plot": {
                    "contour": {
                        "levels",
                        "cmap",
                        "alpha",
                        "linewidths",
                        "linestyles",
                        "colors",
                    },
                    "scatter": {"s", "alpha", "color", "marker", "edgecolors"},
                }
            },
            "bump": {
                "plot": {
                    "line": {
                        "color",
                        "linewidth",
                        "linestyle",
                        "marker",
                        "markersize",
                        "alpha",
                    },
                    "text": {"fontsize", "fontweight", "va", "ha"},
                }
            },
        }
