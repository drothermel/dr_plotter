from typing import Any, Dict, List, Tuple
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D


def extract_scatter_positions(collection: PathCollection) -> List[Tuple[float, float]]:
    offsets = collection.get_offsets()
    return [(float(x), float(y)) for x, y in offsets]


def extract_scatter_colors(
    collection: PathCollection,
) -> List[Tuple[float, float, float, float]]:
    facecolors = collection.get_facecolors()
    return [mcolors.to_rgba(color) for color in facecolors]


def extract_scatter_sizes(collection: PathCollection) -> List[float]:
    sizes = collection.get_sizes()
    return [float(size) for size in sizes]


def extract_scatter_markers(collection: PathCollection) -> List[str]:
    paths = collection.get_paths()
    markers = []
    for path in paths:
        marker_type = identify_marker_from_path(path)
        markers.append(marker_type)
    return markers


def identify_marker_from_path(path: Any) -> str:
    if not hasattr(path, "vertices"):
        return "unknown"

    vertices = path.vertices
    num_vertices = len(vertices)

    # Handle common matplotlib marker patterns
    if num_vertices == 1:
        return "."
    elif num_vertices == 2:
        return "|"
    elif num_vertices == 3:
        return "^"
    elif num_vertices == 4:
        return "D"  # diamond
    elif num_vertices == 5:
        return "s"  # square (4 corners + closing point)
    elif num_vertices == 6:
        return "p"  # pentagon (5 corners + closing point)
    elif num_vertices > 10 and _is_circle_approximation(vertices):
        return "o"
    else:
        # For debugging purposes, show actual number
        return f"custom_{num_vertices}"


def _is_circle_approximation(vertices: np.ndarray) -> bool:
    if len(vertices) < 8:
        return False

    center = np.mean(vertices, axis=0)
    distances = np.linalg.norm(vertices - center, axis=1)
    distance_variation = np.std(distances) / np.mean(distances)

    return distance_variation < 0.1


def _is_triangle_like(vertices: np.ndarray) -> bool:
    if len(vertices) != 5:
        return False

    # For matplotlib triangles, often the first and last vertices are the same
    # Check if we have 3 distinct points (ignoring duplicates)
    unique_vertices = []
    for vertex in vertices:
        is_duplicate = False
        for unique_vertex in unique_vertices:
            if np.allclose(vertex, unique_vertex, atol=1e-10):
                is_duplicate = True
                break
        if not is_duplicate:
            unique_vertices.append(vertex)

    return len(unique_vertices) == 3


def extract_legend_handles(ax: Any) -> List[Line2D]:
    legend = ax.get_legend()
    if legend is None:
        return []

    handles = legend.get_lines()
    return [handle for handle in handles if isinstance(handle, Line2D)]


def extract_legend_markers(handles: List[Line2D]) -> List[str]:
    markers = []
    for handle in handles:
        try:
            marker = handle.get_marker()
            if marker is None:
                marker = "None"
            markers.append(str(marker))
        except (ValueError, TypeError):
            markers.append("None")
    return markers


def extract_legend_colors(
    handles: List[Line2D],
) -> List[Tuple[float, float, float, float]]:
    colors = []
    for handle in handles:
        try:
            face_color = handle.get_markerfacecolor()
            # Handle numpy arrays and string comparisons
            if (
                isinstance(face_color, str) and face_color == "none"
            ) or face_color is None:
                face_color = handle.get_color()
            elif hasattr(face_color, "__len__") and len(face_color) > 1:
                # It's already a color array, use it directly
                pass
            colors.append(mcolors.to_rgba(face_color))
        except (ValueError, TypeError):
            # Fallback to a default color if extraction fails
            colors.append((0.0, 0.0, 0.0, 1.0))  # Black
    return colors


def extract_legend_sizes(handles: List[Line2D]) -> List[float]:
    return [float(handle.get_markersize()) for handle in handles]


def extract_legend_labels(handles: List[Line2D]) -> List[str]:
    return [handle.get_label() for handle in handles]


def extract_pathcollections_from_axis(ax: Any) -> List[PathCollection]:
    collections = []
    for collection in ax.collections:
        if isinstance(collection, PathCollection):
            collections.append(collection)
    return collections


def convert_scatter_size_to_legend_size(scatter_size: float) -> float:
    return np.sqrt(scatter_size / np.pi) * 2


def convert_legend_size_to_scatter_size(legend_size: float) -> float:
    return np.pi * (legend_size / 2) ** 2


def debug_legend_detection(ax: Any) -> Dict[str, Any]:
    legend = ax.get_legend()

    debug_info = {
        "legend_exists": legend is not None,
        "legend_object": legend,
        "legend_visible": legend.get_visible() if legend else False,
        "legend_texts": [],
        "legend_handles": [],
        "all_legend_children": [],
    }

    if legend:
        debug_info["legend_texts"] = [text.get_text() for text in legend.get_texts()]
        debug_info["legend_handles"] = legend.get_lines()
        debug_info["all_legend_children"] = legend.get_children()
        debug_info["legend_numpoints"] = (
            legend.numpoints if hasattr(legend, "numpoints") else None
        )

    return debug_info


def extract_subplot_properties(ax: Any) -> Dict[str, Any]:
    collections = extract_pathcollections_from_axis(ax)
    legend_handles = extract_legend_handles(ax)
    legend_debug = debug_legend_detection(ax)

    result = {
        "collections": [],
        "legend": {
            "handles": legend_handles,
            "markers": extract_legend_markers(legend_handles),
            "colors": extract_legend_colors(legend_handles),
            "sizes": extract_legend_sizes(legend_handles),
            "labels": extract_legend_labels(legend_handles),
            "debug": legend_debug,
        },
    }

    for i, collection in enumerate(collections):
        collection_props = {
            "index": i,
            "positions": extract_scatter_positions(collection),
            "colors": extract_scatter_colors(collection),
            "sizes": extract_scatter_sizes(collection),
            "markers": extract_scatter_markers(collection),
        }
        result["collections"].append(collection_props)

    return result
