from typing import Optional

import matplotlib.pyplot as plt


def get_axes_from_grid(
    axes: plt.Axes, row: Optional[int] = None, col: Optional[int] = None
) -> plt.Axes:
    if not hasattr(axes, "__len__"):
        return axes

    # Convert Python list to numpy array structure if needed
    if not hasattr(axes, "ndim") and len(axes) > 0:
        # Get grid dimensions from first axis's gridspec
        first_ax = axes[0]
        assert (
            hasattr(first_ax, "get_gridspec") and first_ax.get_gridspec() is not None
        ), "Cannot determine grid dimensions: first axis has no gridspec"

        gs = first_ax.get_gridspec()
        nrows, ncols = gs.nrows, gs.ncols

        # Convert list to array using linear indexing: list[row * ncols + col] -> array[row, col]
        assert row is not None and col is not None, (
            "Must specify both row and col for list-based axes"
        )
        linear_index = row * ncols + col
        assert linear_index < len(axes), (
            f"Index {linear_index} (row={row}, col={col}) out of bounds for {len(axes)} axes"
        )
        return axes[linear_index]

    # Handle numpy array case (FigureManager's self.axes)
    if hasattr(axes, "ndim") and axes.ndim == 1:
        idx = col if col is not None else row
        assert idx is not None, "Must specify either row or col for 1D axes array"
        return axes[idx]

    if row is not None and col is not None:
        return axes[row, col]
    elif row is not None:
        return axes[row, :]
    elif col is not None:
        return axes[:, col]

    return axes
