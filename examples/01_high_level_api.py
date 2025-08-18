"""
Example 1: The High-Level API

This script demonstrates the simplicity of the high-level API for creating basic plots.
Each plot will be displayed for 30 seconds.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dr_plotter.api as drp


# --- Create Sample Data ---
def create_data():
    """Creates a sample DataFrame for plotting."""
    return pd.DataFrame(
        {
            "x_values": np.arange(50),
            "y_values": np.random.randn(50).cumsum(),
            "categories": ["A", "B", "C", "D", "E"] * 10,
        }
    )


def show_plot(title):
    """Helper function to show a plot with a title and timeout."""
    plt.suptitle(title)
    plt.show(block=False)
    plt.pause(30)
    plt.close()


if __name__ == "__main__":
    data = create_data()

    # --- Scatter Plot ---
    drp.scatter(data, x="x_values", y="y_values")
    show_plot("Example 1.1: Simple Scatter Plot")

    # --- Line Plot ---
    drp.line(data, x="x_values", y="y_values")
    show_plot("Example 1.2: Simple Line Plot")

    # --- Bar Plot ---
    bar_data = data.groupby("categories")["y_values"].mean().reset_index()
    drp.bar(bar_data, x="categories", y="y_values")
    show_plot("Example 1.3: Simple Bar Plot")

    # --- Histogram ---
    drp.hist(data, x="y_values", bins=10)
    show_plot("Example 1.4: Simple Histogram")
