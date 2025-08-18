"""
Base class for all plotter objects.
"""

from ..style import DrPlotterStyle


class BasePlotter:
    """
    A base class for all atomic plotters.

    Defines the interface that all plotters must follow.
    """

    def __init__(self, data, **kwargs):
        """
        Initialize the plotter with a pandas DataFrame.

        Args:
            data: A pandas DataFrame.
            **kwargs: Styling options to be passed to matplotlib.
        """
        self.data = data
        self.style = DrPlotterStyle()
        self.kwargs = kwargs

    def render(self, ax):
        """
        The core method to draw the plot on a matplotlib Axes object.

        This method should be implemented by all subclasses.
        """
        raise NotImplementedError("The render method must be implemented by subclasses.")