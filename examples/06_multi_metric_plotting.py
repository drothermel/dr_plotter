"""
Example 6: Multi-Metric Plotting - METRICS constant.
Demonstrates plotting multiple y-columns with the METRICS constant.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from dr_plotter import consts
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="Multi-Metric Plotting Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Multi-Metrics: Using the METRICS Constant", fontsize=16)

        # ML training data with multiple metrics
        ml_data = ExampleData.ml_training_curves()

        # Basic multi-metrics: color by METRICS (filter to single learning rate for clarity)
        single_lr_data = ml_data[ml_data["learning_rate"] == 0.01].copy()
        fm.plot(
            "line",
            0,
            0,
            single_lr_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRICS,
            title="Loss Metrics (hue_by=METRICS)",
        )

        # Multi-metrics with additional grouping
        fm.plot(
            "line",
            0,
            1,
            ml_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRICS,
            style_by="learning_rate",
            title="Loss + Learning Rate",
        )

        # Accuracy metrics
        fm.plot(
            "line",
            1,
            0,
            ml_data,
            x="epoch",
            y=["train_accuracy", "val_accuracy"],
            hue_by="learning_rate",
            style_by=consts.METRICS,
            title="Accuracy (style_by=METRICS)",
        )

        # Generic multi-metric data
        multi_data = ExampleData.multi_metric_data()
        fm.plot(
            "line",
            1,
            1,
            multi_data,
            x="x",
            y=["metric_a", "metric_b", "metric_c"],
            hue_by=consts.METRICS,
            title="Generic Multi-Metrics",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "06_multi_metric_plotting")

        # Then verify legend visibility and fail if issues are found
        print("\n" + "=" * 60)
        print("LEGEND VISIBILITY VERIFICATION")
        print("=" * 60)

        verification_result = verify_legend_visibility(
            fm.fig,
            expected_visible_count=4,  # We expect 4 subplots to have visible legends
            fail_on_missing=True,
        )

        if not verification_result["success"]:
            print("\n💥 EXAMPLE 6 FAILED: Legend visibility issues detected!")
            print("   - Expected all 4 subplots to have visible legends")
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
                "   The multi-metric plotting should show legends for METRICS and grouping variables."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All legends are visible and properly positioned!")
