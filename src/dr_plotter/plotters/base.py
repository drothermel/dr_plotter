"""
Base class for all plotter objects.
"""

from ..theme import BASE_THEME, DR_PLOTTER_STYLE_KEYS


class BasePlotter:
    """
    A base class for all atomic plotters.
    """

    def __init__(self, data, **kwargs):
        """
        Initialize the plotter.

        Args:
            data: A pandas DataFrame.
            **kwargs: All keyword arguments, including styling.
        """
        self.data = data
        self.kwargs = kwargs
        self.theme = BASE_THEME  # Default theme

    def _get_style(self, key, default_override=None):
        """Gets a style value, prioritizing user kwargs over theme defaults."""
        if key in self.kwargs:
            return self.kwargs.get(key)
        return self.theme.get(key, default_override)

    def _filter_plot_kwargs(self):
        """Removes dr_plotter specific keys from self.kwargs."""
        plot_kwargs = self.kwargs.copy()
        for key in DR_PLOTTER_STYLE_KEYS:
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

        if self._get_style("legend") is True:
            if not ax.get_legend():
                ax.legend(fontsize=self.theme.get("legend_fontsize"))

    def render(self, ax):
        """
        The core method to draw the plot on a matplotlib Axes object.
        """
        raise NotImplementedError(
            "The render method must be implemented by subclasses."
        )
