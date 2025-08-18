"""
Example 2: Layering Plots

This script demonstrates how to use the `ax` parameter to layer multiple plots
on the same axes for comparison. It also shows how convenience styling is
applied on the last call.

The plot will be displayed for 5 seconds.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dr_plotter.api as drp

if __name__ == "__main__":
    # --- Create two datasets ---
    data1 = pd.DataFrame({'x': np.arange(20), 'y': np.random.rand(20) * 10})
    data2 = pd.DataFrame({'x': np.arange(20), 'y': np.random.rand(20) * 5 + 5})

    # --- Create a figure and axes ---
    fig, ax = plt.subplots()

    # --- Layer a scatter plot and a line plot ---
    # Note that matplotlib kwargs like `label` are passed through
    drp.scatter(data1, x='x', y='y', ax=ax, label='Raw Data')

    # The styling kwargs are applied on the final call to the axes
    drp.line(data2, x='x', y='y', ax=ax, label='Smoothed Data', color='red', linewidth=3,
             title='Layered Scatter and Line Plot',
             xlabel='Time',
             ylabel='Value',
             legend=True)

    # --- Show plot with timeout ---
    plt.show(block=False)
    plt.pause(5)
    plt.close()