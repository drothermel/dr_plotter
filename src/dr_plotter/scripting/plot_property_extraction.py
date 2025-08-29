from typing import Any, Dict, List, Tuple
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.lines import Line2D
from matplotlib.image import AxesImage
from .plot_data_extractor import (
    extract_colors,
    extract_markers,
    extract_sizes,
    extract_positions,
    extract_alphas,
    extract_styles,
    extract_legend_properties,
    extract_collection_properties,
)


def extract_scatter_positions(collection: PathCollection) -> List[Tuple[float, float]]:
    return extract_positions(collection)


def extract_scatter_colors(
    collection: PathCollection,
) -> List[Tuple[float, float, float, float]]:
    return extract_colors(collection)


def extract_scatter_sizes(collection: PathCollection) -> List[float]:
    return extract_sizes(collection)


def extract_scatter_markers(collection: PathCollection) -> List[str]:
    return extract_markers(collection)


def identify_marker_from_path(path: Any) -> str:
    from .plot_data_extractor import _identify_marker_from_path

    return _identify_marker_from_path(path)


def extract_legend_handles(ax: Any) -> List[Line2D]:
    legend_props = extract_legend_properties(ax)
    return [h for h in legend_props["handles"] if isinstance(h, Line2D)]


def extract_legend_markers(handles: List[Line2D]) -> List[str]:
    return extract_markers(handles)


def extract_legend_colors(
    handles: List[Line2D],
) -> List[Tuple[float, float, float, float]]:
    return extract_colors(handles)


def extract_legend_sizes(handles: List[Line2D]) -> List[float]:
    return extract_sizes(handles)


def extract_legend_labels(handles: List[Line2D]) -> List[str]:
    return [handle.get_label() for handle in handles]


def extract_legend_styles(handles: List[Line2D]) -> List[str]:
    return extract_styles(handles)


def extract_pathcollections_from_axis(ax: Any) -> List[PathCollection]:
    collections = []
    for collection in ax.collections:
        if isinstance(collection, PathCollection):
            collections.append(collection)
    return collections


def extract_polycollections_from_axis(ax: Any) -> List[PolyCollection]:
    collections = []
    for collection in ax.collections:
        if isinstance(collection, PolyCollection):
            collections.append(collection)
    return collections


def extract_violin_colors(
    collection: PolyCollection,
) -> List[Tuple[float, float, float, float]]:
    return extract_colors(collection)


def extract_violin_markers(collection: PolyCollection) -> List[str]:
    return extract_markers(collection)


def extract_violin_sizes(collection: PolyCollection) -> List[float]:
    return extract_sizes(collection)


def extract_violin_alphas(collection: PolyCollection) -> List[float]:
    return extract_alphas(collection)


def extract_violin_styles(collection: PolyCollection) -> List[str]:
    return extract_styles(collection)


def extract_barcontainers_from_axis(ax: Any) -> List[Any]:
    from matplotlib.container import BarContainer

    return [c for c in getattr(ax, "containers", []) if isinstance(c, BarContainer)]


def extract_bar_colors(container: Any) -> List[Tuple[float, float, float, float]]:
    return extract_colors(container)


def extract_lines_from_axis(ax: Any) -> List[Any]:
    return [line for line in getattr(ax, "lines", []) if hasattr(line, "get_color")]


def extract_line_colors(lines: List[Any]) -> List[Tuple[float, float, float, float]]:
    return extract_colors(lines)


def extract_line_styles(lines: List[Any]) -> List[str]:
    return extract_styles(lines)


def extract_line_markers(lines: List[Any]) -> List[str]:
    return extract_markers(lines)


def extract_line_alphas(lines: List[Any]) -> List[float]:
    return extract_alphas(lines)


def extract_images_from_axis(ax: Any) -> List[AxesImage]:
    return [img for img in getattr(ax, "images", []) if isinstance(img, AxesImage)]


def extract_image_data(image: AxesImage) -> Dict[str, Any]:
    props = extract_collection_properties(image)
    return props.get("image_data", {})


def debug_legend_detection(ax: Any) -> Dict[str, Any]:
    legend = ax.get_legend()
    legend_props = extract_legend_properties(ax)

    debug_info = {
        "legend_exists": legend is not None,
        "legend_object": legend,
        "legend_visible": legend_props["visible"],
        "legend_texts": legend_props["labels"],
        "legend_handles": legend_props["handles"],
        "all_legend_children": legend.get_children() if legend else [],
    }

    if legend:
        debug_info["legend_numpoints"] = (
            legend.numpoints if hasattr(legend, "numpoints") else None
        )

    return debug_info


def extract_legend_colors_from_handles(handles: List[Any]) -> List[Tuple[float, ...]]:
    return extract_colors(handles)


def extract_legend_markers_from_handles(handles: List[Any]) -> List[str]:
    return extract_markers(handles)


def extract_legend_sizes_from_handles(handles: List[Any]) -> List[float]:
    return extract_sizes(handles)


def extract_subplot_properties(ax: Any) -> Dict[str, Any]:
    path_collections = extract_pathcollections_from_axis(ax)
    poly_collections = extract_polycollections_from_axis(ax)
    bar_containers = extract_barcontainers_from_axis(ax)
    lines = extract_lines_from_axis(ax)
    images = extract_images_from_axis(ax)
    legend_props = extract_legend_properties(ax)
    legend_debug = debug_legend_detection(ax)

    result = {
        "collections": [],
        "legend": {
            "handles": legend_props["handles"],
            "markers": legend_props["markers"],
            "colors": legend_props["colors"],
            "sizes": legend_props["sizes"],
            "labels": legend_props["labels"],
            "styles": legend_props["styles"],
            "debug": legend_debug,
        },
    }

    for i, collection in enumerate(path_collections):
        collection_props = extract_collection_properties(collection, "scatter")
        collection_props["index"] = i
        result["collections"].append(collection_props)

    for i, collection in enumerate(poly_collections):
        collection_props = extract_collection_properties(collection, "violin")
        collection_props["index"] = len(path_collections) + i
        result["collections"].append(collection_props)

    for i, container in enumerate(bar_containers):
        collection_props = extract_collection_properties(container, "bar")
        collection_props["index"] = len(path_collections) + len(poly_collections) + i
        result["collections"].append(collection_props)

    if lines:
        collection_props = extract_collection_properties(lines, "line")
        collection_props["index"] = (
            len(path_collections) + len(poly_collections) + len(bar_containers)
        )
        result["collections"].append(collection_props)

    for i, image in enumerate(images):
        collection_props = extract_collection_properties(image, "image")
        collection_props["index"] = (
            len(path_collections)
            + len(poly_collections)
            + len(bar_containers)
            + len(lines)
            + i
        )
        result["collections"].append(collection_props)

    return result
