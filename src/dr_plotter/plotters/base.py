"""
Base class for all plotter objects.
"""

import pandas as pd
import itertools
from dr_plotter.theme import BASE_THEME, DR_PLOTTER_STYLE_KEYS
from dr_plotter.consts import METRICS, METRICS_STR


class BasePlotter:
    """
    A base class for all atomic plotters with multi-series support.

    Includes automatic registration of subclasses for dynamic plotter discovery.
    """

    # Class-level registry to store all plotter subclasses
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register plotter subclasses when they are defined.

        The registry key is derived from the class name:
        - LinePlotter -> "line"
        - ScatterPlotter -> "scatter"
        - CustomPlotter -> "custom"
        """
        super().__init_subclass__(**kwargs)

        # Derive registry key from class name
        # Remove "Plotter" suffix and convert to lowercase
        class_name = cls.__name__
        if class_name.endswith("Plotter"):
            plot_type = class_name[:-7].lower()  # Remove "Plotter" suffix
        else:
            plot_type = class_name.lower()

        # Register the class
        BasePlotter._registry[plot_type] = cls

    @classmethod
    def get_plotter(cls, plot_type):
        """
        Get a plotter class from the registry by plot type name.

        Args:
            plot_type: String name of the plot type (e.g., "line", "scatter")

        Returns:
            The plotter class

        Raises:
            ValueError: If plot_type is not registered
        """
        if plot_type not in cls._registry:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(
                f"Unknown plot type: '{plot_type}'. Available types: {available}"
            )
        return cls._registry[plot_type]

    @classmethod
    def list_plotters(cls):
        """
        List all registered plotter types.

        Returns:
            List of registered plot type names
        """
        return sorted(cls._registry.keys())

    # Default class attributes for declarative configuration
    default_theme = BASE_THEME
    enabled_channels = {}  # Which visual channels this plotter supports
    data_validator = None  # PlotData class for validation

    def __init__(self, data, **kwargs):
        """
        Initialize the plotter with intelligent configuration merging.

        Args:
            data: A pandas DataFrame.
            **kwargs: All keyword arguments, including configuration, styling, and grouping params.
        """
        self.raw_data = data
        self.plot_data = None  # Will be set by prepare_data()
        self.kwargs = kwargs
        self.metric_column = None  # Will be set if metrics are melted

        # Merge class-level defaults with instance-specific overrides
        for key, value in kwargs.items():
            if hasattr(self.__class__, key) and not key.startswith("_"):
                setattr(self, key, value)

        # Set theme (can be overridden via kwargs)
        self.theme = kwargs.get(
            "theme", getattr(self.__class__, "default_theme", BASE_THEME)
        )

        # Extract grouping parameters from kwargs if they exist
        self.hue_by = kwargs.get("hue_by")
        self.style_by = kwargs.get("style_by")
        self.size_by = kwargs.get("size_by")
        self.marker_by = kwargs.get("marker_by")
        self.alpha_by = kwargs.get("alpha_by")

        # Initialize style engine if this plotter uses groupings
        if self.enabled_channels:
            from dr_plotter.plotters.style_engine import StyleEngine

            self.style_engine = StyleEngine(self.theme, self.enabled_channels)

    def prepare_data(self):
        """
        Intelligent data preparation that handles multi-metrics and validation.

        Returns:
            The prepared data
        """
        # Handle multi-metric data if y_param is defined and is a list
        if hasattr(self, "y_param") and hasattr(self, "x"):
            # Build auto-hue groupings dict
            auto_hue_groupings = {}
            if hasattr(self, "hue_by"):
                auto_hue_groupings["hue"] = self.hue_by
            if hasattr(self, "style_by"):
                auto_hue_groupings["style"] = self.style_by
            if hasattr(self, "size_by"):
                auto_hue_groupings["size"] = self.size_by
            if hasattr(self, "marker_by"):
                auto_hue_groupings["marker"] = self.marker_by
            if hasattr(self, "alpha_by"):
                auto_hue_groupings["alpha"] = self.alpha_by

            self.plot_data, self.y, self.metric_column = (
                self._prepare_multi_metric_data(
                    self.y_param, self.x, auto_hue_groupings
                )
            )

            # Update hue_by if auto-set to METRICS
            if self.metric_column and not self.hue_by:
                self.hue_by = self.metric_column
        else:
            self.plot_data = self.raw_data
            if hasattr(self, "y_param"):
                self.y = self.y_param

        # Validate data using the plotter's validator if specified
        if self.data_validator:
            # Build validation args dynamically based on what the plotter has
            validation_kwargs = {"data": self.plot_data}
            
            # Add common plotter attributes if they exist
            for attr in ["x", "y", "values", "time_col", "category_col", "value_col"]:
                if hasattr(self, attr):
                    validation_kwargs[attr] = getattr(self, attr)
            
            # For plotters that use different naming conventions, map them
            if hasattr(self, "y_param") and not hasattr(self, "y"):
                validation_kwargs["y"] = getattr(self, "y_param")
            
            # Map BumpPlotter's category_col to group for validation
            if hasattr(self, "category_col"):
                validation_kwargs["group"] = getattr(self, "category_col")
            
            # For BumpPlotter, use value_col as y for validation (not the computed rank)
            if hasattr(self, "value_col") and hasattr(self, "time_col"):
                validation_kwargs["x"] = getattr(self, "time_col")
                validation_kwargs["y"] = getattr(self, "value_col")
            
            validated = self.data_validator(**validation_kwargs)
            self.plot_data = validated.data

        # Process grouping parameters with METRICS handling
        if hasattr(self, "hue_by"):
            self.hue_by = self._process_grouping_params(self.hue_by)
        if hasattr(self, "style_by"):
            self.style_by = self._process_grouping_params(self.style_by)
        if hasattr(self, "size_by"):
            self.size_by = self._process_grouping_params(self.size_by)
        if hasattr(self, "marker_by"):
            self.marker_by = self._process_grouping_params(self.marker_by)
        if hasattr(self, "alpha_by"):
            self.alpha_by = self._process_grouping_params(self.alpha_by)

        # Check if we have any groupings (only if channels are enabled)
        if self.enabled_channels:
            self._has_groups = any(
                [
                    getattr(self, "hue_by", None),
                    getattr(self, "style_by", None),
                    getattr(self, "size_by", None),
                    getattr(self, "marker_by", None),
                    getattr(self, "alpha_by", None),
                ]
            )
        else:
            self._has_groups = False

        # Call plotter-specific data preparation if it exists
        if hasattr(self, "_prepare_specific_data"):
            specific_data = self._prepare_specific_data()
            if specific_data is not None:
                self.plot_data = specific_data

        return self.plot_data

    def _prepare_multi_metric_data(self, y_param, x_col, auto_hue_groupings=None):
        """
        Unified multi-metric preparation. Handles detection, melting, and auto-hue.

        Args:
            y_param: str or List[str] - the y parameter
            x_col: str - x column name
            auto_hue_groupings: dict - grouping params for auto-hue detection

        Returns:
            tuple: (plot_data_df, final_y_col, metric_column_name)
        """
        if not isinstance(y_param, list):
            # Single metric - return original data
            return self.raw_data, y_param, None

        # Multi-metric path
        # Auto-set hue to METRICS if no other groupings specified
        if auto_hue_groupings and all(v is None for v in auto_hue_groupings.values()):
            auto_hue_groupings["hue"] = METRICS

        # Build id_vars for melting
        id_vars = [
            col for col in self.raw_data.columns if col not in y_param and col != x_col
        ]
        if x_col and x_col not in id_vars:
            id_vars = [x_col] + id_vars

        # Use robust melt method
        melted_df = self._melt_metrics(
            self.raw_data, id_vars, y_param, "_metric", "_value"
        )

        return melted_df, "_value", "_metric"

    def _melt_metrics(
        self, data, id_vars, value_vars, var_name="_metric", value_name="_value"
    ):
        """
        Convert wide format data to long format for multi-metric plotting.

        Args:
            data: DataFrame to melt
            id_vars: Columns to use as ID variables
            value_vars: Columns to melt (the metrics)
            var_name: Name for the metric column
            value_name: Name for the value column
        """
        # Handle case where some value_vars might not exist (wide format)
        existing_value_vars = [col for col in value_vars if col in data.columns]
        missing_value_vars = [col for col in value_vars if col not in data.columns]

        if existing_value_vars:
            # Standard melt for existing columns
            melted = pd.melt(
                data,
                id_vars=id_vars,
                value_vars=existing_value_vars,
                var_name=var_name,
                value_name=value_name,
            )
        else:
            melted = pd.DataFrame()

        # For missing columns, assume they are the value columns themselves (wide format)
        if missing_value_vars:
            wide_data = []
            for metric in missing_value_vars:
                if metric in data.columns:
                    metric_df = data[id_vars + [metric]].copy()
                    metric_df[var_name] = metric
                    metric_df[value_name] = metric_df[metric]
                    wide_data.append(metric_df)

            if wide_data:
                wide_melted = pd.concat(wide_data, ignore_index=True)
                melted = (
                    pd.concat([melted, wide_melted], ignore_index=True)
                    if not melted.empty
                    else wide_melted
                )

        return melted

    def _process_grouping_params(self, param_value):
        """
        Process a grouping parameter, handling METRICS constant.

        Args:
            param_value: The parameter value (could be column name, METRICS, or None)

        Returns:
            Processed column name or None
        """
        if param_value is None:
            return None
        elif param_value is METRICS or param_value == METRICS_STR:
            return self.metric_column
        else:
            return param_value

    def _create_style_cycles(self):
        """Create separate cycles for each visual channel."""
        return {
            "color": itertools.cycle(self.theme.get("color_cycle")),
            "linestyle": itertools.cycle(self.theme.get("linestyle_cycle")),
            "marker": itertools.cycle(self.theme.get("marker_cycle")),
            "size": itertools.cycle([1.0, 1.5, 2.0, 2.5]),  # Size multipliers
            "alpha": itertools.cycle([1.0, 0.7, 0.5, 0.3]),  # Alpha values
        }

    def _get_group_styles(
        self,
        data,
        hue_by=None,
        style_by=None,
        size_by=None,
        marker_by=None,
        alpha_by=None,
    ):
        """
        DEPRECATED: Use StyleEngine.generate_styles() instead.

        This method is kept for backward compatibility during migration.
        """
        from dr_plotter.plotters.style_engine import StyleEngine

        # Create a temporary style engine with all channels enabled
        engine = StyleEngine(self.theme)

        return engine.generate_styles(
            data,
            hue_by=hue_by,
            style_by=style_by,
            size_by=size_by,
            marker_by=marker_by,
            alpha_by=alpha_by,
            shared_context=getattr(self, "kwargs", None),
        )

    def _get_style(self, key, default_override=None):
        """Gets a style value, prioritizing user kwargs over theme defaults."""
        if key in self.kwargs:
            return self.kwargs.get(key)
        return self.theme.get(key, default_override)

    def _filter_plot_kwargs(self):
        """Removes dr_plotter specific keys from self.kwargs."""
        plot_kwargs = self.kwargs.copy()
        # Extended list of keys to filter - now using _by suffixes
        filter_keys = DR_PLOTTER_STYLE_KEYS + [
            "hue_by",
            "style_by",
            "size_by",
            "marker_by",
            "alpha_by",
            "colorbar_label",  # Colorbar customization
            "_figure_manager",  # Color coordination
            "_shared_hue_styles",  # Color coordination
        ]
        for key in filter_keys:
            plot_kwargs.pop(key, None)
        return plot_kwargs

    def _apply_styling(self, ax):
        """Apply high-level styling options to the axes object."""
        ax.set_title(
            self._get_style("title"), fontsize=self.theme.get("title_fontsize")
        )

        xlabel = self._get_style(
            "xlabel",
            self.x.replace("_", " ").title() if hasattr(self, "x") and self.x else None,
        )
        ax.set_xlabel(xlabel, fontsize=self.theme.get("label_fontsize"))

        ylabel = self._get_style(
            "ylabel",
            self.y.replace("_", " ").title() if hasattr(self, "y") and self.y else None,
        )
        ax.set_ylabel(ylabel, fontsize=self.theme.get("label_fontsize"))

        if self._get_style("grid", True):
            ax.grid(True, alpha=self.theme.get("grid_alpha"))
        else:
            ax.grid(False)

        if self._get_style("legend") is True or self._get_style("legend") is None:
            # Auto-show legend if we have groupings
            if hasattr(self, "_has_groups") and self._has_groups:
                if not ax.get_legend():
                    ax.legend(fontsize=self.theme.get("legend_fontsize"))
            elif self._get_style("legend") is True:
                if not ax.get_legend():
                    ax.legend(fontsize=self.theme.get("legend_fontsize"))

    def render(self, ax):
        """
        Intelligent render method that orchestrates the plotting lifecycle.

        Concrete plotters only need to implement _draw() method.
        """
        # Prepare data
        self.prepare_data()

        # Render based on grouping
        if not self._has_groups:
            # Simple single plot
            plot_kwargs = self._build_single_plot_kwargs()
            self._draw(ax, self.plot_data, **plot_kwargs)
        else:
            # Multi-series plot with groupings
            self._render_grouped(ax)

        # Apply styling
        self._apply_styling(ax)

    def _draw(self, ax, data, **kwargs):
        """
        Draw the actual plot. Must be implemented by concrete plotters.

        Args:
            ax: Matplotlib axes
            data: The data to plot (DataFrame or dict for compound plots)
            **kwargs: All plot-specific kwargs
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _draw() method"
        )

    def _build_single_plot_kwargs(self):
        """Build kwargs for a single (non-grouped) plot."""
        plot_kwargs = {}

        # Add common defaults based on plot type
        if hasattr(self, "marker"):
            plot_kwargs["marker"] = self._get_style("marker")
        if hasattr(self, "linestyle"):
            plot_kwargs["linestyle"] = self._get_style("linestyle", "-")
        if hasattr(self, "line_width"):
            plot_kwargs["linewidth"] = self._get_style("line_width")

        # Common style attributes
        plot_kwargs["alpha"] = self._get_style("alpha")
        plot_kwargs["color"] = self._get_style(
            "color", next(self.theme.get("color_cycle"))
        )

        # Add user-specified kwargs
        plot_kwargs.update(self._filter_plot_kwargs())

        # Add label if specified
        if "label" in self.kwargs:
            plot_kwargs["label"] = self.kwargs["label"]

        return plot_kwargs

    def _render_grouped(self, ax):
        """Unified grouped rendering for all plotters that support grouping."""
        # Get group styles using style engine
        group_styles = self.style_engine.generate_styles(
            self.plot_data,
            hue_by=getattr(self, "hue_by", None),
            style_by=getattr(self, "style_by", None),
            size_by=getattr(self, "size_by", None),
            marker_by=getattr(self, "marker_by", None),
            alpha_by=getattr(self, "alpha_by", None),
            shared_context=self.kwargs,
        )

        # Get grouping columns
        group_cols = self.style_engine.get_grouping_columns(
            hue_by=getattr(self, "hue_by", None),
            style_by=getattr(self, "style_by", None),
            size_by=getattr(self, "size_by", None),
            marker_by=getattr(self, "marker_by", None),
            alpha_by=getattr(self, "alpha_by", None),
        )

        if group_cols:
            grouped = self.plot_data.groupby(group_cols)

            for name, group_data in grouped:
                # Create group key for style lookup
                if isinstance(name, tuple):
                    group_key = tuple(zip(group_cols, name))
                else:
                    group_key = tuple([(group_cols[0], name)])

                # Get styles for this group
                styles = group_styles.get(group_key, {})

                # Build plot kwargs for this group
                plot_kwargs = self._build_group_plot_kwargs(styles, name, group_cols)

                # Call the concrete plotter's draw method
                self._draw(ax, group_data, **plot_kwargs)

    def _build_group_plot_kwargs(self, styles, name, group_cols):
        """Build kwargs for a grouped plot."""
        from dr_plotter.theme import BASE_COLORS

        # Use first color if not grouped by hue
        default_color = styles.get("color", BASE_COLORS[0])

        plot_kwargs = {
            "color": default_color,
            "alpha": styles.get("alpha", self._get_style("alpha", 1.0)),
        }

        # Add style-specific attributes based on what this plotter supports
        if "linestyle" in styles:
            plot_kwargs["linestyle"] = styles["linestyle"]
        if "marker" in styles:
            plot_kwargs["marker"] = styles["marker"]
        if "size_mult" in styles:
            # Apply size multiplier to appropriate attribute
            if hasattr(self, "line_width"):
                plot_kwargs["linewidth"] = (
                    self._get_style("line_width", 2.0) * styles["size_mult"]
                )
            elif hasattr(self, "marker_size"):
                plot_kwargs["s"] = (
                    self._get_style("marker_size", 50) * styles["size_mult"]
                )

        # Add user-specified kwargs that aren't group-controlled
        user_kwargs = self._filter_plot_kwargs()
        for k, v in user_kwargs.items():
            if k not in plot_kwargs:
                plot_kwargs[k] = v

        # Create label
        if isinstance(name, tuple):
            label_parts = []
            for col, val in zip(group_cols, name):
                if self.metric_column and col == self.metric_column:
                    label_parts.append(str(val))
                else:
                    label_parts.append(f"{col}={val}")
            plot_kwargs["label"] = ", ".join(label_parts)
        else:
            if self.metric_column and group_cols[0] == self.metric_column:
                plot_kwargs["label"] = str(name)
            else:
                plot_kwargs["label"] = f"{group_cols[0]}={name}"

        return plot_kwargs
