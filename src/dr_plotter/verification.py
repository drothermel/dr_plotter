from typing import Optional, Dict, Any
import matplotlib.pyplot as plt


def is_legend_actually_visible(
    ax: plt.Axes, figure: Optional[plt.Figure] = None
) -> Dict[str, Any]:
    result = {
        "visible": False,
        "exists": False,
        "marked_visible": False,
        "has_content": False,
        "within_bounds": False,
        "bbox_info": {},
        "reason": "",
    }

    legend = ax.get_legend()
    if legend is None:
        result["reason"] = "No legend object exists"
        return result

    result["exists"] = True

    if not legend.get_visible():
        result["reason"] = "Legend exists but is marked as not visible"
        return result

    result["marked_visible"] = True

    handles = (
        legend.legendHandles if hasattr(legend, "legendHandles") else legend.get_lines()
    )
    labels = [t.get_text() for t in legend.get_texts()]

    if not handles or not labels or all(not label.strip() for label in labels):
        result["reason"] = "Legend exists and is visible but has no content"
        return result

    result["has_content"] = True

    if figure is None:
        figure = ax.get_figure()

    try:
        figure.canvas.draw()

        legend_bbox = legend.get_window_extent()
        fig_bbox = figure.bbox

        result["bbox_info"] = {
            "legend_bbox": {
                "x0": legend_bbox.x0,
                "y0": legend_bbox.y0,
                "x1": legend_bbox.x1,
                "y1": legend_bbox.y1,
                "width": legend_bbox.width,
                "height": legend_bbox.height,
            },
            "figure_bbox": {
                "x0": fig_bbox.x0,
                "y0": fig_bbox.y0,
                "x1": fig_bbox.x1,
                "y1": fig_bbox.y1,
                "width": fig_bbox.width,
                "height": fig_bbox.height,
            },
        }

        legend_in_figure = (
            legend_bbox.x0 < fig_bbox.x1
            and legend_bbox.x1 > fig_bbox.x0
            and legend_bbox.y0 < fig_bbox.y1
            and legend_bbox.y1 > fig_bbox.y0
        )

        if not legend_in_figure:
            result["reason"] = "Legend is positioned outside the visible figure area"
            return result

        if legend_bbox.width <= 0 or legend_bbox.height <= 0:
            result["reason"] = "Legend has zero width or height"
            return result

        result["within_bounds"] = True

        visible_area = min(legend_bbox.x1, fig_bbox.x1) - max(
            legend_bbox.x0, fig_bbox.x0
        )
        visible_area *= min(legend_bbox.y1, fig_bbox.y1) - max(
            legend_bbox.y0, fig_bbox.y0
        )
        legend_area = legend_bbox.width * legend_bbox.height

        if legend_area > 0:
            visibility_ratio = visible_area / legend_area
            result["bbox_info"]["visibility_ratio"] = visibility_ratio

            if visibility_ratio < 0.1:
                result["reason"] = (
                    f"Legend is mostly clipped (only {visibility_ratio:.1%} visible)"
                )
                return result

        result["visible"] = True
        result["reason"] = "Legend is fully visible and properly positioned"

    except Exception as e:
        result["reason"] = f"Error checking legend bounds: {str(e)}"
        return result

    return result


def check_all_subplot_legends(figure: plt.Figure) -> Dict[int, Dict[str, Any]]:
    results = {}

    if hasattr(figure, "axes"):
        for i, ax in enumerate(figure.axes):
            results[i] = is_legend_actually_visible(ax, figure)

    return results


def verify_legend_visibility(
    figure: plt.Figure,
    expected_visible_count: Optional[int] = None,
    fail_on_missing: bool = True,
) -> Dict[str, Any]:
    results = check_all_subplot_legends(figure)

    visible_count = sum(1 for result in results.values() if result["visible"])
    total_count = len(results)

    summary = {
        "total_subplots": total_count,
        "visible_legends": visible_count,
        "missing_legends": total_count - visible_count,
        "success": True,
        "issues": [],
        "details": results,
    }

    print("🔍 LEGEND VISIBILITY VERIFICATION")
    print("=" * 50)
    print(f"Total subplots: {total_count}")
    print(f"Legends visible: {visible_count}")
    print(f"Legends missing: {total_count - visible_count}")
    print()

    for i, result in results.items():
        status = "✅" if result["visible"] else "❌"
        print(f"Subplot {i}: {status} {result['reason']}")

        if not result["visible"]:
            summary["issues"].append(
                {
                    "subplot": i,
                    "reason": result["reason"],
                    "exists": result["exists"],
                    "marked_visible": result["marked_visible"],
                    "has_content": result["has_content"],
                }
            )

    if expected_visible_count is not None and visible_count != expected_visible_count:
        summary["success"] = False
        print(
            f"\n❌ EXPECTED {expected_visible_count} visible legends, but found {visible_count}"
        )

    if visible_count == 0:
        summary["success"] = False
        print("\n❌ CRITICAL: No legends are visible in any subplot!")
    elif visible_count < total_count:
        if fail_on_missing:
            summary["success"] = False
        print(f"\n⚠️  WARNING: {total_count - visible_count} subplot(s) missing legends")

    if summary["success"]:
        print("\n✅ All legend visibility checks passed!")
    else:
        print("\n❌ Legend visibility verification FAILED!")

    return summary
