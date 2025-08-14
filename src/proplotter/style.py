import numpy as np
import matplotlib.pyplot as plt
from typing import List


class ProPlotterStyle:
    """Unified visual styling for all plots."""

    # Color palette
    COLORS = {
        "primary_1": "skyblue",
        "primary_2": "lightcoral",
        "primary_3": "lightgreen",
        "primary_4": "gold",
        "accent_1": "steelblue",
        "accent_2": "green",
        "accent_3": "red",
        "accent_4": "orange",
    }

    # Transparency settings
    ALPHA = {
        "bars": 0.7,
        "scatter": 0.6,
        "regions": 0.1,
        "lines": 0.8,
        "reference": 0.7,
    }

    # Grid and layout
    GRID = {"alpha": 0.3}
    LINE_WEIGHTS = {"main": 2, "reference": 2, "thin": 1}
    FONT_SIZES = {"labels": 10, "annotations": 9, "legend": 8}

    # Marker settings
    SCATTER_SIZE = {"default": 30, "large": 100}

    # Colormap for multi-category data
    COLORMAP = "viridis"

    @classmethod
    def get_category_colors(cls, n_categories: int, colormap: str = None) -> List[str]:
        """Get evenly spaced colors for multiple categories."""
        cmap = colormap or cls.COLORMAP
        return plt.cm.get_cmap(cmap)(np.linspace(0, 1, n_categories))

    @classmethod
    def apply_grid(cls, ax):
        """Apply consistent grid styling."""
        ax.grid(True, **cls.GRID)
