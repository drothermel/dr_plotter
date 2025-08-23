"""
Example 2: High-Level API - All plotting functions.
Demonstrates each high-level plotting function with consistent data.
"""

from plot_data import ExampleData

import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
import sys


def verify_single_plot_no_legend(fig, plot_name):
    verification_result = verify_legend_visibility(
        fig,
        expected_visible_count=0,
        fail_on_missing=False,
    )
    if verification_result["visible_legends"] > 0:
        print(f"\n💥 {plot_name} FAILED: Unexpected legend detected!")
        print("   - Expected 0 legends (simple plot with no grouping)")
        print(f"   - Found {verification_result['visible_legends']} unexpected legends")
        return False
    return True


if __name__ == "__main__":
    parser = setup_arg_parser(description="High-Level API Example")
    args = parser.parse_args()

    failed_plots = []
    # === Bump Plot ===
    bump_data = ExampleData.ranking_data()
    fig7, _ = drp.bump_plot(
        bump_data,
        time_col="time",
        category_col="category",
        value_col="score",
        title="High-Level API: Bump Plot",
    )
    show_or_save_plot(fig7, args, "02_bump")

    # === Contour Plot ===
    contour_data = ExampleData.gaussian_mixture()
    fig8, _ = drp.gmm_level_set(
        contour_data, x="x", y="y", title="High-Level API: Contour"
    )
    show_or_save_plot(fig8, args, "02_contour")

    # === Heatmap ===
    heatmap_data = ExampleData.heatmap_data()
    fig6, _ = drp.heatmap(
        heatmap_data,
        x="column",
        y="row",
        values="value",
        title="High-Level API: Heatmap",
    )
    show_or_save_plot(fig6, args, "02_heatmap")

    # === Violin Plot ===
    violin_data = ExampleData.categorical_data()
    fig5, _ = drp.violin(
        violin_data, x="category", y="value", title="High-Level API: Violin"
    )
    show_or_save_plot(fig5, args, "02_violin")

    # === Histogram ===
    hist_data = ExampleData.distribution_data()
    fig4, _ = drp.hist(hist_data, x="values", title="High-Level API: Histogram")
    show_or_save_plot(fig4, args, "02_histogram")

    # === Scatter Plot ===
    scatter_data = ExampleData.simple_scatter()
    fig1, _ = drp.scatter(
        scatter_data,
        x="x",
        y="y",
        title="High-Level API: Scatter",
        s=10,
    )
    show_or_save_plot(fig1, args, "02_scatter")

    # === Line Plot ===
    line_data = ExampleData.time_series()
    fig2, _ = drp.line(line_data, x="time", y="value", title="High-Level API: Line")
    show_or_save_plot(fig2, args, "02_line")

    # === Bar Plot ===
    bar_data = ExampleData.categorical_data()
    bar_summary = bar_data.groupby("category")["value"].mean().reset_index()
    fig3, _ = drp.bar(bar_summary, x="category", y="value", title="High-Level API: Bar")
    show_or_save_plot(fig3, args, "02_bar")

    # Verify all plots have no legends (since they are simple plots with no grouping)
    print("\n" + "=" * 60)
    print("LEGEND VISIBILITY VERIFICATION")
    print("=" * 60)

    plots_to_verify = [
        (fig1, "Scatter Plot"),
        (fig2, "Line Plot"),
        (fig3, "Bar Plot"),
        (fig4, "Histogram"),
        (fig5, "Violin Plot"),
        (fig6, "Heatmap"),
        (fig7, "Bump Plot"),
        (fig8, "Contour Plot"),
    ]

    failed_plots = []
    for fig, plot_name in plots_to_verify:
        if not verify_single_plot_no_legend(fig, plot_name):
            failed_plots.append(plot_name)

    if failed_plots:
        print(
            f"\n💥 EXAMPLE 2 FAILED: {len(failed_plots)} plots had unexpected legends!"
        )
        print(
            "   - All plots in this example should have 0 legends (simple plots with no grouping)"
        )
        print(f"   - Failed plots: {', '.join(failed_plots)}")
        print(
            "\n🔧 This indicates the legend management system is creating legends when it shouldn't."
        )
        print("   Simple plots without grouping variables should not have legends.")
        print("   📊 Plots have been saved for visual debugging.")

        sys.exit(1)

    print(
        f"\n🎉 SUCCESS: All {len(plots_to_verify)} plots are clean with no unexpected legends!"
    )
