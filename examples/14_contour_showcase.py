"""
Example 14: Contour Plot Showcase - All contour plot features.
Demonstrates Gaussian Mixture Model level set visualizations.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Contour Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Contour Plot Showcase: Density Visualization", fontsize=16)

        # Basic contour plot
        mixture_data = ExampleData.gaussian_mixture(n_components=2)
        fm.plot("contour", 0, 0, mixture_data, x="x", y="y", title="2-Component GMM")

        # More complex mixture
        complex_mixture = ExampleData.gaussian_mixture(n_components=3)
        fm.plot("contour", 0, 1, complex_mixture, x="x", y="y", title="3-Component GMM")

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "14_contour_showcase")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=0,  # We expect 0 legends (contour plots don't use discrete legends)
            fail_on_missing=False,  # Don't fail for missing legends since we expect 0
        )

        if verification_result["visible_legends"] > 0:
            print("\n💥 EXAMPLE 14 FAILED: Unexpected legends detected!")
            print("   - Expected 0 legends (contour plots don't use discrete legends)")
            print(
                f"   - Found {verification_result['visible_legends']} unexpected legends"
            )

            print("\n📋 Detailed Issues:")
            for i, result in verification_result["details"].items():
                if result["visible"]:
                    print(f"   • Subplot {i}: Unexpected legend detected")

            print(
                "\n🔧 This indicates the legend management system is creating legends when it shouldn't."
            )
            print("   Contour plots should show density levels, not discrete legends.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print(
            "\n🎉 SUCCESS: No unexpected legends found - contour plots are clean as expected!"
        )
