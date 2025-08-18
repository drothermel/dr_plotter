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
        # If axes is a single object, return it
        if not hasattr(self.axes, "__len__"):
            return self.axes

        # If axes is 1D array
        if self.axes.ndim == 1:
            if row is not None and col is not None:
                # This case is ambiguous, but we'll assume the user wants the col index
                # if rows==1, or the row index if cols==1.
                idx = col if self.axes.shape[0] > 1 else row
                return self.axes[idx]
            elif row is not None:
                return self.axes[row]
            elif col is not None:
                return self.axes[col]
            else:
                return self.axes

        # If axes is 2D array
        if row is not None and col is not None:
            return self.axes[row, col]
        elif row is not None:
            return self.axes[row, :]
        elif col is not None:
            return self.axes[:, col]
        return self.axes

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
