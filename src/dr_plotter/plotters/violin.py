"""
Atomic plotter for violin plots.
"""

from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots.
    """

    def __init__(self, data, x=None, y=None, **kwargs):
        """
        Initialize the ViolinPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis (categories).
            y: The column for the y-axis (values).
            **kwargs: Styling options for the violin plot.
        """
        super().__init__(data, **kwargs)
        self.x = x
        self.y = y

    def render(self, ax):
        """
        Render the violin plot on the given axes.

        Args:
            ax: A matplotlib Axes object.
        """
        if self.x and self.y:
            # Grouped violin plot
            groups = self.data[self.x].unique()
            dataset = [self.data[self.data[self.x] == group][self.y].dropna() for group in groups]
            ax.violinplot(dataset, **self.kwargs)
            ax.set_xticks(list(range(1, len(groups) + 1)))
            ax.set_xticklabels(groups)
        elif self.y:
            # Single violin plot
            ax.violinplot(self.data[self.y].dropna(), **self.kwargs)
        else:
            # Plot all numeric columns if no y is specified
            numeric_cols = self.data.select_dtypes(include='number').columns
            dataset = [self.data[col].dropna() for col in numeric_cols]
            ax.violinplot(dataset, **self.kwargs)
            ax.set_xticks(list(range(1, len(numeric_cols) + 1)))
            ax.set_xticklabels(numeric_cols)

        self.style.apply_grid(ax)
