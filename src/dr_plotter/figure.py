"""
Context manager for creating complex figures.
"""

import matplotlib.pyplot as plt


class FigureManager:
    """
    A context manager for creating complex figures with multiple subplots.
    """

    def __init__(self, rows=1, cols=1, **fig_kwargs):
        """
        Initialize the FigureManager.

        Args:
            rows: The number of rows of subplots.
            cols: The number of columns of subplots.
            **fig_kwargs: Keyword arguments to be passed to plt.subplots().
        """
        self.fig, self.axes = plt.subplots(rows, cols, **fig_kwargs)

    def get_axes(self, row=None, col=None):
        """
        Get the axes object for a specific subplot.

        Args:
            row: The row of the subplot.
            col: The column of the subplot.

        Returns:
            A matplotlib Axes object.
        """
        if row is None and col is None:
            return self.axes
        if row is not None and col is not None:
            return self.axes[row, col]
        if row is not None:
            return self.axes[row]
        return self.axes[col]

    def add_plotter(self, plotter, row=None, col=None):
        """
        Add a plotter to a specific subplot.

        Args:
            plotter: An atomic plotter object.
            row: The row of the subplot.
            col: The column of the subplot.
        """
        ax = self.get_axes(row, col)
        plotter.render(ax)

    def __enter__(self):
        """
        Enter the context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and show the plot.
        """
        plt.show()
