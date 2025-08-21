"""
Base class for all plotter objects.
"""

import pandas as pd

from dr_plotter.consts import METRICS, METRICS_STR
from dr_plotter.legend import Legend
from dr_plotter.plotters.style_engine import StyleEngine
from dr_plotter.theme import BASE_COLORS, BASE_THEME, DR_PLOTTER_STYLE_KEYS


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

        Requires the declarative plotter_name attribute - fails fast if missing.
        """
        super().__init_subclass__(**kwargs)

        # Require plotter_name attribute (fail fast)
        if not hasattr(cls, "plotter_name"):
            raise AttributeError(
                f"{cls.__name__} must define 'plotter_name' class attribute. "
                f"All plotters must follow the declarative pattern."
            )

        # Register the class using the declarative name
        BasePlotter._registry[cls.plotter_name] = cls

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
        Initialize the plotter using declarative configuration.

        Args:
            data: A pandas DataFrame.
            **kwargs: All keyword arguments, including configuration, styling, and grouping params.
        """
        self.raw_data = data
        self.plot_data = None  # Will be set by prepare_data()
        self.kwargs = kwargs
        self.metric_column = None  # Will be set if metrics are melted

        # Extract parameters based on plotter_params
        if hasattr(self.__class__, "plotter_params"):
            for param in self.__class__.plotter_params:
                value = kwargs.get(param)
                if value is not None:
                    # Map to standard names if needed
                    mapped_name = self.__class__.param_mapping.get(param, param)
                    setattr(self, mapped_name, value)
                else:
                    # Set to None for parameters not provided
                    mapped_name = self.__class__.param_mapping.get(param, param)
                    setattr(self, mapped_name, None)

        # Extract grouping parameters (only check *_by params to avoid clash with matplotlib)
        self.hue_by = kwargs.get("hue_by")
        self.style_by = kwargs.get("style_by")
        self.size_by = kwargs.get("size_by")
        self.marker_by = kwargs.get("marker_by")
        self.alpha_by = kwargs.get("alpha_by")

        # Set theme (can be overridden via kwargs)
        self.theme = kwargs.get(
            "theme", getattr(self.__class__, "default_theme", BASE_THEME)
        )

        # Initialize style engine if this plotter uses groupings
        if hasattr(self.__class__, "enabled_channels") and self.__class__.enabled_channels:
            self.style_engine = StyleEngine(self.theme, self.__class__.enabled_channels)

    def prepare_data(self):
        """
        Intelligent data preparation that handles multi-metrics and validation using declarative configuration.

        Returns:
            The prepared data
        """
        # Handle multi-metric melting if y is a list
        if hasattr(self, "y") and isinstance(self.y, list):
            # Build auto-hue groupings dict
            auto_hue_groupings = {
                "hue": self.hue_by,
                "style": self.style_by,
                "size": self.size_by,
                "marker": self.marker_by,
                "alpha": self.alpha_by,
            }

            self.plot_data, self.y, self.metric_column = (
                self._prepare_multi_metric_data(
                    self.y, self.x, auto_hue_groupings
                )
            )

            # Update hue_by if auto-set to METRICS
            if self.metric_column and not self.hue_by:
                self.hue_by = self.metric_column
        else:
            self.plot_data = self.raw_data

        # Validate data using the plotter's validator if specified
        if hasattr(self.__class__, "data_validator") and self.__class__.data_validator:
            # Build validation args dynamically using param_mapping
            validation_kwargs = {"data": self.plot_data}
            
            # Add parameters based on what the plotter declared, using mapped names
            if hasattr(self.__class__, "plotter_params"):
                for param in self.__class__.plotter_params:
                    mapped_name = self.__class__.param_mapping.get(param, param)
                    if hasattr(self, mapped_name):
                        # Use the mapped name as the key for validation
                        validation_kwargs[mapped_name] = getattr(self, mapped_name)
            
            validated = self.__class__.data_validator(**validation_kwargs)
            self.plot_data = validated.data

        # Process grouping parameters with METRICS handling
        self.hue_by = self._process_grouping_params(self.hue_by)
        self.style_by = self._process_grouping_params(self.style_by)
        self.size_by = self._process_grouping_params(self.size_by)
        self.marker_by = self._process_grouping_params(self.marker_by)
        self.alpha_by = self._process_grouping_params(self.alpha_by)

        # Check if we have any groupings (only if channels are enabled)
        if hasattr(self.__class__, "enabled_channels") and self.__class__.enabled_channels:
            self._has_groups = any([
                self.hue_by, self.style_by, self.size_by, self.marker_by, self.alpha_by
            ])
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
        
        # Also filter out plotter-specific parameters
        if hasattr(self.__class__, "plotter_params"):
            filter_keys.extend(self.__class__.plotter_params)
        
        for key in filter_keys:
            plot_kwargs.pop(key, None)
        return plot_kwargs

    def _apply_styling(self, ax, legend):
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
            # Auto-show legend if we have groupings or custom legend entries
            if (hasattr(self, "_has_groups") and self._has_groups) or legend.has_entries():
                if not ax.get_legend():
                    # Use custom legend handles if provided
                    if legend.has_entries():
                        ax.legend(handles=legend.get_handles(), 
                                fontsize=self.theme.get("legend_fontsize"))
                    else:
                        ax.legend(fontsize=self.theme.get("legend_fontsize"))
            elif self._get_style("legend") is True:
                if not ax.get_legend():
                    ax.legend(fontsize=self.theme.get("legend_fontsize"))

    def render(self, ax):
        """
        Intelligent render method that orchestrates the plotting lifecycle.

        Concrete plotters only need to implement _draw() method.
        For plotters that need special grouped positioning, they can also
        implement _draw_simple() and _draw_grouped() methods.
        """
        # Prepare data
        self.prepare_data()
        
        # Create legend builder
        legend = Legend()

        # Check if plotter implements the hybrid pattern
        has_draw_simple = hasattr(self, '_draw_simple')
        has_draw_grouped = hasattr(self, '_draw_grouped')
        
        # Render based on grouping and available methods
        if not self._has_groups:
            # Simple single plot
            plot_kwargs = self._build_single_plot_kwargs()
            if has_draw_simple:
                self._draw_simple(ax, self.plot_data, legend, **plot_kwargs)
            else:
                self._draw(ax, self.plot_data, legend, **plot_kwargs)
        else:
            # Multi-series plot with groupings
            if has_draw_grouped:
                # Use specialized grouped drawing method
                self._render_with_grouped_method(ax, legend)
            else:
                # Use standard grouped rendering
                self._render_grouped(ax, legend)

        # Apply styling (including legend if needed)
        self._apply_styling(ax, legend)

    def _draw(self, ax, data, legend, **kwargs):
        """
        Draw the actual plot. Must be implemented by concrete plotters.
        
        Plotters can implement either:
        - _draw() for simple plotters
        - _draw_simple() and _draw_grouped() for plotters needing special grouped positioning

        Args:
            ax: Matplotlib axes
            data: The data to plot (DataFrame or dict for compound plots)
            legend: Legend builder object for adding custom legend entries
            **kwargs: All plot-specific kwargs
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement either _draw() or _draw_simple()/_draw_grouped() methods"
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

    def _render_grouped(self, ax, legend):
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
                self._draw(ax, group_data, legend, **plot_kwargs)
    
    def _render_with_grouped_method(self, ax, legend):
        """Render using plotter's _draw_grouped method with position information."""
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

        # Group the data
        grouped = self.plot_data.groupby(group_cols)
        n_groups = len(grouped)
        
        # Get all unique x categories for consistent positioning
        x_categories = None
        if hasattr(self, 'x') and self.x:
            x_categories = self.plot_data[self.x].unique()
        
        # Iterate through groups and draw with position info
        for group_index, (name, group_data) in enumerate(grouped):
            # Handle multi-column grouping
            if isinstance(name, tuple):
                group_key = tuple(zip(group_cols, name))
            else:
                group_key = tuple([(group_cols[0], name)])

            # Get styles for this group
            styles = group_styles.get(group_key, {})

            # Build plot kwargs for this group
            plot_kwargs = self._build_group_plot_kwargs(styles, name, group_cols)
            
            # Calculate group position info
            group_position = self._calculate_group_position(group_index, n_groups)
            group_position['x_categories'] = x_categories
            
            # Call the plotter's _draw_grouped method with position info
            self._draw_grouped(ax, group_data, group_position, legend, **plot_kwargs)
    
    def _calculate_group_position(self, group_index, n_groups):
        """Calculate positioning information for grouped plots."""
        width = 0.8 / n_groups  # Total width divided by number of groups
        offset = width * (group_index - n_groups / 2 + 0.5)
        
        return {
            'index': group_index,
            'total': n_groups,
            'width': width,
            'offset': offset
        }

    def _build_group_plot_kwargs(self, styles, name, group_cols):
        """Build kwargs for a grouped plot."""
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

        # Create label - use simple value for single grouping (like hue)
        if isinstance(name, tuple):
            # Check if it's a single-element tuple (single grouping column)
            if len(name) == 1:
                # Single grouping column - just show the value
                plot_kwargs["label"] = str(name[0])
            else:
                # Multiple grouping columns - show which column each value is from
                label_parts = []
                for col, val in zip(group_cols, name):
                    if self.metric_column and col == self.metric_column:
                        label_parts.append(str(val))
                    else:
                        label_parts.append(f"{col}={val}")
                plot_kwargs["label"] = ", ".join(label_parts)
        else:
            # Single grouping column - just show the value
            plot_kwargs["label"] = str(name)

        return plot_kwargs
