import functools
import sys
from typing import Optional, Callable, Any, Dict, List, Union, Tuple
import matplotlib.pyplot as plt
from .verification_formatter import (
    print_section_header,
    print_subsection_header,
    print_success,
    print_failure,
    print_critical,
    print_final_success,
    print_info,
    print_item_result,
    print_suggestions,
    print_detailed_issues,
)
from .verification import verify_legend_visibility
from .plot_verification import (
    verify_plot_properties_for_subplot,
    verify_legend_plot_consistency,
    verify_figure_legend_strategy,
)
from .plot_data_extractor import extract_figure_legend_properties
from .validation import validate_figure_result, validate_legend_properties
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
    print_critical(f"EXAMPLE {name.upper()} FAILED: Legend visibility issues detected!")

    if expected == 0:
        print_info("- Expected NO legends (simple plots with no grouping)", 1)
        print_info(f"- Found {result['visible_legends']} unexpected legend(s)", 1)
    else:
        print_info(f"- Expected {expected} subplot(s) to have visible legends", 1)
        print_info(
            f"- Only {result['visible_legends']} legends are actually visible", 1
        )
        print_info(f"- {result['missing_legends']} legends are missing", 1)

    if descriptions:
        print_info("Expected Configuration:", 1)
        for idx, desc in descriptions.items():
            print_info(f"• Subplot {idx}: {desc}", 2)

    if result.get("issues"):
        print_detailed_issues(result["issues"], 1)

    print_info("This indicates a bug in the legend management system.")
    if expected > 0:
        print_info("The plots should show legends for all visual encoding channels.", 1)
    else:
        print_info(
            "Simple plots without grouping variables should not have legends.", 1
        )
    print_info("Please check the legend manager implementation.", 1)
    print_info("Plot has been saved for visual debugging.", 1)


def verify_plot_properties(
    expected_channels: ExpectedChannels,
    min_unique_threshold: int = 2,
    tolerance: Optional[float] = None,
    fail_on_missing: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            assert isinstance(result, (plt.Figure, list, tuple)), (
                f"Function must return Figure or list, got {type(result).__name__}"
            )

            if isinstance(result, plt.Figure):
                fig = result
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                assert isinstance(result[0], plt.Figure), (
                    f"Function must return Figure(s), got {type(result[0]).__name__}"
                )
                fig = result[0]
            else:
                assert False, f"Invalid return type: {type(result).__name__}"

            name = func.__name__.replace("_", "-")
            if name == "main":
                module_parts = func.__module__.split(".") if func.__module__ else []
                name = module_parts[-1] if module_parts else "example"

            print_section_header("PLOT PROPERTIES VERIFICATION")

            all_passed = True
            failed_subplots = []

            for subplot_coord, channels in expected_channels.items():
                row, col = subplot_coord

                main_grid_axes = filter_main_grid_axes(fig.axes)
                ax = get_axes_from_grid(main_grid_axes, row, col)

                print_subsection_header(f"Verifying subplot [{row},{col}]: {channels}")

                subplot_result = verify_plot_properties_for_subplot(
                    ax, channels, min_unique_threshold, tolerance
                )

                print_info(f"Collections found: {subplot_result['collections_found']}")

                for channel, channel_result in subplot_result["channels"].items():
                    success = channel_result["passed"]
                    print_item_result(
                        channel_result["channel"], success, channel_result["message"], 1
                    )
                    if (
                        channel_result["passed"]
                        and channel_result["details"]["sample_values"]
                    ):
                        sample = channel_result["details"]["sample_values"]
                        print_info(f"- Sample values: {sample}", 2)

                if not subplot_result["overall_passed"]:
                    all_passed = False
                    failed_subplots.append(f"[{row},{col}]")
                    print_failure(subplot_result["summary_message"], 1)

                    if subplot_result["suggestions"]:
                        print_suggestions(subplot_result["suggestions"], 2)
                else:
                    print_success(subplot_result["summary_message"], 1)

            # Check if legend verification also failed
            legend_verification_failed = getattr(
                result, "_legend_verification_failed", False
            )
            legend_failure_types = getattr(result, "_legend_failure_types", [])

            # Collect all failure types
            all_failure_types = list(legend_failure_types)  # Copy the list

            if not all_passed and fail_on_missing:
                print_critical("PLOT PROPERTIES VERIFICATION FAILED!")
                print_info(f"- Failed subplots: {', '.join(failed_subplots)}", 1)
                print_info("- This indicates issues with visual encoding channels", 1)
                print_info("Plot has been saved for visual debugging.", 1)
                all_failure_types.append("plot properties")
            elif all_passed:
                print_final_success(
                    "SUCCESS: All plot properties verified successfully!"
                )
                print_info("- All expected visual channels show proper variation", 1)

            # Final exit decision
            if all_failure_types:
                print_critical(
                    f"FINAL RESULT: VERIFICATION FAILED - {' and '.join(all_failure_types)}"
                )
                sys.exit(1)
            elif not legend_verification_failed:  # Both passed
                print_final_success("FINAL RESULT: ALL VERIFICATIONS PASSED!")

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
    legend_tolerance: Optional[float] = None,
    expected_channels: Optional[ExpectedChannels] = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            assert isinstance(result, (plt.Figure, list, tuple)), (
                f"Function must return Figure or list/tuple, got {type(result).__name__}"
            )

            if isinstance(result, plt.Figure):
                figs = [result]
            elif isinstance(result, (list, tuple)) and len(result) >= 1:
                if all(isinstance(f, plt.Figure) for f in result):
                    figs = list(result)
                elif isinstance(result[0], plt.Figure):
                    figs = [result[0]]
                else:
                    assert False, (
                        f"Function must return Figure(s), got {type(result[0]).__name__} in {type(result).__name__}"
                    )
            else:
                assert False, (
                    f"Function must return Figure or list of Figures, got {type(result).__name__}"
                )

            name = func.__name__.replace("_", "-")
            if name == "main":
                module_parts = func.__module__.split(".") if func.__module__ else []
                name = module_parts[-1] if module_parts else "example"

            print_section_header("LEGEND VISIBILITY VERIFICATION")

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
                print_info(f"Verifying {len(figs)} individual plots...")
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
                    print_critical(
                        f"EXAMPLE {name.upper()} FAILED: {len(failed_plots)} plots had legend issues!"
                    )
                    print_info(f"- Failed plots: {', '.join(failed_plots)}", 1)

            # NEW: Legend-plot consistency verification
            if verify_legend_consistency and len(figs) == 1:
                print_section_header("LEGEND-PLOT CONSISTENCY VERIFICATION")

                fig = figs[0]

                # Use expected_channels passed to this decorator
                expected_channels_map = expected_channels or {}

                if expected_legend_entries:
                    for subplot_coord, _ in expected_legend_entries.items():
                        row, col = subplot_coord

                        main_grid_axes = filter_main_grid_axes(fig.axes)
                        ax = get_axes_from_grid(main_grid_axes, row, col)

                        assert ax is not None, (
                            f"No axis found at position ({row}, {col})"
                        )

                        print_subsection_header(
                            f"Checking legend consistency for subplot [{row},{col}]"
                        )

                        expected_varying_channels = expected_channels_map.get(
                            subplot_coord, []
                        )

                        consistency_result = verify_legend_plot_consistency(
                            ax,
                            expected_varying_channels,
                            expected_legend_entries.get(subplot_coord),
                            legend_tolerance,
                        )

                        success = consistency_result["overall_passed"]
                        if success:
                            print_success(consistency_result["message"], 1)
                        else:
                            print_failure(consistency_result["message"], 1)

                        for check_name, check_result in consistency_result[
                            "consistency_checks"
                        ].items():
                            success = check_result["passed"]
                            if success:
                                print_success(check_result["message"], 2)
                            else:
                                print_failure(check_result["message"], 2)

                        if not consistency_result["overall_passed"]:
                            consistency_failed = True
                            if consistency_result["suggestions"]:
                                print_suggestions(consistency_result["suggestions"], 2)

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
                print_critical(f"VERIFICATION FAILED: {' and '.join(failure_types)}")
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

                print_final_success(f"SUCCESS: {' '.join(success_parts)}")

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
    tolerance: Optional[float] = None,
    fail_on_missing: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            fig = validate_figure_result(result)

            print_section_header("FIGURE LEGEND VERIFICATION")
            print_info(f"Strategy: {legend_strategy.upper()}")

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

            print_info(f"Figure legends found: {figure_props['legend_count']}")
            print_info(f"Expected: {expected_legend_count}")
            success = verification_result["passed"]
            if success:
                print_success(verification_result["message"], 1)
            else:
                print_failure(verification_result["message"], 1)

            for check_name, check_result in verification_result["checks"].items():
                success = check_result["passed"]
                if success:
                    print_success(check_result["message"], 1)
                else:
                    print_failure(check_result["message"], 1)

            if not verification_result["passed"] and fail_on_missing:
                print_critical("FIGURE LEGEND VERIFICATION FAILED!")
                print_info(
                    "This indicates issues with figure-level legend management", 1
                )
                sys.exit(1)
            elif verification_result["passed"]:
                print_final_success("SUCCESS: Figure legend verification passed!")

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

    for i, line in enumerate(ax.lines):
        color = line.get_color()
        normalized_color = mcolors.to_hex(color)
        info["lines"].append({"index": i, "color": normalized_color})

    info["legend"] = validate_legend_properties(ax)

    return info


def report_subplot_line_colors() -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            fig = validate_figure_result(result)

            print_section_header("SUBPLOT LINE COLORS REPORT")

            main_grid_axes = filter_main_grid_axes(fig.axes)

            subplot_infos = []
            for i, ax in enumerate(main_grid_axes):
                info = extract_basic_subplot_info(ax)
                subplot_infos.append(info)

                print_info(f"Subplot {i}:")
                print_info(f'Title: "{info["title"]}"', 1)
                print_info(f'X-label: "{info["xlabel"]}"', 1)
                print_info(f'Y-label: "{info["ylabel"]}"', 1)
                print_info("Lines:", 1)

                if info["lines"]:
                    for line_info in info["lines"]:
                        print_info(
                            f"Line {line_info['index']}: {line_info['color']}", 2
                        )
                else:
                    print_info("(no lines found)", 2)

                print_info("Legend:", 1)
                if info["legend"]["visible"]:
                    if info["legend"]["entries"]:
                        for entry in info["legend"]["entries"]:
                            print_info(f'{entry["color"]}: "{entry["label"]}"', 2)
                    else:
                        error_msg = info["legend"].get("error", "unknown error")
                        print_info(
                            f"(legend visible but extraction failed: {error_msg})", 2
                        )
                else:
                    print_info("(no legend found)", 2)

            # Basic consistency check
            print_section_header("BASIC CONSISTENCY SUMMARY")

            if subplot_infos:
                # Check if all subplots have same number of lines
                line_counts = [len(info["lines"]) for info in subplot_infos]
                if len(set(line_counts)) == 1:
                    print_success(f"All subplots have {line_counts[0]} lines", 1)

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
                            print_success(
                                f"Position {pos}: {color} (consistent across {len(colors_at_pos)} subplots)",
                                1,
                            )
                        else:
                            print_failure(
                                f"Position {pos}: {len(unique_colors)} different colors found",
                                1,
                            )
                            for color in unique_colors:
                                count = colors_at_pos.count(color)
                                print_info(f"{color}: {count} subplots", 2)
                else:
                    print_failure(f"Inconsistent line counts: {line_counts}", 1)
            else:
                print_failure("No subplots found", 1)

            return result

        return wrapper

    return decorator
