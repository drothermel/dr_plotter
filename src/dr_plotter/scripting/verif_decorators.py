import functools
import sys
from typing import Optional, Callable, Any, Dict, List, Union, Tuple
import matplotlib.pyplot as plt
from .verification import verify_legend_visibility
from .plot_verification import (
    verify_plot_properties_for_subplot,
    verify_legend_plot_consistency,
    verify_figure_legend_strategy,
)
from .plot_property_extraction import extract_figure_legend_properties
from dr_plotter.utils import get_axes_from_grid


def filter_main_grid_axes(fig_axes):
    grid_axes = []
    main_gridspec = None

    for ax in fig_axes:
        if hasattr(ax, "get_gridspec") and ax.get_gridspec() is not None:
            gs = ax.get_gridspec()
            if main_gridspec is None:
                main_gridspec = gs
            # Only include axes from the main gridspec (exclude auxiliary axes)
            if gs is main_gridspec:
                grid_axes.append(ax)

    return grid_axes


type SubplotCoord = Tuple[int, int]
type ChannelName = str
type ExpectedChannels = Dict[SubplotCoord, List[ChannelName]]


def _print_failure_message(
    name: str,
    expected: int,
    result: Dict[str, Any],
    descriptions: Optional[Dict[int, str]] = None,
) -> None:
    print(f"\n💥 EXAMPLE {name.upper()} FAILED: Legend visibility issues detected!")

    if expected == 0:
        print("   - Expected NO legends (simple plots with no grouping)")
        print(f"   - Found {result['visible_legends']} unexpected legend(s)")
    else:
        print(f"   - Expected {expected} subplot(s) to have visible legends")
        print(f"   - Only {result['visible_legends']} legends are actually visible")
        print(f"   - {result['missing_legends']} legends are missing")

    if descriptions:
        print("\n📋 Expected Configuration:")
        for idx, desc in descriptions.items():
            print(f"   • Subplot {idx}: {desc}")

    if result.get("issues"):
        print("\n📋 Detailed Issues:")
        for issue in result["issues"]:
            print(f"   • Subplot {issue['subplot']}: {issue['reason']}")
            print(
                f"     (exists: {issue['exists']}, marked_visible: {issue['marked_visible']}, has_content: {issue['has_content']})"
            )

    print("\n🔧 This indicates a bug in the legend management system.")
    if expected > 0:
        print("   The plots should show legends for all visual encoding channels.")
    else:
        print("   Simple plots without grouping variables should not have legends.")
    print("   Please check the legend manager implementation.")
    print("   📊 Plot has been saved for visual debugging.")


def verify_plot_properties(
    expected_channels: ExpectedChannels,
    min_unique_threshold: int = 2,
    tolerance: float = 0.05,
    fail_on_missing: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            if isinstance(result, plt.Figure):
                fig = result
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                if isinstance(result[0], plt.Figure):
                    fig = result[0]
                else:
                    raise ValueError(
                        f"@verify_plot_properties requires function to return a Figure, "
                        f"got {type(result[0]).__name__}"
                    )
            else:
                raise ValueError(
                    f"@verify_plot_properties requires function to return a Figure, "
                    f"got {type(result).__name__}"
                )

            name = func.__name__.replace("_", "-")
            if name == "main":
                module_parts = func.__module__.split(".") if func.__module__ else []
                name = module_parts[-1] if module_parts else "example"

            print(f"\n{'=' * 60}")
            print("PLOT PROPERTIES VERIFICATION")
            print(f"{'=' * 60}")

            all_passed = True
            failed_subplots = []

            for subplot_coord, channels in expected_channels.items():
                row, col = subplot_coord

                try:
                    # Filter to only main grid axes, excluding auxiliary axes like colorbars
                    main_grid_axes = filter_main_grid_axes(fig.axes)
                    ax = get_axes_from_grid(main_grid_axes, row, col)
                except (IndexError, AttributeError, AssertionError) as e:
                    print(f"🔴 Could not find axis at position ({row}, {col}): {e}")
                    all_passed = False
                    continue

                print(f"\n📊 Verifying subplot [{row},{col}]: {channels}")
                print("-" * 50)

                subplot_result = verify_plot_properties_for_subplot(
                    ax, channels, min_unique_threshold, tolerance
                )

                print(f"Collections found: {subplot_result['collections_found']}")

                for channel, channel_result in subplot_result["channels"].items():
                    print(channel_result["message"])
                    if (
                        channel_result["passed"]
                        and channel_result["details"]["sample_values"]
                    ):
                        sample = channel_result["details"]["sample_values"]
                        print(f"   - Sample values: {sample}")

                if not subplot_result["overall_passed"]:
                    all_passed = False
                    failed_subplots.append(f"[{row},{col}]")
                    print(f"\n{subplot_result['summary_message']}")

                    if subplot_result["suggestions"]:
                        print("Suggestions:")
                        for suggestion in subplot_result["suggestions"]:
                            print(f"   • {suggestion}")
                else:
                    print(f"\n{subplot_result['summary_message']}")

            # Check if legend verification also failed
            legend_verification_failed = getattr(
                result, "_legend_verification_failed", False
            )
            legend_failure_types = getattr(result, "_legend_failure_types", [])

            # Collect all failure types
            all_failure_types = list(legend_failure_types)  # Copy the list

            if not all_passed and fail_on_missing:
                print("\n💥 PLOT PROPERTIES VERIFICATION FAILED!")
                print(f"   - Failed subplots: {', '.join(failed_subplots)}")
                print("   - This indicates issues with visual encoding channels")
                print("   📊 Plot has been saved for visual debugging.")
                all_failure_types.append("plot properties")
            elif all_passed:
                print("\n🎉 SUCCESS: All plot properties verified successfully!")
                print("   - All expected visual channels show proper variation")

            # Final exit decision
            if all_failure_types:
                print(
                    f"\n🔥 FINAL RESULT: VERIFICATION FAILED - {' and '.join(all_failure_types)}"
                )
                sys.exit(1)
            elif not legend_verification_failed:  # Both passed
                print("\n🎉 FINAL RESULT: ALL VERIFICATIONS PASSED!")

            return result

        wrapper.__wrapped__ = func

        return wrapper

    return decorator


def verify_example(
    expected_legends: int = 0,
    fail_on_missing: bool = True,
    subplot_descriptions: Optional[Dict[int, str]] = None,
    verify_legend_consistency: bool = False,
    expected_legend_entries: Optional[
        Dict[SubplotCoord, Dict[str, Union[int, str]]]
    ] = None,
    legend_tolerance: float = 0.1,
    expected_channels: Optional[ExpectedChannels] = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            if isinstance(result, plt.Figure):
                figs = [result]
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                # Handle list/tuple of figures
                if all(isinstance(f, plt.Figure) for f in result):
                    figs = list(result)
                elif isinstance(result[0], plt.Figure):
                    figs = [result[0]]
                else:
                    raise ValueError(
                        f"@verify_example requires function to return Figure(s), "
                        f"got {type(result[0]).__name__} in {type(result).__name__}"
                    )
            else:
                raise ValueError(
                    f"@verify_example requires function to return a Figure or list of Figures, "
                    f"got {type(result).__name__}"
                )

            name = func.__name__.replace("_", "-")
            if name == "main":
                module_parts = func.__module__.split(".") if func.__module__ else []
                name = module_parts[-1] if module_parts else "example"

            print(f"\n{'=' * 60}")
            print("LEGEND VISIBILITY VERIFICATION")
            print(f"{'=' * 60}")

            legend_failed = False
            consistency_failed = False

            # Original legend visibility verification
            if len(figs) == 1:
                verification_result = verify_legend_visibility(
                    figs[0],
                    expected_visible_count=expected_legends,
                    fail_on_missing=fail_on_missing if expected_legends > 0 else False,
                )

                if not verification_result["success"]:
                    legend_failed = True
                    _print_failure_message(
                        name,
                        expected_legends,
                        verification_result,
                        subplot_descriptions,
                    )
            else:
                # Multiple figures verification
                print(f"Verifying {len(figs)} individual plots...")
                failed_plots = []

                for i, fig in enumerate(figs):
                    verification_result = verify_legend_visibility(
                        fig,
                        expected_visible_count=expected_legends,
                        fail_on_missing=fail_on_missing
                        if expected_legends > 0
                        else False,
                    )

                    if not verification_result["success"]:
                        failed_plots.append(f"Plot {i + 1}")

                if failed_plots:
                    legend_failed = True
                    print(
                        f"\n💥 EXAMPLE {name.upper()} FAILED: {len(failed_plots)} plots had legend issues!"
                    )
                    print(f"   - Failed plots: {', '.join(failed_plots)}")

            # NEW: Legend-plot consistency verification
            if verify_legend_consistency and len(figs) == 1:
                print(f"\n{'=' * 60}")
                print("LEGEND-PLOT CONSISTENCY VERIFICATION")
                print(f"{'=' * 60}")

                fig = figs[0]

                # Use expected_channels passed to this decorator
                expected_channels_map = expected_channels or {}

                if expected_legend_entries:
                    for subplot_coord, _ in expected_legend_entries.items():
                        row, col = subplot_coord

                        try:
                            ax = (
                                fig.axes[row * 2 + col]
                                if len(fig.axes) > row * 2 + col
                                else fig.axes[0]
                            )

                            print(
                                f"\n📊 Checking legend consistency for subplot [{row},{col}]"
                            )
                            print("-" * 50)

                            # Get expected varying channels for this subplot
                            expected_varying_channels = expected_channels_map.get(
                                subplot_coord, []
                            )

                            consistency_result = verify_legend_plot_consistency(
                                ax,
                                expected_varying_channels,
                                expected_legend_entries.get(subplot_coord),
                                legend_tolerance,
                            )

                            print(consistency_result["message"])

                            for check_name, check_result in consistency_result[
                                "consistency_checks"
                            ].items():
                                print(f"   {check_result['message']}")

                            if not consistency_result["overall_passed"]:
                                consistency_failed = True
                                if consistency_result["suggestions"]:
                                    print("Suggestions:")
                                    for suggestion in consistency_result["suggestions"]:
                                        print(f"   • {suggestion}")

                        except (IndexError, AttributeError):
                            print(f"🔴 Could not find axis at position ({row}, {col})")
                            consistency_failed = True

            # Check if plot properties verification also failed
            plot_properties_failed = getattr(result, "_plot_properties_failed", False)

            # Final results - collect all failure types
            failure_types = []
            if plot_properties_failed:
                failure_types.append("plot properties")
            if legend_failed:
                failure_types.append("legend visibility")
            if consistency_failed:
                failure_types.append("legend consistency")

            if failure_types:
                print(f"\n💥 VERIFICATION FAILED: {' and '.join(failure_types)}")
                # Mark failures but don't exit yet - let other decorators run
                result._legend_verification_failed = True
                result._legend_failure_types = failure_types
            else:
                success_parts = []
                if hasattr(result, "_plot_properties_failed"):
                    success_parts.append("Plot properties verified!")

                if expected_legends == 0:
                    success_parts.append("No unexpected legends found - plot is clean!")
                else:
                    success_parts.append(
                        f"All {expected_legends} expected legends verified!"
                    )

                if verify_legend_consistency:
                    success_parts.append("Legend-plot consistency confirmed!")

                print(f"\n🎉 SUCCESS: {' '.join(success_parts)}")

            return result

        wrapper.__wrapped__ = func
        wrapper._verify_expected = expected_legends
        wrapper._verify_consistency = verify_legend_consistency

        return wrapper

    return decorator


def verify_figure_legends(
    expected_legend_count: int,
    legend_strategy: str,
    expected_total_entries: Optional[int] = None,
    expected_channel_entries: Optional[Dict[str, int]] = None,
    expected_channels: Optional[List[str]] = None,
    tolerance: float = 0.1,
    fail_on_missing: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            if isinstance(result, plt.Figure):
                fig = result
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                if isinstance(result[0], plt.Figure):
                    fig = result[0]
                else:
                    raise ValueError(
                        f"@verify_figure_legends requires function to return a Figure, "
                        f"got {type(result[0]).__name__}"
                    )
            else:
                raise ValueError(
                    f"@verify_figure_legends requires function to return a Figure, "
                    f"got {type(result).__name__}"
                )

            print(f"\n{'=' * 60}")
            print("FIGURE LEGEND VERIFICATION")
            print(f"Strategy: {legend_strategy.upper()}")
            print(f"{'=' * 60}")

            figure_props = extract_figure_legend_properties(fig)

            verification_result = verify_figure_legend_strategy(
                figure_props,
                legend_strategy,
                expected_legend_count,
                expected_total_entries,
                expected_channel_entries,
                expected_channels,
                tolerance,
            )

            print(f"Figure legends found: {figure_props['legend_count']}")
            print(f"Expected: {expected_legend_count}")
            print(verification_result["message"])

            for check_name, check_result in verification_result["checks"].items():
                print(f"   {check_result['message']}")

            if not verification_result["passed"] and fail_on_missing:
                print("\n💥 FIGURE LEGEND VERIFICATION FAILED!")
                print("   This indicates issues with figure-level legend management")
                sys.exit(1)
            elif verification_result["passed"]:
                print("\n🎉 SUCCESS: Figure legend verification passed!")

            return result

        return wrapper

    return decorator


def extract_basic_subplot_info(ax: Any) -> Dict[str, Any]:
    import matplotlib.colors as mcolors

    info = {
        "title": ax.get_title() or "(no title)",
        "xlabel": ax.get_xlabel() or "(no xlabel)",
        "ylabel": ax.get_ylabel() or "(no ylabel)",
        "lines": [],
        "legend": {},
    }

    # Extract line colors
    for i, line in enumerate(ax.lines):
        color = line.get_color()
        normalized_color = mcolors.to_hex(color)
        info["lines"].append({"index": i, "color": normalized_color})

    # Extract legend information
    legend = ax.get_legend()
    if legend is not None and legend.get_visible():
        try:
            # Get legend labels
            labels = [text.get_text() for text in legend.get_texts()]

            # Get legend handles (proxy artists)
            handles = (
                legend.legend_handles
                if hasattr(legend, "legend_handles")
                else legend.get_lines()
            )

            # Extract colors from handles
            legend_colors = []
            for handle in handles:
                try:
                    if hasattr(handle, "get_color"):
                        color = handle.get_color()
                    elif hasattr(handle, "get_markerfacecolor"):
                        color = handle.get_markerfacecolor()
                        if color == "none" or color is None:
                            color = (
                                handle.get_color()
                                if hasattr(handle, "get_color")
                                else "black"
                            )
                    else:
                        color = "unknown"

                    normalized_color = (
                        mcolors.to_hex(color) if color != "unknown" else "unknown"
                    )
                    legend_colors.append(normalized_color)
                except Exception:
                    legend_colors.append("unknown")

            # Create color-to-label mapping
            color_label_pairs = []
            for i, (color, label) in enumerate(zip(legend_colors, labels)):
                color_label_pairs.append(
                    {
                        "index": i,
                        "color": color,
                        "label": label.strip() if label else "(empty)",
                    }
                )

            info["legend"] = {
                "visible": True,
                "entries": color_label_pairs,
                "entry_count": len(labels),
            }

        except Exception as e:
            info["legend"] = {
                "visible": True,
                "entries": [],
                "entry_count": 0,
                "error": str(e),
            }
    else:
        info["legend"] = {"visible": False, "entries": [], "entry_count": 0}

    return info


def report_subplot_line_colors() -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            if isinstance(result, plt.Figure):
                fig = result
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                if isinstance(result[0], plt.Figure):
                    fig = result[0]
                else:
                    raise ValueError(
                        f"@report_subplot_line_colors requires function to return a Figure, "
                        f"got {type(result[0]).__name__}"
                    )
            else:
                raise ValueError(
                    f"@report_subplot_line_colors requires function to return a Figure, "
                    f"got {type(result).__name__}"
                )

            print(f"\n{'=' * 60}")
            print("SUBPLOT LINE COLORS REPORT")
            print(f"{'=' * 60}")

            main_grid_axes = filter_main_grid_axes(fig.axes)

            subplot_infos = []
            for i, ax in enumerate(main_grid_axes):
                info = extract_basic_subplot_info(ax)
                subplot_infos.append(info)

                print(f"\nSubplot {i}:")
                print(f'   Title: "{info["title"]}"')
                print(f'   X-label: "{info["xlabel"]}"')
                print(f'   Y-label: "{info["ylabel"]}"')
                print("   Lines:")

                if info["lines"]:
                    for line_info in info["lines"]:
                        print(f"     Line {line_info['index']}: {line_info['color']}")
                else:
                    print("     (no lines found)")

                print("   Legend:")
                if info["legend"]["visible"]:
                    if info["legend"]["entries"]:
                        for entry in info["legend"]["entries"]:
                            print(f'     {entry["color"]}: "{entry["label"]}"')
                    else:
                        error_msg = info["legend"].get("error", "unknown error")
                        print(
                            f"     (legend visible but extraction failed: {error_msg})"
                        )
                else:
                    print("     (no legend found)")

            # Basic consistency check
            print(f"\n{'=' * 60}")
            print("BASIC CONSISTENCY SUMMARY")
            print(f"{'=' * 60}")

            if subplot_infos:
                # Check if all subplots have same number of lines
                line_counts = [len(info["lines"]) for info in subplot_infos]
                if len(set(line_counts)) == 1:
                    print(f"✅ All subplots have {line_counts[0]} lines")

                    # Check color consistency by position
                    num_lines = line_counts[0]
                    for pos in range(num_lines):
                        colors_at_pos = [
                            info["lines"][pos]["color"]
                            for info in subplot_infos
                            if len(info["lines"]) > pos
                        ]
                        unique_colors = set(colors_at_pos)

                        if len(unique_colors) == 1:
                            color = list(unique_colors)[0]
                            print(
                                f"✅ Position {pos}: {color} (consistent across {len(colors_at_pos)} subplots)"
                            )
                        else:
                            print(
                                f"❌ Position {pos}: {len(unique_colors)} different colors found"
                            )
                            for color in unique_colors:
                                count = colors_at_pos.count(color)
                                print(f"     {color}: {count} subplots")
                else:
                    print(f"❌ Inconsistent line counts: {line_counts}")
            else:
                print("❌ No subplots found")

            return result

        return wrapper

    return decorator
