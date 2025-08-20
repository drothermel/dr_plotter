"""
Example 9: ML Experiment Visualization with Multi-Dimensional Encoding

This example shows how to visualize ML training results with multiple metrics,
learning rates, and weight decay values using the new multi-series API.
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter import consts
from dr_plotter.utils import setup_arg_parser, show_or_save_plot


def simulate_training_run(epochs, lr, wd):
    """Simulate training metrics for a given hyperparameter combination."""
    # Simulate decreasing loss with some noise
    base_loss = np.exp(-np.linspace(0, 2, epochs) * lr * 10)
    train_loss = base_loss * (1 + np.random.randn(epochs) * 0.1) * (1 + wd)
    val_loss = base_loss * (1 + np.random.randn(epochs) * 0.15) * (1 + wd * 1.2) + 0.05

    # Simulate increasing accuracy
    train_acc = 1 - base_loss * 0.8 + np.random.randn(epochs) * 0.02
    val_acc = 1 - base_loss * 0.85 + np.random.randn(epochs) * 0.03 - 0.05

    return train_loss, val_loss, train_acc, val_acc


if __name__ == "__main__":
    parser = setup_arg_parser(description="ML Experiment Visualization Example")
    args = parser.parse_args()

    # Simulate an ML experiment with different hyperparameters
    epochs = 50
    learning_rates = [0.001, 0.01, 0.1]
    weight_decays = [0.0, 0.001]

    # Generate synthetic experiment data
    data_records = []
    for lr in learning_rates:
        for wd in weight_decays:
            train_loss, val_loss, train_acc, val_acc = simulate_training_run(
                epochs, lr, wd
            )
            for epoch in range(epochs):
                data_records.append(
                    {
                        "epoch": epoch,
                        "learning_rate": lr,
                        "weight_decay": wd,
                        "train_loss": train_loss[epoch],
                        "val_loss": val_loss[epoch],
                        "train_accuracy": train_acc[epoch],
                        "val_accuracy": val_acc[epoch],
                    }
                )

    df = pd.DataFrame(data_records)

    # Create a figure with different visualization strategies
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(15, 12), constrained_layout=True)
    fig.suptitle(
        "ML Experiment: Multiple Metrics × Learning Rates × Weight Decay", fontsize=16
    )

    # --- Plot 1: Loss curves with metrics as color, LR as line style ---
    ax1 = axes[0, 0]
    drp.line(
        df,
        x="epoch",
        y=["train_loss", "val_loss"],
        hue=consts.METRICS,  # Different colors for train vs val
        style="learning_rate",  # Different line styles for LR
        ax=ax1,
        title="Loss by Metric Type and Learning Rate",
    )

    # --- Plot 2: Loss curves with LR as color, metrics as line style ---
    ax2 = axes[0, 1]
    drp.line(
        df,
        x="epoch",
        y=["train_loss", "val_loss"],
        hue="learning_rate",  # Different colors for LR
        style=consts.METRICS,  # Different line styles for train vs val
        ax=ax2,
        title="Loss by Learning Rate and Metric Type",
    )

    # --- Plot 3: Accuracy with all dimensions encoded ---
    ax3 = axes[1, 0]
    drp.line(
        df,
        x="epoch",
        y=["train_accuracy", "val_accuracy"],
        hue="learning_rate",  # Color for LR
        style="weight_decay",  # Line style for WD
        marker=consts.METRICS,  # Markers for train vs val
        ax=ax3,
        title="Accuracy (color=LR, style=WD, marker=metric)",
    )

    # --- Plot 4: Focus on validation loss only ---
    ax4 = axes[1, 1]
    drp.line(
        df,
        x="epoch",
        y="val_loss",
        hue="learning_rate",  # Color for LR
        style="weight_decay",  # Line style for WD
        ax=ax4,
        title="Validation Loss Only (color=LR, style=WD)",
    )

    show_or_save_plot(fig, args, "09_ml_experiment")
