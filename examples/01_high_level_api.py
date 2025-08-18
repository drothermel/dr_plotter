"""
Example 1: The High-Level API using the new Theming system.
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="High-Level API Example")
    args = parser.parse_args()

    data = pd.DataFrame(
        {
            "x_values": np.arange(50),
            "y_values": np.random.randn(50).cumsum(),
            "categories": ["A", "B", "C", "D", "E"] * 10,
        }
    )

    # --- Plots will now use the default theme automatically ---
    fig1, _ = drp.scatter(data, x="x_values", y="y_values", title="Themed Scatter Plot")
    show_or_save_plot(fig1, args, "01_scatter")

    fig2, _ = drp.line(data, x="x_values", y="y_values", title="Themed Line Plot")
    show_or_save_plot(fig2, args, "01_line")

    bar_data = data.groupby("categories")["y_values"].mean().reset_index()
    fig3, _ = drp.bar(bar_data, x="categories", y="y_values", title="Themed Bar Plot")
    show_or_save_plot(fig3, args, "01_bar")

    fig4, _ = drp.hist(data, x="y_values", bins=10, title="Themed Histogram (Counts)")
    show_or_save_plot(fig4, args, "01_histogram_counts")

    fig5, _ = drp.hist(
        data, x="y_values", bins=10, title="Themed Histogram (Density)", density=True
    )
    show_or_save_plot(fig5, args, "01_histogram_density")
