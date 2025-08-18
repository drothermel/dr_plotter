"""
Atomic plotter for violin plots.
"""

from .base import BasePlotter


class ViolinPlotter(BasePlotter):
    """
    An atomic plotter for creating violin plots.
    """

    def __init__(self, data, x, y, dr_plotter_kwargs, matplotlib_kwargs):
        """
        Initialize the ViolinPlotter.

        Args:
            data: A pandas DataFrame.
            x: The column for the x-axis (categories).
            y: The column for the y-axis (values).
            dr_plotter_kwargs: High-level styling options for dr_plotter.
            matplotlib_kwargs: Low-level kwargs to pass to matplotlib.
        """
        super().__init__(data, dr_plotter_kwargs, matplotlib_kwargs)
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
            ax.violinplot(dataset, **self.matplotlib_kwargs)
            ax.set_xticks(list(range(1, len(groups) + 1)))
            ax.set_xticklabels(groups)
        elif self.y:
            # Single violin plot
            ax.violinplot(self.data[self.y].dropna(), **self.matplotlib_kwargs)
        else:
            # Plot all numeric columns if no y is specified
            numeric_cols = self.data.select_dtypes(include='number').columns
            dataset = [self.data[col].dropna() for col in numeric_cols]
            ax.violinplot(dataset, **self.matplotlib_kwargs)
            ax.set_xticks(list(range(1, len(numeric_cols) + 1)))
            ax.set_xticklabels(numeric_cols)

        self.style.apply_grid(ax)
        self._apply_styling(ax)