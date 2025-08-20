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
                f"Unknown plot type: '{plot_type}'. "
                f"Available types: {available}"
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

    def __init__(self, data, **kwargs):
        """
        Initialize the plotter.

        Args:
            data: A pandas DataFrame.
            **kwargs: All keyword arguments, including styling.
        """
        self.raw_data = data
        self.plot_data = None  # Will be set by prepare_data()
        self.kwargs = kwargs
        self.theme = BASE_THEME  # Default theme
        self.metric_column = None  # Will be set if metrics are melted

    def prepare_data(self):
        """
        Prepare and validate data for plotting.

        This method creates a validated PlotData object and performs any necessary
        preprocessing. Subclasses should override this method to create their
        specific PlotData dataclass which handles validation automatically.

        Returns:
            The prepared data
        """
        # Base implementation just sets plot_data to raw_data
        # Subclasses will override to create specific PlotData dataclasses
        self.plot_data = self.raw_data
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
        self, data, hue_by=None, style_by=None, size_by=None, marker_by=None, alpha_by=None
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
        The core method to draw the plot on a matplotlib Axes object.
        """
        raise NotImplementedError(
            "The render method must be implemented by subclasses."
        )
