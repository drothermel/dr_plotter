"""
Example 18: Scientific Figures - Publication-ready plots.
Demonstrates creating publication-quality figures with proper styling.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Scientific Figures Example")
    args = parser.parse_args()

    # Create publication-style figure
    with FigureManager(rows=2, cols=3, figsize=(18, 12)) as fm:
        fm.fig.suptitle(
            "Scientific Data Analysis: Multi-Panel Figure", fontsize=16, y=0.95
        )

        # Panel A: Time series data
        ts_data = ExampleData.time_series_grouped(periods=50, groups=3)
        fm.plot(
            "line",
            0,
            0,
            ts_data,
            x="time",
            y="value",
            hue_by="group",
            title="A) Temporal Dynamics",
            xlabel="Time (hours)",
            ylabel="Signal Intensity",
        )

        # Panel B: Distribution comparison
        dist_data = ExampleData.distribution_data(distributions=3)
        fm.plot(
            "violin",
            0,
            1,
            dist_data,
            x="distribution",
            y="value",
            title="B) Response Distributions",
            xlabel="Treatment Group",
            ylabel="Response",
        )

        # Panel C: Correlation analysis
        corr_data = ExampleData.simple_scatter(n=200)
        fm.plot(
            "scatter",
            0,
            2,
            corr_data,
            x="x",
            y="y",
            title="C) Variable Correlation",
            xlabel="Predictor X",
            ylabel="Response Y",
        )

        # Panel D: Categorical analysis
        cat_data = ExampleData.grouped_categories()
        cat_summary = (
            cat_data.groupby(["category", "group"])["value"].mean().reset_index()
        )
        fm.plot(
            "bar",
            1,
            0,
            cat_summary,
            x="category",
            y="value",
            hue_by="group",
            title="D) Treatment Effects",
            xlabel="Condition",
            ylabel="Mean Response",
        )

        # Panel E: Heatmap of relationships
        heatmap_data = ExampleData.heatmap_data(rows=6, cols=6)
        fm.plot(
            "heatmap",
            1,
            1,
            heatmap_data,
            x="column",
            y="row",
            values="value",
            title="E) Correlation Matrix",
            cmap="RdBu_r",
        )

        # Panel F: Ranking over time
        ranking_data = ExampleData.ranking_data(time_points=10, categories=4)
        fm.plot(
            "bump",
            1,
            2,
            ranking_data,
            time_col="time",
            category_col="category",
            value_col="score",
            title="F) Performance Rankings",
        )

        # Adjust layout for better appearance
        # Skip tight_layout due to colorbar compatibility issue
        fm.fig.subplots_adjust(
            top=0.92, bottom=0.08, left=0.08, right=0.95, hspace=0.3, wspace=0.3
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "18_scientific_figures")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=2,  # We expect 2/6 subplots to have visible legends (Panel A: line with hue_by, Panel D: bar with hue_by)
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 18 FAILED: Legend visibility issues detected!")
            print("   - Expected 2 subplots to have visible legends")
            print("   - Panel A (line plot) should have a legend (hue_by grouping)")
            print("   - Panel D (grouped bar) should have a legend (hue_by grouping)")
            print(
                "   - Panels B, C, E, F should NOT have legends (no grouping or heatmap/bump)"
            )
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
                "   The scientific figures should show legends only for panels with grouping variables."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All expected legends are visible and properly positioned!")
