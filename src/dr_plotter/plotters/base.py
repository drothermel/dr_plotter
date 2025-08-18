"""
Base class for all plotter objects.
"""

from ..style import DrPlotterStyle


class BasePlotter:
    """
    A base class for all atomic plotters.

    Defines the interface that all plotters must follow and provides
    centralized styling logic.
    """

    def __init__(self, data, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the plotter.

        Args:
            data: A pandas DataFrame.
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        self.data = data
        self.dr_plotter_kwargs = dr_plotter_kwargs
        self.matplotlib_kwargs = matplotlib_kwargs
        self.style = DrPlotterStyle()

    def _apply_styling(self, ax):
        """Apply high-level styling options to the axes object."""
        # Set title
        if 'title' in self.dr_plotter_kwargs:
            ax.set_title(self.dr_plotter_kwargs['title'])

        # Set xlabel
        if 'xlabel' in self.dr_plotter_kwargs:
            ax.set_xlabel(self.dr_plotter_kwargs['xlabel'])
        elif hasattr(self, 'x') and self.x:
            ax.set_xlabel(self.x.replace('_', ' ').title())

        # Set ylabel
        if 'ylabel' in self.dr_plotter_kwargs:
            ax.set_ylabel(self.dr_plotter_kwargs['ylabel'])
        elif hasattr(self, 'y') and self.y:
            ax.set_ylabel(self.y.replace('_', ' ').title())

        # Set legend
        if self.dr_plotter_kwargs.get('legend') is True:
            # Avoid duplicate legends
            if not ax.get_legend():
                ax.legend()

    def render(self, ax):
        """
        The core method to draw the plot on a matplotlib Axes object.

        This method should be implemented by all subclasses.
        """
        raise NotImplementedError("The render method must be implemented by subclasses.")