"""
Example 3: The Low-Level API (FigureManager)

This script introduces power-users to creating complex, multi-panel figures
using the FigureManager.

The plot will be displayed for 30 seconds.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dr_plotter.figure import FigureManager
from dr_plotter.plotters.line import LinePlotter
from dr_plotter.plotters.histogram import HistogramPlotter

if __name__ == "__main__":
    # --- Create sample data ---
    ts_data = pd.DataFrame({'x': np.arange(100), 'y': np.random.randn(100).cumsum()})
    dist_data = pd.DataFrame({'z': np.random.randn(1000)})

    # --- Use the FigureManager for a multi-panel layout ---
    # Note: We don't use the context manager here because we need to control the show() call
    fm = FigureManager(rows=1, cols=2, figsize=(12, 5))

    # --- Add a line plot to the first subplot ---
    ax1 = fm.get_axes(row=0, col=0)
    line_plotter = LinePlotter(ts_data, x='x', y='y')
    line_plotter.render(ax1)
    ax1.set_title('Time Series')

    # --- Add a histogram to the second subplot ---
    ax2 = fm.get_axes(row=0, col=1)
    hist_plotter = HistogramPlotter(dist_data, x='z', bins=20)
    hist_plotter.render(ax2)
    ax2.set_title('Value Distribution')

    # --- Show plot with timeout ---
    plt.suptitle("Example 3: FigureManager with Low-Level Plotters")
    plt.show(block=False)
    plt.pause(30)
    plt.close()
