"""
Example 1: The High-Level API
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='High-Level API Example')
    args = parser.parse_args()

    data = pd.DataFrame({
        'x_values': np.arange(50),
        'y_values': np.random.randn(50).cumsum(),
        'categories': ['A', 'B', 'C', 'D', 'E'] * 10
    })

    # --- Scatter Plot ---
    fig1, _ = drp.scatter(data, x='x_values', y='y_values', title='Scatter Plot')
    show_or_save_plot(fig1, args, '01_scatter')

    # --- Line Plot ---
    fig2, _ = drp.line(data, x='x_values', y='y_values', title='Line Plot')
    show_or_save_plot(fig2, args, '01_line')

    # --- Bar Plot ---
    bar_data = data.groupby('categories')['y_values'].mean().reset_index()
    fig3, _ = drp.bar(bar_data, x='categories', y='y_values', title='Bar Plot')
    show_or_save_plot(fig3, args, '01_bar')

    # --- Histogram (Counts) ---
    fig4, _ = drp.hist(data, x='y_values', bins=10, title='Histogram (Counts)')
    show_or_save_plot(fig4, args, '01_histogram_counts')

    # --- Histogram (Density) ---
    fig5, _ = drp.hist(data, x='y_values', bins=10, title='Histogram (Density)', density=True)
    show_or_save_plot(fig5, args, '01_histogram_density')
