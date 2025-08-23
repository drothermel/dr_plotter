import functools
import sys
from typing import Optional, Callable, Any, Dict
import matplotlib.pyplot as plt
from .verification import verify_legend_visibility


def verify_example(
    expected_legends: int = 0,
    fail_on_missing: bool = True,
    subplot_descriptions: Optional[Dict[int, str]] = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            if isinstance(result, plt.Figure):
                fig = result
            elif (
                isinstance(result, tuple)
                and len(result) >= 1
                and isinstance(result[0], plt.Figure)
            ):
                fig = result[0]
            else:
                raise ValueError(
                    f"@verify_example requires function to return a Figure, "
                    f"got {type(result).__name__}"
                )

            name = func.__name__.replace("_", "-")
            if name == "main":
                module_parts = func.__module__.split(".") if func.__module__ else []
                name = module_parts[-1] if module_parts else "example"

            print(f"\n{'=' * 60}")
            print("LEGEND VISIBILITY VERIFICATION")
            print(f"{'=' * 60}")

            verification_result = verify_legend_visibility(
                fig,
                expected_visible_count=expected_legends,
                fail_on_missing=fail_on_missing if expected_legends > 0 else False,
            )

            if not verification_result["success"]:
                _print_failure_message(
                    name, expected_legends, verification_result, subplot_descriptions
                )
                sys.exit(1)

            if expected_legends == 0:
                print(
                    "\n🎉 SUCCESS: No unexpected legends found - plot is clean as expected!"
                )
            else:
                print(
                    f"\n🎉 SUCCESS: All {expected_legends} expected legends are visible and properly positioned!"
                )

            return result

        wrapper.__wrapped__ = func
        wrapper._verify_expected = expected_legends

        return wrapper

    return decorator


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
