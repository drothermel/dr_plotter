"""
Example 17: ML Experiment Dashboard - Real-world use case.
Complete ML experiment visualization with multiple metrics and hyperparameters.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter import consts
from plot_data import ExampleData

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
        fm.line(
            0,
            0,
            ml_data,
            x="epoch",
            y=["train_loss", "val_loss"],
            hue_by=consts.METRICS,
            style_by="learning_rate",
            title="Loss Curves (color=metric, style=lr)",
        )

        # Learning rate comparison for validation loss
        fm.line(
            0,
            1,
            ml_data,
            x="epoch",
            y="val_loss",
            hue_by="learning_rate",
            title="Validation Loss by Learning Rate",
        )

        # Accuracy progression
        fm.line(
            1,
            0,
            ml_data,
            x="epoch",
            y=["train_accuracy", "val_accuracy"],
            hue_by="learning_rate",
            style_by=consts.METRICS,
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

        fm.bar(
            1,
            1,
            perf_df,
            x="learning_rate",
            y="value",
            hue_by="metric",
            title="Final Performance Summary",
        )

        show_or_save_plot(fm.fig, args, "17_ml_experiment")
