import matplotlib.pyplot as plt
from ..style import ProPlotterStyle


class BasePlotter:
    """
    A base class for plotters.

    Handles common plotting setup, such as creating a figure and axes,
    and applying a consistent style.
    """

    def __init__(self, data):
        """
        Initialize the plotter with a pandas DataFrame.

        Args:
            data: A pandas DataFrame.
        """
        self.data = data
        self.style = ProPlotterStyle()

    def _setup_figure(self, figsize=(10, 6)):
        """
        Set up the figure and axes for the plot.

        Args:
            figsize: The size of the figure.

        Returns:
            A tuple of (figure, axes).
        """
        fig, ax = plt.subplots(figsize=figsize)
        self.style.apply_grid(ax)
        return fig, ax
