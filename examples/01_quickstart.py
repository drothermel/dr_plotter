"""
Example 1: Quickstart - Simplest possible usage.
Shows the absolute minimal code needed to create a plot.
"""

import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Quickstart Example")
    args = parser.parse_args()

    # Get some simple data
    data = ExampleData.simple_scatter()

    # Create a plot - that's it!
    fig, ax = drp.scatter(data, x="x", y="y", title="Quickstart Scatter Plot")

    # Always show/save the plot first for debugging purposes
    show_or_save_plot(fig, args, "01_quickstart")

    # Then verify legend visibility and fail if issues are found
    print("\n" + "=" * 60)
    print("LEGEND VISIBILITY VERIFICATION")
    print("=" * 60)

    verification_result = verify_legend_visibility(
        fig,
        expected_visible_count=0,  # We expect 0 legends (simple scatter with no grouping)
        fail_on_missing=False,  # Don't fail for missing legends since we expect 0
    )

    if verification_result["visible_legends"] > 0:
        print("\n💥 EXAMPLE 1 FAILED: Unexpected legends detected!")
        print("   - Expected 0 legends (simple scatter with no grouping variables)")
        print(f"   - Found {verification_result['visible_legends']} unexpected legends")

        print("\n📋 Detailed Issues:")
        for i, result in verification_result["details"].items():
            if result["visible"]:
                print(f"   • Subplot {i}: Unexpected legend detected")

        print(
            "\n🔧 This indicates the legend management system is creating legends when it shouldn't."
        )
        print("   Simple plots without grouping variables should not have legends.")
        print("   📊 Plot has been saved for visual debugging.")

        # Exit with error code to fail the example
        sys.exit(1)

    print("\n🎉 SUCCESS: No unexpected legends found - plot is clean as expected!")
