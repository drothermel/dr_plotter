"""
Example 3: The Low-Level API (FigureManager)

This script introduces power-users to creating complex, multi-panel figures
using the FigureManager.

The plot will be displayed for 5 seconds.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dr_plotter.figure import FigureManager
from dr_plotter.plotters.line import LinePlotter
from dr_plotter.plotters.histogram import HistogramPlotter

if __name__ == "__main__":
    # --- Create sample data ---
    ts_data = pd.DataFrame({'x_axis_time': np.arange(100), 'y_axis_value': np.random.randn(100).cumsum()})
    dist_data = pd.DataFrame({'distribution': np.random.randn(1000)})

    # --- Use the FigureManager for a multi-panel layout ---
    fm = FigureManager(rows=1, cols=2, figsize=(12, 5))

    # --- Add a line plot to the first subplot ---
    # Note that the plotter automatically infers the axis labels from the column names.
    line_plotter = LinePlotter(ts_data, 'x_axis_time', 'y_axis_value', 
                               dr_plotter_kwargs={'title': 'Time Series'}, 
                               matplotlib_kwargs={})
    fm.add_plotter(line_plotter, row=0, col=0)

    # --- Add a histogram to the second subplot ---
    # Note the smart 'Frequency' ylabel and inferred xlabel.
    hist_plotter = HistogramPlotter(dist_data, 'distribution', 
                                    dr_plotter_kwargs={'title': 'Value Distribution'}, 
                                    matplotlib_kwargs={'bins': 20})
    fm.add_plotter(hist_plotter, row=0, col=1)

    # --- Show plot with timeout ---
    plt.suptitle("Example 3: FigureManager with Low-Level Plotters")
    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to make room for suptitle
    plt.show(block=False)
    plt.pause(5)
    plt.close()