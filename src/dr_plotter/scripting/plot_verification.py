from typing import Any, Dict, List, Optional, Tuple, Union

from .unified_verification_engine import execute_verification
from .plot_property_extraction import extract_subplot_properties


type SubplotCoord = Tuple[int, int]
type ChannelName = str
type ExpectedChannels = Dict[SubplotCoord, List[ChannelName]]
type VerificationResult = Dict[str, Any]


def verify_channel_variation(
    collections: List[Dict[str, Any]], channel: str, min_unique_threshold: int = 2
) -> VerificationResult:
    return execute_verification(
        "channel_variation",
        {
            "collections": collections,
            "channel": channel,
            "min_unique_threshold": min_unique_threshold,
        },
    )


def verify_plot_properties_for_subplot(
    ax: Any,
    expected_channels: List[str],
    min_unique_threshold: int = 2,
    tolerance: Optional[float] = None,
) -> Dict[str, Any]:
    props = extract_subplot_properties(ax)

    result = {
        "subplot_coord": getattr(ax, "_subplot_spec", "unknown"),
        "collections_found": len(props["collections"]),
        "channels": {},
        "overall_passed": True,
        "summary_message": "",
        "suggestions": [],
    }

    if not props["collections"]:
        result["overall_passed"] = False
        result["summary_message"] = "No collections found in subplot"
        result["suggestions"].append("Check if plot was created successfully")
        return result

    passed_channels = []
    failed_channels = []

    for channel in expected_channels:
        channel_result = execute_verification(
            "channel_variation",
            {
                "collections": props["collections"],
                "channel": channel,
                "min_unique_threshold": min_unique_threshold,
            },
        )
        result["channels"][channel] = channel_result

        if channel_result["passed"]:
            passed_channels.append(channel)
        else:
            failed_channels.append(channel)

    result["overall_passed"] = len(failed_channels) == 0

    if result["overall_passed"]:
        result["summary_message"] = (
            f"All channels verified: {', '.join(passed_channels)}"
        )
    else:
        result["summary_message"] = (
            f"Channel verification failed: {', '.join(failed_channels)}"
        )

        for channel in failed_channels:
            if channel == "size":
                result["suggestions"].append(
                    "Check if size_by parameter is properly configured"
                )
            elif channel in ["hue", "color"]:
                result["suggestions"].append(
                    "Check if hue_by parameter creates color variation"
                )
            elif channel == "marker":
                result["suggestions"].append(
                    "Check if marker_by parameter creates marker variation"
                )
            elif channel == "alpha":
                result["suggestions"].append(
                    "Check if alpha_by parameter creates alpha variation"
                )

    return result


def verify_marker_consistency(
    plot_markers: List[str],
    legend_markers: List[str],
    expected_unique_markers: int = None,
) -> Dict[str, Any]:
    return execute_verification(
        "consistency_check",
        {
            "channel": "marker",
            "plot_data": plot_markers,
            "legend_data": legend_markers,
            "expected_unique": expected_unique_markers,
        },
    )


def verify_color_consistency(
    plot_colors: List[Tuple[float, ...]],
    legend_colors: List[Tuple[float, ...]],
    tolerance: Optional[float] = None,
) -> Dict[str, Any]:
    return execute_verification(
        "consistency_check",
        {
            "channel": "color",
            "plot_data": plot_colors,
            "legend_data": legend_colors,
            "tolerance": tolerance,
        },
    )


def verify_alpha_consistency(
    plot_alphas: List[float],
    legend_alphas: List[float],
    tolerance: Optional[float] = None,
) -> Dict[str, Any]:
    return execute_verification(
        "consistency_check",
        {
            "channel": "alpha",
            "plot_data": plot_alphas,
            "legend_data": legend_alphas,
            "tolerance": tolerance,
        },
    )


def verify_size_consistency(
    plot_sizes: List[float],
    legend_sizes: List[float],
    tolerance: Optional[float] = None,
) -> Dict[str, Any]:
    return execute_verification(
        "consistency_check",
        {
            "channel": "size",
            "plot_data": plot_sizes,
            "legend_data": legend_sizes,
            "tolerance": tolerance,
        },
    )


def verify_style_consistency(
    plot_styles: List[str], legend_styles: List[str], expected_unique_styles: int = None
) -> Dict[str, Any]:
    return execute_verification(
        "consistency_check",
        {
            "channel": "style",
            "plot_data": plot_styles,
            "legend_data": legend_styles,
            "expected_unique": expected_unique_styles,
        },
    )


def verify_channel_uniformity(
    values: List[Any], channel: str, tolerance: float = None
) -> Dict[str, Any]:
    return execute_verification(
        "channel_uniformity",
        {"values": values, "channel": channel, "tolerance": tolerance},
    )


def verify_legend_plot_consistency(
    ax: Any,
    expected_varying_channels: Optional[List[str]] = None,
    expected_legend_entries: Optional[Dict[str, Union[int, str]]] = None,
    tolerance: Optional[float] = None,
) -> Dict[str, Any]:
    return execute_verification(
        "legend_plot_consistency",
        {
            "ax": ax,
            "expected_varying_channels": expected_varying_channels,
            "expected_legend_entries": expected_legend_entries,
            "tolerance": tolerance,
        },
    )


def verify_figure_legend_strategy(
    figure_props: Dict[str, Any],
    strategy: str,
    expected_count: int,
    expected_total_entries: Optional[int],
    expected_channel_entries: Optional[Dict[str, int]],
    expected_channels: Optional[List[str]],
    tolerance: float,
) -> Dict[str, Any]:
    return execute_verification(
        "figure_legend_strategy",
        {
            "figure_props": figure_props,
            "strategy": strategy,
            "expected_count": expected_count,
            "expected_total_entries": expected_total_entries,
            "expected_channel_entries": expected_channel_entries,
            "expected_channels": expected_channels,
            "tolerance": tolerance,
        },
    )


def verify_unified_figure_strategy(
    figure_props: Dict[str, Any],
    expected_total_entries: Optional[int],
    result: Dict[str, Any],
    tolerance: float,
) -> Dict[str, Any]:
    return execute_verification(
        "figure_legend_strategy",
        {
            "figure_props": figure_props,
            "strategy": "figure_below",
            "expected_count": 1,
            "expected_total_entries": expected_total_entries,
            "expected_channel_entries": None,
            "expected_channels": None,
            "tolerance": tolerance,
        },
    )


def verify_split_figure_strategy(
    figure_props: Dict[str, Any],
    expected_channel_entries: Optional[Dict[str, int]],
    expected_channels: Optional[List[str]],
    result: Dict[str, Any],
    tolerance: float,
) -> Dict[str, Any]:
    expected_count = len(expected_channels) if expected_channels else 0
    return execute_verification(
        "figure_legend_strategy",
        {
            "figure_props": figure_props,
            "strategy": "split",
            "expected_count": expected_count,
            "expected_total_entries": None,
            "expected_channel_entries": expected_channel_entries,
            "expected_channels": expected_channels,
            "tolerance": tolerance,
        },
    )
