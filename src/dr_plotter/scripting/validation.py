from typing import Any
import matplotlib.pyplot as plt


def validate_figure_result(result: Any) -> plt.Figure:
    assert isinstance(result, (plt.Figure, list, tuple)), (
        f"Function must return Figure or list/tuple, got {type(result).__name__}"
    )

    if isinstance(result, plt.Figure):
        return result
    elif isinstance(result, (list, tuple)) and len(result) >= 1:
        assert isinstance(result[0], plt.Figure), (
            f"Function must return Figure(s), got {type(result[0]).__name__}"
        )
        return result[0]
    else:
        assert False, f"Invalid return type: {type(result).__name__}"


def validate_figure_list_result(result: Any) -> list[plt.Figure]:
    assert isinstance(result, (plt.Figure, list, tuple)), (
        f"Function must return Figure or list/tuple, got {type(result).__name__}"
    )

    if isinstance(result, plt.Figure):
        return [result]
    elif isinstance(result, (list, tuple)) and len(result) >= 1:
        if all(isinstance(f, plt.Figure) for f in result):
            return list(result)
        elif isinstance(result[0], plt.Figure):
            return [result[0]]
        else:
            assert False, (
                f"Function must return Figure(s), got {type(result[0]).__name__} in {type(result).__name__}"
            )
    else:
        assert False, (
            f"Function must return Figure or list of Figures, got {type(result).__name__}"
        )


def validate_axes_access(fig_axes: list, row: int, col: int) -> plt.Axes:
    assert len(fig_axes) > 0, "No axes found in figure"

    from dr_plotter.utils import get_axes_from_grid

    ax = get_axes_from_grid(fig_axes, row, col)
    assert ax is not None, f"No axis found at position ({row}, {col})"
    return ax


def validate_legend_properties(ax: plt.Axes) -> dict:
    from .plot_data_extractor import extract_legend_properties, extract_colors
    import matplotlib.colors as mcolors

    legend_props = extract_legend_properties(ax)

    if not legend_props["visible"]:
        return {"visible": False, "entries": [], "entry_count": 0}

    legend_colors = extract_colors(legend_props["handles"])
    legend_labels = legend_props["labels"]

    color_label_pairs = []
    for i, (rgba_color, label) in enumerate(zip(legend_colors, legend_labels)):
        hex_color = mcolors.to_hex(rgba_color)
        color_label_pairs.append(
            {
                "index": i,
                "color": hex_color,
                "label": label.strip() if label else "(empty)",
            }
        )

    return {
        "visible": True,
        "entries": color_label_pairs,
        "entry_count": len(legend_labels),
    }


def validate_subplot_coord_access(
    fig: plt.Figure, subplot_coord: tuple[int, int]
) -> plt.Axes:
    row, col = subplot_coord
    from dr_plotter.utils import get_axes_from_grid

    main_grid_axes = []
    for ax in fig.axes:
        if hasattr(ax, "get_gridspec") and ax.get_gridspec() is not None:
            main_grid_axes.append(ax)

    assert len(main_grid_axes) > 0, "No main grid axes found in figure"

    ax = get_axes_from_grid(main_grid_axes, row, col)
    assert ax is not None, f"No axis found at position ({row}, {col})"
    return ax
