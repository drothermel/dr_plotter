"""
Example 8: Multi-Series Plots with the new simplified API.
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.figure import FigureManager
from dr_plotter import consts
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="Multi-Series Plot Example using New API")
    args = parser.parse_args()

    fm = FigureManager(rows=2, cols=2, figsize=(15, 12))
    fm.fig.suptitle("Multi-Series Plot Examples with Simplified API", fontsize=16)

    # --- 1. Multi-Line Plot with hue grouping ---
    ax1 = fm.get_axes(row=0, col=0)
    line_data = pd.DataFrame(
        {
            "time": list(range(10)) * 3,
            "value": np.random.randn(30).cumsum(),
            "category": np.repeat(["A", "B", "C"], 10),
        }
    )
    drp.line(
        line_data,
        x="time",
        y="value",
        hue="category",
        ax=ax1,
        title="Multi-Line Plot (hue=category)",
    )

    # --- 2. Multi-Scatter Plot with redundant encoding ---
    ax2 = fm.get_axes(row=0, col=1)
    scatter_data = pd.DataFrame(
        {
            "x_coord": np.random.rand(90) * 10,
            "y_coord": np.random.rand(90) * 10,
            "category": np.repeat(["X", "Y", "Z"], 30),
        }
    )
    drp.scatter(
        scatter_data,
        x="x_coord",
        y="y_coord",
        hue="category",      # Color by category
        marker="category",   # AND marker by category (redundant encoding)
        ax=ax2,
        title="Multi-Scatter Plot (hue+marker=category)",
    )

    # --- 3. Multi-Metric Line Plot ---
    # Create data with multiple metrics and groupings
    multi_metric_data = pd.DataFrame(
        {
            "epoch": list(range(20)) * 2,
            "learning_rate": [0.001] * 20 + [0.01] * 20,
            "train_loss": np.random.rand(40) * np.exp(-np.linspace(0, 2, 40)),
            "val_loss": np.random.rand(40) * np.exp(-np.linspace(0, 1.5, 40)) + 0.1,
        }
    )

    ax3 = fm.get_axes(row=1, col=0)
    # Plot multiple metrics with automatic METRICS encoding
    drp.line(
        multi_metric_data,
        x="epoch",
        y=["train_loss", "val_loss"],
        hue=consts.METRICS,  # Metrics get different colors
        style="learning_rate",  # LR gets different line styles
        ax=ax3,
        title="Multi-Metric Plot (hue=METRICS, style=lr)",
    )

    # --- 4. Complex encoding example ---
    ax4 = fm.get_axes(row=1, col=1)

    # Create a more complex dataset
    complex_data = pd.DataFrame(
        {
            "x": np.random.rand(120) * 10,
            "y": np.random.rand(120) * 10,
            "experiment": np.repeat(["Exp1", "Exp2", "Exp3"], 40),
            "condition": np.tile(np.repeat(["Control", "Treatment"], 20), 3),
        }
    )

    # Use multiple visual channels
    drp.scatter(
        complex_data,
        x="x",
        y="y",
        hue="experiment",  # Color by experiment
        marker="condition",  # Marker by condition
        ax=ax4,
        title="Complex Encoding (hue=exp, marker=cond)",
    )

    show_or_save_plot(fm.fig, args, "08_multi_series_new_api")
