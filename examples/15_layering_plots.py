"""
Example 15: Layering Plots - Combining multiple plot types.
Demonstrates combining different plot types in the same subplot.
"""

import dr_plotter.api as drp
import matplotlib.pyplot as plt
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Layering Example")
    args = parser.parse_args()

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle("Layering: Combining Multiple Plot Types", fontsize=16)

    # === Left plot: Scatter + Line ===
    ax1 = axes[0]

    # Base scatter plot - test direct matplotlib parameter (alpha=0.6)
    scatter_data = ExampleData.simple_scatter()
    drp.scatter(scatter_data, x="x", y="y", ax=ax1, alpha=0.6, label="Data points")

    # Add trend line (simplified - just connect sorted points)
    sorted_data = scatter_data.sort_values("x")
    drp.line(
        sorted_data, x="x", y="y", ax=ax1, color="red", linewidth=2, label="Trend line"
    )

    ax1.set_title("Scatter + Trend Line")
    ax1.legend()

    # === Right plot: Histogram + Distribution overlay ===
    ax2 = axes[1]

    # Base histogram - test direct matplotlib parameter (alpha=0.7)
    dist_data = ExampleData.distribution_data()
    drp.hist(
        dist_data,
        x="values",
        ax=ax2,
        alpha=0.7,
        density=True,
        bins=30,
        label="Empirical distribution",
    )

    # Add theoretical normal curve
    import numpy as np

    x_theory = np.linspace(dist_data["values"].min(), dist_data["values"].max(), 100)
    y_theory = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x_theory**2)
    ax2.plot(x_theory, y_theory, "r-", linewidth=2, label="Standard normal")

    ax2.set_title("Histogram + Theoretical Curve")
    ax2.legend()

    # Always show/save the plot first for debugging purposes
    show_or_save_plot(fig, args, "15_layering_plots")

    # Then verify legend visibility and fail if issues are found
    print("\n" + "=" * 60)
    print("LEGEND VISIBILITY VERIFICATION")
    print("=" * 60)

    verification_result = verify_legend_visibility(
        fig,
        expected_visible_count=2,  # We expect 2 subplots to have visible legends
        fail_on_missing=True,
    )

    if not verification_result["success"]:
        print("\n💥 EXAMPLE 15 FAILED: Legend visibility issues detected!")
        print("   - Expected both subplots to have visible legends")
        print(
            f"   - Only {verification_result['visible_legends']} legends are actually visible"
        )
        print(f"   - {verification_result['missing_legends']} legends are missing")

        print("\n📋 Detailed Issues:")
        for issue in verification_result["issues"]:
            print(f"   • Subplot {issue['subplot']}: {issue['reason']}")
            print(
                f"     (exists: {issue['exists']}, marked_visible: {issue['marked_visible']}, has_content: {issue['has_content']})"
            )

        print("\n🔧 This indicates a bug in the legend management system.")
        print(
            "   The layering plots should show manual legends created with ax.legend() calls."
        )
        print("   Please check that manual legend calls are working properly.")
        print("   📊 Plot has been saved for visual debugging.")

        # Exit with error code to fail the example
        sys.exit(1)

    print("\n🎉 SUCCESS: All legends are visible and properly positioned!")
