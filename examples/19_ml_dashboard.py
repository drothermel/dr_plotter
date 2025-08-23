"""
Example 19: ML Dashboard Dashboard - Real-world use case.
Complete ML experiment visualization with multiple metrics and hyperparameters.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.verification import verify_legend_visibility
from dr_plotter import consts
from plot_data import ExampleData
import sys

if __name__ == "__main__":
    parser = setup_arg_parser(description="ML Experiment Dashboard")
    args = parser.parse_args()

    # Generate comprehensive ML experiment data
    ml_data = ExampleData.ml_training_curves(
        epochs=100, learning_rates=[0.001, 0.01, 0.1]
    )

    with FigureManager(rows=2, cols=2, figsize=(16, 12)) as fm:
        fm.fig.suptitle("ML Experiment Dashboard: Training Analysis", fontsize=16)

        # Loss curves by metric type
        fm.plot(
            "line",
            0,
            0,
            ml_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRIC_COL_NAME,
            style_by="learning_rate",
            title="Loss Curves (color=metric, style=lr)",
        )

        # Learning rate comparison for validation loss
        fm.plot(
            "line",
            0,
            1,
            ml_data,
            x="epoch",
            y="val_loss",
            hue_by="learning_rate",
            title="Validation Loss by Learning Rate",
        )

        # Accuracy progression
        fm.plot(
            "line",
            1,
            0,
            ml_data,
            x="epoch",
            y=["train_accuracy", "val_accuracy"],
            hue_by="learning_rate",
            style_by=consts.METRIC_COL_NAME,
            title="Accuracy (color=lr, style=metric)",
        )

        # Final performance comparison (last epoch only)
        final_epoch = ml_data[ml_data["epoch"] == ml_data["epoch"].max()]
        performance_data = []

        for _, row in final_epoch.iterrows():
            performance_data.extend(
                [
                    {
                        "learning_rate": row["learning_rate"],
                        "metric": "train_loss",
                        "value": row["train_loss"],
                    },
                    {
                        "learning_rate": row["learning_rate"],
                        "metric": "val_loss",
                        "value": row["val_loss"],
                    },
                    {
                        "learning_rate": row["learning_rate"],
                        "metric": "train_accuracy",
                        "value": row["train_accuracy"],
                    },
                    {
                        "learning_rate": row["learning_rate"],
                        "metric": "val_accuracy",
                        "value": row["val_accuracy"],
                    },
                ]
            )

        import pandas as pd

        perf_df = pd.DataFrame(performance_data)

        fm.plot(
            "bar",
            1,
            1,
            perf_df,
            x="learning_rate",
            y="value",
            hue_by="metric",
            title="Final Performance Summary",
        )

        # Always show/save the plot first for debugging purposes
        show_or_save_plot(fm.fig, args, "19_ml_dashboard")

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
            print("\n💥 EXAMPLE 19 FAILED: Legend visibility issues detected!")
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
                "   The ML dashboard should show legends for all metrics and learning rate groupings."
            )
            print("   Please check the legend manager implementation.")
            print("   📊 Plot has been saved for visual debugging.")

            # Exit with error code to fail the example
            sys.exit(1)

        print("\n🎉 SUCCESS: All legends are visible and properly positioned!")
