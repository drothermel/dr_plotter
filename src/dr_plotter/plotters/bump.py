"""
Compound plotter for bump plots.
"""

import matplotlib.patheffects as path_effects
from .base import BasePlotter
from dr_plotter.theme import BUMP_PLOT_THEME


class BumpPlotter(BasePlotter):
    """
    A compound plotter for creating bump plots to visualize rankings over time.
    """

    def __init__(self, data, time_col, category_col, value_col, **kwargs):
        """
        Initialize the BumpPlotter.
        """
        super().__init__(data, **kwargs)
        self.time_col = time_col
        self.category_col = category_col
        self.value_col = value_col
        self.theme = BUMP_PLOT_THEME
        self.x = time_col
        self.y = "Rank"

    def _prepare_data(self):
        """Calculate ranks for each category at each time point."""
        self.data["rank"] = self.data.groupby(self.time_col)[self.value_col].rank(
            method="first", ascending=False
        )
        return self.data

    def render(self, ax):
        """
        Render the bump plot on the given axes.
        """
        plot_data = self._prepare_data()
        categories = plot_data[self.category_col].unique()

        for category in categories:
            category_data = plot_data[
                plot_data[self.category_col] == category
            ].sort_values(by=self.time_col)

            plot_kwargs = {
                "marker": self.theme.get("marker"),
                "linewidth": self.theme.get("line_width"),
                "color": next(self.theme.get("color_cycle")),
            }
            plot_kwargs.update(self._filter_plot_kwargs())

            ax.plot(category_data[self.time_col], category_data["rank"], **plot_kwargs)

            last_point = category_data.iloc[-1]
            text = ax.text(
                last_point[self.time_col],
                last_point["rank"],
                f" {category}",
                va="center",
                color=plot_kwargs["color"],
                fontweight="bold",
            )
            text.set_path_effects(
                [
                    path_effects.Stroke(linewidth=2, foreground="white"),
                    path_effects.Normal(),
                ]
            )

        ax.invert_yaxis()
        max_rank = int(plot_data["rank"].max())
        ax.set_yticks(range(1, max_rank + 1))
        ax.margins(x=0.15)

        self._apply_styling(ax)
