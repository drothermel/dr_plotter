"""
Example 4: Violin Plot

This script demonstrates how to create a violin plot.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dr_plotter.api as drp

if __name__ == "__main__":
    # --- Create sample data ---
    data = pd.DataFrame({
        'category': np.repeat(['A', 'B', 'C', 'D'], 25),
        'value': np.random.randn(100)
    })

    # --- Create a violin plot ---
    drp.violin(data, x='category', y='value')

    # --- Show plot with timeout ---
    plt.suptitle("Example 4: Violin Plot")
    plt.show(block=False)
    plt.pause(30)
    plt.close()
