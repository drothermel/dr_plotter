"""
Example 2: Layering Plots with the new Theming system.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="Layering Plots Example")
    args = parser.parse_args()

    data1 = pd.DataFrame({"x": np.arange(20), "y": np.random.rand(20) * 10})
    data2 = pd.DataFrame({"x": np.arange(20), "y": np.random.rand(20) * 5 + 5})

    fig, ax = plt.subplots(constrained_layout=True)

    # The theme will automatically cycle colors and styles
    drp.scatter(data1, x="x", y="y", ax=ax, label="Raw Data")
    # User can still override any theme default
    drp.line(
        data2,
        x="x",
        y="y",
        ax=ax,
        label="Smoothed Data",
        color="#E63946",
        linewidth=3,
        title="Layered Scatter and Line Plot",
        xlabel="Time",
        ylabel="Value",
        legend=True,
    )

    show_or_save_plot(fig, args, "02_layered_plot")
