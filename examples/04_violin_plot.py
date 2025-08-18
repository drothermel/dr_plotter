"""
Example 4: Violin Plot

This script demonstrates how to create a violin plot using the high-level API.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dr_plotter.api as drp

if __name__ == "__main__":
    # --- Create sample data ---
    data = pd.DataFrame({
        'category': np.repeat(['Category A', 'Category B', 'Category C', 'Category D'], 25),
        'value_distribution': np.random.randn(100)
    })

    # --- Create a violin plot ---
    # Note the automatically inferred labels for x and y axes.
    drp.violin(data, x='category', y='value_distribution', title='Violin Plot Example')

    # --- Show plot with timeout ---
    plt.show(block=False)
    plt.pause(5)
    plt.close()