from typing import Any, Dict, List, Optional, Set, Tuple, Union
import matplotlib.colors as mcolors

from .plot_property_extraction import extract_subplot_properties


type SubplotCoord = Tuple[int, int]
type ChannelName = str
type ExpectedChannels = Dict[SubplotCoord, List[ChannelName]]
type VerificationResult = Dict[str, Any]


def format_sample_values(values: List[Any], max_count: int = 5) -> List[Any]:
    limited_values = values[:max_count] if len(values) > max_count else values
    formatted_values = []

    for value in limited_values:
        if isinstance(value, (tuple, list)) and len(value) >= 3:
            if all(isinstance(x, float) for x in value):
                formatted_values.append(tuple(round(x, 3) for x in value))
            else:
                formatted_values.append(value)
        elif isinstance(value, float):
            formatted_values.append(round(value, 3))
        else:
            formatted_values.append(value)

    return formatted_values


def verify_channel_variation(
    collections: List[Dict[str, Any]], channel: str, min_unique_threshold: int = 2
) -> VerificationResult:
    result = {
        "channel": channel,
        "passed": False,
        "unique_values": 0,
        "total_points": 0,
        "details": {},
        "message": "",
    }

    if not collections:
        result["message"] = f"No collections found to verify {channel} variation"
        return result

    all_values = []

    if channel == "size":
        for collection in collections:
            all_values.extend(collection["sizes"])
    elif channel == "hue" or channel == "color":
        for collection in collections:
            all_values.extend(collection["colors"])
    elif channel == "marker":
        for collection in collections:
            all_values.extend(collection["markers"])
    elif channel == "alpha":
        for collection in collections:
            # For lines, use separate alphas field if available
            if "alphas" in collection and collection["alphas"]:
                all_values.extend(collection["alphas"])
            else:
                # Extract alpha from RGBA colors (scatter/bar)
                for rgba in collection["colors"]:
                    if len(rgba) == 4:
                        all_values.append(rgba[3])
                    else:
                        all_values.append(1.0)
    elif channel == "style":
        for collection in collections:
            if "styles" in collection:
                all_values.extend(collection["styles"])
    else:
        result["message"] = f"Unknown channel: {channel}"
        return result

    # Count unique values (with tolerance for floats)
    if channel in ["size", "alpha"]:
        unique_values = _count_unique_floats(all_values, tolerance=1e-6)
    elif channel in ["hue", "color"]:
        unique_values = _count_unique_colors(all_values, tolerance=1e-6)
    else:
        unique_values = set(all_values)

    result["unique_values"] = len(unique_values)
    result["total_points"] = len(all_values)

    # Format sample values with rounding for readability
    raw_samples = (
        list(unique_values)[:5]
        if isinstance(unique_values, (set, list))
        else sorted(list(unique_values))[:5]
    )
    result["details"]["sample_values"] = format_sample_values(raw_samples)
    result["passed"] = len(unique_values) >= min_unique_threshold

    if result["passed"]:
        result["message"] = (
            f"✅ {channel.title()} variation: PASS ({len(unique_values)} unique values found)"
        )
    else:
        result["message"] = (
            f"🔴 {channel.title()} variation: FAIL (only {len(unique_values)} unique values, expected ≥{min_unique_threshold})"
        )

        if len(unique_values) == 1:
            sample_val = next(iter(unique_values)) if unique_values else "none"
            result["message"] += f"\n   - All points have {channel}: {sample_val}"

    return result


def _count_unique_floats(values: List[float], tolerance: float = 1e-6) -> Set[float]:
    unique = set()
    for val in values:
        is_duplicate = False
        for existing in unique:
            if abs(val - existing) < tolerance:
                is_duplicate = True
                break
        if not is_duplicate:
            unique.add(val)
    return unique


def _count_unique_colors(
    colors: List[Tuple[float, ...]], tolerance: float = 1e-6
) -> Set[Tuple[float, ...]]:
    unique = set()
    for color in colors:
        is_duplicate = False
        for existing in unique:
            if len(color) == len(existing) and all(
                abs(a - b) < tolerance for a, b in zip(color, existing)
            ):
                is_duplicate = True
                break
        if not is_duplicate:
            unique.add(color)
    return unique


def verify_plot_properties_for_subplot(
    ax: Any,
    expected_channels: List[str],
    min_unique_threshold: int = 2,
    tolerance: float = 0.05,
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
        result["summary_message"] = "🔴 No collections found in subplot"
        result["suggestions"].append("Check if plot was created successfully")
        return result

    # Verify each expected channel
    passed_channels = []
    failed_channels = []

    for channel in expected_channels:
        channel_result = verify_channel_variation(
            props["collections"], channel, min_unique_threshold
        )
        result["channels"][channel] = channel_result

        if channel_result["passed"]:
            passed_channels.append(channel)
        else:
            failed_channels.append(channel)

    result["overall_passed"] = len(failed_channels) == 0

    # Build summary message
    if result["overall_passed"]:
        result["summary_message"] = (
            f"✅ All channels verified: {', '.join(passed_channels)}"
        )
    else:
        result["summary_message"] = (
            f"🔴 Channel verification failed: {', '.join(failed_channels)}"
        )

        # Add specific suggestions
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
    plot_unique = set(plot_markers)
    legend_unique = set(legend_markers)

    result = {
        "passed": plot_unique == legend_unique,
        "plot_markers": sorted(plot_unique),
        "legend_markers": sorted(legend_unique),
        "missing_from_legend": sorted(plot_unique - legend_unique),
        "extra_in_legend": sorted(legend_unique - plot_unique),
        "message": "",
    }

    if expected_unique_markers and len(plot_unique) != expected_unique_markers:
        result["passed"] = False
        result["message"] = (
            f"🔴 Expected {expected_unique_markers} unique markers in plot, found {len(plot_unique)}"
        )
        return result

    if result["passed"]:
        result["message"] = (
            f"✅ Marker consistency: PASS ({len(plot_unique)} unique markers match)"
        )
    else:
        result["message"] = "🔴 Marker consistency: FAIL"
        if result["missing_from_legend"]:
            result["message"] += (
                f"\n   - Missing from legend: {result['missing_from_legend']}"
            )
        if result["extra_in_legend"]:
            result["message"] += f"\n   - Extra in legend: {result['extra_in_legend']}"

    return result


def verify_color_consistency(
    plot_colors: List[Tuple[float, ...]],
    legend_colors: List[Tuple[float, ...]],
    tolerance: float = 0.05,
) -> Dict[str, Any]:
    plot_unique = _count_unique_colors(plot_colors, tolerance)
    legend_unique = _count_unique_colors(legend_colors, tolerance)

    # Convert to hex for easier comparison and display
    plot_hex = [mcolors.to_hex(color) for color in plot_unique]
    legend_hex = [mcolors.to_hex(color) for color in legend_unique]

    result = {
        "passed": set(plot_hex) == set(legend_hex),
        "plot_colors": sorted(plot_hex),
        "legend_colors": sorted(legend_hex),
        "message": "",
    }

    if result["passed"]:
        result["message"] = (
            f"✅ Color consistency: PASS ({len(plot_unique)} unique colors match)"
        )
    else:
        result["message"] = "🔴 Color consistency: FAIL"
        result["message"] += f"\n   - Plot colors: {result['plot_colors']}"
        result["message"] += f"\n   - Legend colors: {result['legend_colors']}"

    return result


def verify_alpha_consistency(
    plot_alphas: List[float], legend_alphas: List[float], tolerance: float = 0.05
) -> Dict[str, Any]:
    plot_unique = _count_unique_floats(plot_alphas, tolerance)
    legend_unique = _count_unique_floats(legend_alphas, tolerance)

    result = {
        "passed": len(plot_unique) == len(legend_unique),
        "plot_alpha_range": (min(plot_unique), max(plot_unique))
        if plot_unique
        else (1.0, 1.0),
        "legend_alpha_range": (min(legend_unique), max(legend_unique))
        if legend_unique
        else (1.0, 1.0),
        "plot_unique_count": len(plot_unique),
        "legend_unique_count": len(legend_unique),
        "message": "",
    }

    # More sophisticated check - ranges should overlap significantly
    if plot_unique and legend_unique:
        plot_min, plot_max = min(plot_unique), max(plot_unique)
        legend_min, legend_max = min(legend_unique), max(legend_unique)

        # Check if ranges overlap reasonably
        range_overlap = (min(plot_max, legend_max) - max(plot_min, legend_min)) / max(
            (plot_max - plot_min), 0.1
        )

        if range_overlap > 0.5:  # At least 50% overlap
            result["passed"] = True
            result["message"] = (
                "✅ Alpha consistency: PASS (ranges overlap sufficiently)"
            )
        else:
            result["passed"] = False
            result["message"] = "🔴 Alpha consistency: FAIL (ranges don't overlap)"
    elif result["passed"]:
        result["message"] = (
            f"✅ Alpha consistency: PASS ({len(plot_unique)} alpha values match)"
        )
    else:
        result["message"] = "🔴 Alpha consistency: FAIL"
        result["message"] += f"\n   - Plot alpha range: {result['plot_alpha_range']}"
        result["message"] += (
            f"\n   - Legend alpha range: {result['legend_alpha_range']}"
        )

    return result


def verify_size_consistency(
    plot_sizes: List[float], legend_sizes: List[float], tolerance: float = 0.1
) -> Dict[str, Any]:
    from .plot_property_extraction import convert_legend_size_to_scatter_size

    # Convert legend sizes to scatter size units for comparison
    legend_as_scatter = [
        convert_legend_size_to_scatter_size(size) for size in legend_sizes
    ]

    plot_unique = _count_unique_floats(plot_sizes, tolerance)
    legend_unique = _count_unique_floats(legend_as_scatter, tolerance)

    result = {
        "passed": len(plot_unique) == len(legend_unique),
        "plot_size_range": (min(plot_unique), max(plot_unique))
        if plot_unique
        else (0, 0),
        "legend_size_range": (min(legend_unique), max(legend_unique))
        if legend_unique
        else (0, 0),
        "message": "",
    }

    if result["passed"]:
        result["message"] = "✅ Size consistency: PASS (ranges match within tolerance)"
    else:
        result["message"] = "🔴 Size consistency: FAIL"
        result["message"] += f"\n   - Plot size range: {result['plot_size_range']}"
        result["message"] += f"\n   - Legend size range: {result['legend_size_range']}"

    return result


def verify_style_consistency(
    plot_styles: List[str], legend_styles: List[str], expected_unique_styles: int = None
) -> Dict[str, Any]:
    plot_unique = set(plot_styles)
    legend_unique = set(legend_styles)

    result = {
        "passed": plot_unique == legend_unique,
        "plot_styles": sorted(plot_unique),
        "legend_styles": sorted(legend_unique),
        "missing_from_legend": sorted(plot_unique - legend_unique),
        "extra_in_legend": sorted(legend_unique - plot_unique),
        "message": "",
    }

    if expected_unique_styles and len(plot_unique) != expected_unique_styles:
        result["passed"] = False
        result["message"] = (
            f"🔴 Expected {expected_unique_styles} unique styles in plot, found {len(plot_unique)}"
        )
        return result

    if result["passed"]:
        result["message"] = (
            f"✅ Style consistency: PASS ({len(plot_unique)} unique styles match)"
        )
    else:
        result["message"] = "🔴 Style consistency: FAIL"
        if result["missing_from_legend"]:
            result["message"] += (
                f"\n   - Missing from legend: {result['missing_from_legend']}"
            )
        if result["extra_in_legend"]:
            result["message"] += f"\n   - Extra in legend: {result['extra_in_legend']}"

    return result


def verify_channel_uniformity(
    values: List[Any], channel: str, tolerance: float = 1e-6
) -> Dict[str, Any]:
    result = {
        "channel": channel,
        "passed": False,
        "unique_values": 0,
        "message": "",
        "uniform_value": None,
    }

    if not values:
        result["message"] = f"🔴 {channel.title()} uniformity: No values to check"
        return result

    if channel in ["size", "alpha"]:
        unique_values = _count_unique_floats(values, tolerance)
    elif channel in ["hue", "color"]:
        unique_values = _count_unique_colors(values, tolerance)
    else:
        unique_values = set(values)

    result["unique_values"] = len(unique_values)
    result["passed"] = len(unique_values) == 1

    if result["passed"]:
        result["uniform_value"] = next(iter(unique_values)) if unique_values else None
        result["message"] = (
            f"✅ {channel.title()} uniformity: PASS (all plot values are {result['uniform_value']})"
        )
    else:
        result["message"] = (
            f"🔴 {channel.title()} uniformity: FAIL ({len(unique_values)} different plot values found)"
        )
        raw_samples = (
            list(unique_values)[:3]
            if isinstance(unique_values, (set, list))
            else sorted(list(unique_values))[:3]
        )
        formatted_samples = format_sample_values(raw_samples, max_count=3)
        result["message"] += f"\n   - Plot sample values: {formatted_samples}"

    return result


def verify_legend_plot_consistency(
    ax: Any,
    expected_varying_channels: Optional[List[str]] = None,
    expected_legend_entries: Optional[Dict[str, Union[int, str]]] = None,
    tolerance: float = 0.1,
) -> Dict[str, Any]:
    props = extract_subplot_properties(ax)

    result = {
        "consistency_checks": {},
        "overall_passed": True,
        "message": "",
        "suggestions": [],
    }

    # Extract plot data
    all_plot_markers = []
    all_plot_colors = []
    all_plot_sizes = []
    all_plot_alphas = []
    all_plot_styles = []

    for collection in props["collections"]:
        all_plot_markers.extend(collection["markers"])
        all_plot_colors.extend(collection["colors"])
        all_plot_sizes.extend(collection["sizes"])

        # Handle line-specific alphas and styles
        if "alphas" in collection and collection["alphas"]:
            all_plot_alphas.extend(collection["alphas"])
        else:
            # Extract alpha values from RGBA colors (scatter/bar)
            for rgba_color in collection["colors"]:
                if len(rgba_color) >= 4:
                    all_plot_alphas.append(rgba_color[3])
                else:
                    all_plot_alphas.append(1.0)  # Default alpha

        # Extract line styles if available
        if "styles" in collection:
            all_plot_styles.extend(collection["styles"])

    # Extract legend data
    legend_markers = props["legend"]["markers"]
    legend_colors = props["legend"]["colors"]
    legend_sizes = props["legend"]["sizes"]
    legend_styles = props["legend"]["styles"]
    legend_alphas = []

    # Extract alpha from legend colors
    for rgba_color in legend_colors:
        if len(rgba_color) >= 4:
            legend_alphas.append(rgba_color[3])
        else:
            legend_alphas.append(1.0)

    # Default to checking all channels if none specified
    if expected_varying_channels is None:
        expected_varying_channels = ["hue", "marker", "alpha", "size", "style"]

    # Map channel names to their data and verification functions
    channel_data = {
        "marker": (all_plot_markers, legend_markers, verify_marker_consistency),
        "hue": (
            all_plot_colors,
            legend_colors,
            lambda p, l, t=tolerance: verify_color_consistency(p, l, t),
        ),
        "alpha": (
            all_plot_alphas,
            legend_alphas,
            lambda p, l, t=tolerance: verify_alpha_consistency(p, l, t),
        ),
        "size": (
            all_plot_sizes,
            legend_sizes,
            lambda p, l, t=tolerance: verify_size_consistency(p, l, t),
        ),
        "style": (
            all_plot_styles,
            legend_styles,
            verify_style_consistency,
        ),
    }

    # Check each channel based on whether it should vary or not
    for channel in ["marker", "hue", "alpha", "size", "style"]:
        if channel not in channel_data or not channel_data[channel][0]:
            continue  # Skip if no data available

        plot_data, legend_data, verify_func = channel_data[channel]

        # Determine if this channel should vary based on expected channels
        should_vary = False
        if channel in expected_varying_channels:
            should_vary = True
        # Handle hue/color synonyms - if expected channels contain "color", treat it as "hue"
        elif channel == "hue" and "color" in expected_varying_channels:
            should_vary = True

        if should_vary and legend_data:
            # This channel should vary - check plot-legend consistency
            consistency_check = verify_func(plot_data, legend_data)
            result["consistency_checks"][f"{channel}s"] = consistency_check
            if not consistency_check["passed"]:
                result["overall_passed"] = False
        elif should_vary and not legend_data:
            # This channel should vary but legend data is missing - verify plot has variation
            variation_check = verify_channel_variation(
                [
                    {
                        "colors": all_plot_colors,
                        "markers": all_plot_markers,
                        "sizes": all_plot_sizes,
                    }
                ],
                channel,
            )

            # Create a special message for this case
            if variation_check["passed"]:
                message = f"✅ {channel.title()} variation: VERIFIED (plot shows expected variation, legend data missing)"
            else:
                message = f"🔴 {channel.title()} variation: MISSING (expected variation not found in plot)"

            special_check = {"passed": variation_check["passed"], "message": message}
            result["consistency_checks"][f"{channel}s"] = special_check
            if not special_check["passed"]:
                result["overall_passed"] = False
        elif not should_vary:
            # This channel should NOT vary - check plot uniformity
            uniformity_check = verify_channel_uniformity(plot_data, channel, tolerance)
            result["consistency_checks"][f"{channel}s"] = uniformity_check
            if not uniformity_check["passed"]:
                result["overall_passed"] = False

    # Build overall message
    if result["overall_passed"]:
        checks = list(result["consistency_checks"].keys())
        result["message"] = f"✅ Legend-plot consistency: PASS ({', '.join(checks)})"
    else:
        failed = [k for k, v in result["consistency_checks"].items() if not v["passed"]]
        result["message"] = f"🔴 Legend-plot consistency: FAIL ({', '.join(failed)})"
        result["suggestions"].append("Check legend proxy artist creation")
        result["suggestions"].append(
            "Verify legend manager is creating correct entries"
        )

    return result
