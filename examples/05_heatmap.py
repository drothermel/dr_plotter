"""
Example 5: Heatmap

This script demonstrates how to create a heatmap, for example to show
a correlation matrix.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dr_plotter.api as drp

if __name__ == "__main__":
    # --- Create sample data ---
    # Create a sample DataFrame
    np.random.seed(0)
    data = pd.DataFrame(np.random.rand(10, 10),
                        columns=[f'Feature_{i}' for i in range(10)])
    # Compute the correlation matrix
    corr_matrix = data.corr()

    # --- Create a heatmap ---
    # Note the use of the matplotlib kwarg `cmap`
    drp.heatmap(corr_matrix, 
                title='Correlation Matrix Heatmap', 
                cmap='viridis')

    # --- Show plot with timeout ---
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(5)
    plt.close()
