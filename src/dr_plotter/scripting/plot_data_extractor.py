from typing import Any, Dict, List, Tuple
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.image import AxesImage
from matplotlib.container import BarContainer
import matplotlib.legend


type RGBA = Tuple[float, float, float, float]
type Position = Tuple[float, float]
type CollectionProperties = Dict[str, Any]


def extract_colors(obj: Any) -> List[RGBA]:
    if isinstance(obj, PathCollection):
        return [mcolors.to_rgba(color) for color in obj.get_facecolors()]
    elif isinstance(obj, PolyCollection):
        facecolors = obj.get_facecolors()
        if len(facecolors) == 0:
            return [(0.0, 0.0, 0.0, 1.0)]
        return [mcolors.to_rgba(color) for color in facecolors]
    elif isinstance(obj, BarContainer):
        return [mcolors.to_rgba(patch.get_facecolor()) for patch in obj.patches]
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_color"):
        colors = []
        for line in obj:
            color = line.get_color()
            alpha = line.get_alpha() if line.get_alpha() is not None else 1.0
            rgba = mcolors.to_rgba(color)
            if len(rgba) == 3:
                rgba = (*rgba, alpha)
            elif len(rgba) == 4:
                rgba = (*rgba[:3], alpha)
            colors.append(rgba)
        return colors
    elif hasattr(obj, "get_markerfacecolor"):
        face_color = obj.get_markerfacecolor()
        if (isinstance(face_color, str) and face_color == "none") or face_color is None:
            face_color = obj.get_color()
        return [mcolors.to_rgba(face_color)]
    elif hasattr(obj, "get_facecolor"):
        return [mcolors.to_rgba(obj.get_facecolor())]
    elif hasattr(obj, "get_color"):
        return [mcolors.to_rgba(obj.get_color())]
    else:
        return [(0.0, 0.0, 0.0, 1.0)]


def extract_markers(obj: Any) -> List[str]:
    if isinstance(obj, PathCollection):
        paths = obj.get_paths()
        markers = []
        for path in paths:
            marker_type = _identify_marker_from_path(path)
            markers.append(marker_type)
        return markers
    elif isinstance(obj, PolyCollection):
        return ["violin"]
    elif isinstance(obj, BarContainer):
        return ["bar"] * len(obj.patches)
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_marker"):
        markers = []
        for line in obj:
            marker = line.get_marker()
            if marker is None or marker == "None":
                marker = ""
            markers.append(str(marker))
        return markers
    elif hasattr(obj, "get_marker"):
        marker = obj.get_marker()
        return [str(marker) if marker and marker != "None" else "None"]
    else:
        return ["unknown"]


def extract_sizes(obj: Any) -> List[float]:
    if isinstance(obj, PathCollection):
        sizes = obj.get_sizes()
        return [float(size) for size in sizes]
    elif isinstance(obj, PolyCollection):
        return [1.0]
    elif isinstance(obj, BarContainer):
        return [1.0] * len(obj.patches)
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_markersize"):
        return [float(line.get_markersize()) for line in obj]
    elif hasattr(obj, "get_markersize"):
        return [float(obj.get_markersize())]
    else:
        return [1.0]


def extract_positions(obj: Any) -> List[Position]:
    if isinstance(obj, PathCollection):
        offsets = obj.get_offsets()
        return [(float(x), float(y)) for x, y in offsets]
    else:
        return []


def extract_alphas(obj: Any) -> List[float]:
    if isinstance(obj, PathCollection):
        facecolors = obj.get_facecolors()
        return [float(color[3]) if len(color) >= 4 else 1.0 for color in facecolors]
    elif isinstance(obj, PolyCollection):
        alpha = obj.get_alpha()
        if alpha is None:
            facecolors = obj.get_facecolors()
            if len(facecolors) > 0 and len(facecolors[0]) >= 4:
                return [float(facecolors[0][3])]
            return [1.0]
        return [float(alpha)]
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_alpha"):
        alphas = []
        for line in obj:
            alpha = line.get_alpha()
            if alpha is None:
                alpha = 1.0
            alphas.append(float(alpha))
        return alphas
    else:
        colors = extract_colors(obj)
        return [float(color[3]) if len(color) >= 4 else 1.0 for color in colors]


def extract_styles(obj: Any) -> List[str]:
    if isinstance(obj, PolyCollection):
        edgecolors = obj.get_edgecolors()
        linewidths = obj.get_linewidths()
        if len(edgecolors) > 0 and len(linewidths) > 0:
            edge_rgba = mcolors.to_rgba(edgecolors[0])
            if edge_rgba[3] > 0 and linewidths[0] > 0:
                return ["-"]
        return [""]
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_linestyle"):
        return [line.get_linestyle() for line in obj]
    elif hasattr(obj, "get_linestyle"):
        style = obj.get_linestyle()
        return [str(style) if style is not None else "-"]
    else:
        return ["-"]


def extract_legend_properties(ax: Any) -> Dict[str, Any]:
    legend = ax.get_legend()
    if legend is None:
        return {
            "handles": [],
            "markers": [],
            "colors": [],
            "sizes": [],
            "labels": [],
            "styles": [],
            "visible": False,
        }

    handles = []
    if hasattr(legend, "legend_handles"):
        handles = legend.legend_handles
    elif hasattr(legend, "legendHandles"):
        handles = legend.legendHandles
    elif hasattr(legend, "get_lines") and hasattr(legend, "get_patches"):
        handles.extend(legend.get_lines())
        handles.extend(legend.get_patches())
    elif hasattr(legend, "_legend_handles"):
        handles = legend._legend_handles

    return {
        "handles": handles,
        "markers": [_extract_marker_from_handle(h) for h in handles],
        "colors": [_extract_color_from_handle(h) for h in handles],
        "sizes": [_extract_size_from_handle(h) for h in handles],
        "labels": [text.get_text() for text in legend.get_texts()],
        "styles": [_extract_style_from_handle(h) for h in handles],
        "visible": legend.get_visible(),
    }


def extract_collection_properties(
    obj: Any, collection_type: str = "auto"
) -> CollectionProperties:
    if collection_type == "auto":
        collection_type = _detect_collection_type(obj)

    base_props = {
        "type": collection_type,
        "positions": extract_positions(obj),
        "colors": extract_colors(obj),
        "markers": extract_markers(obj),
        "sizes": extract_sizes(obj),
        "alphas": extract_alphas(obj),
        "styles": extract_styles(obj),
    }

    if isinstance(obj, AxesImage):
        base_props.update(_extract_image_properties(obj))

    return base_props


def extract_figure_legend_properties(fig: Any) -> Dict[str, Any]:
    legends = []
    for child in fig.get_children():
        if isinstance(child, matplotlib.legend.Legend):
            legends.append(child)

    result = {
        "legend_count": len(legends),
        "legends": [],
        "total_entries": 0,
    }

    for i, legend in enumerate(legends):
        handles = []
        if hasattr(legend, "legend_handles"):
            handles.extend(legend.legend_handles)
        elif hasattr(legend, "legendHandles"):
            handles.extend(legend.legendHandles)
        elif hasattr(legend, "get_lines") and hasattr(legend, "get_patches"):
            handles.extend(legend.get_lines())
            handles.extend(legend.get_patches())
        else:
            if hasattr(legend, "_legend_handles"):
                handles.extend(legend._legend_handles)

        legend_props = {
            "index": i,
            "title": legend.get_title().get_text() if legend.get_title() else None,
            "handles": handles,
            "labels": [text.get_text() for text in legend.get_texts()],
            "entry_count": len(legend.get_texts()),
            "ncol": getattr(legend, "_ncols", getattr(legend, "_ncol", 1)),
            "position": getattr(legend, "_loc", None),
            "colors": [_extract_color_from_handle(h) for h in handles],
            "markers": [_extract_marker_from_handle(h) for h in handles],
            "sizes": [_extract_size_from_handle(h) for h in handles],
        }

        result["legends"].append(legend_props)
        result["total_entries"] += legend_props["entry_count"]

    return result


def convert_scatter_size_to_legend_size(scatter_size: float) -> float:
    return np.sqrt(scatter_size / np.pi) * 2


def convert_legend_size_to_scatter_size(legend_size: float) -> float:
    return np.pi * (legend_size / 2) ** 2


def _identify_marker_from_path(path: Any) -> str:
    if not hasattr(path, "vertices"):
        return "unknown"

    vertices = path.vertices
    num_vertices = len(vertices)

    if num_vertices == 1:
        return "."
    elif num_vertices == 2:
        return "|"
    elif num_vertices == 3:
        return "^"
    elif num_vertices == 4:
        return "D"
    elif num_vertices == 5:
        return "s"
    elif num_vertices == 6:
        return "p"
    elif num_vertices > 10 and _is_circle_approximation(vertices):
        return "o"
    else:
        return f"custom_{num_vertices}"


def _is_circle_approximation(vertices: np.ndarray) -> bool:
    if len(vertices) < 8:
        return False

    center = np.mean(vertices, axis=0)
    distances = np.linalg.norm(vertices - center, axis=1)
    distance_variation = np.std(distances) / np.mean(distances)

    return distance_variation < 0.1


def _detect_collection_type(obj: Any) -> str:
    if isinstance(obj, PathCollection):
        return "scatter"
    elif isinstance(obj, PolyCollection):
        return "violin"
    elif isinstance(obj, BarContainer):
        return "bar"
    elif isinstance(obj, list) and obj and hasattr(obj[0], "get_marker"):
        return "line"
    elif isinstance(obj, AxesImage):
        return "image"
    else:
        return "unknown"


def _extract_color_from_handle(handle: Any) -> RGBA:
    try:
        if hasattr(handle, "get_markerfacecolor"):
            color = handle.get_markerfacecolor()
            if (isinstance(color, str) and color == "none") or color is None:
                color = handle.get_color()
        elif hasattr(handle, "get_facecolor"):
            color = handle.get_facecolor()
        elif hasattr(handle, "get_color"):
            color = handle.get_color()
        else:
            color = "black"
        return mcolors.to_rgba(color)
    except (ValueError, TypeError):
        return (0.0, 0.0, 0.0, 1.0)


def _extract_marker_from_handle(handle: Any) -> str:
    try:
        if hasattr(handle, "get_marker"):
            marker = handle.get_marker()
            return str(marker) if marker and marker != "None" else "None"
        else:
            return "patch"
    except (ValueError, TypeError):
        return "unknown"


def _extract_size_from_handle(handle: Any) -> float:
    try:
        if hasattr(handle, "get_markersize"):
            return float(handle.get_markersize())
        else:
            return 1.0
    except (ValueError, TypeError):
        return 1.0


def _extract_style_from_handle(handle: Any) -> str:
    try:
        if hasattr(handle, "get_linestyle"):
            style = handle.get_linestyle()
            return str(style) if style is not None else "-"
        else:
            return "-"
    except (ValueError, TypeError):
        return "-"


def _extract_image_properties(image: AxesImage) -> Dict[str, Any]:
    array = image.get_array()
    extent = image.get_extent()
    return {
        "image_data": {
            "shape": array.shape if hasattr(array, "shape") else None,
            "extent": extent,
            "colormap": str(image.get_cmap()),
            "vmin": image.get_clim()[0] if image.get_clim() else None,
            "vmax": image.get_clim()[1] if image.get_clim() else None,
        }
    }
