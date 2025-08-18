"""
Example 8: Multi-Series Plots using FigureManager

This script demonstrates how to use the FigureManager to create a complex
figure with multiple, varied subplots.
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='Multi-Series Plot Example using FigureManager')
    args = parser.parse_args()

    # Use the FigureManager to set up the grid
    fm = FigureManager(rows=2, cols=2, figsize=(15, 12))
    fm.fig.suptitle('Multi-Series Plot Examples', fontsize=16)

    # --- 1. Multi-Line Plot ---
    # For plots with custom loop logic, get the axes and use the main API
    ax1 = fm.get_axes(row=0, col=0)
    line_data = pd.DataFrame({
        'time': list(range(10)) * 3,
        'value': np.random.randn(30).cumsum(),
        'category': np.repeat(['A', 'B', 'C'], 10)
    })
    colors = ['#E63946', '#457B9D', '#F1C40F']
    for i, category in enumerate(line_data['category'].unique()):
        subset = line_data[line_data['category'] == category]
        drp.line(subset, x='time', y='value', ax=ax1, label=category, color=colors[i], linewidth=2)
    # Final call to apply styling
    drp.line(pd.DataFrame(), x=None, y=None, ax=ax1, title='Multi-Line Plot', legend=True)

    # --- 2. Multi-Scatter Plot ---
    ax2 = fm.get_axes(row=0, col=1)
    scatter_data = pd.DataFrame({
        'x_coord': np.random.rand(90) * 10,
        'y_coord': np.random.rand(90) * 10,
        'category': np.repeat(['X', 'Y', 'Z'], 30)
    })
    markers = ['o', '^', 's']
    for i, category in enumerate(scatter_data['category'].unique()):
        subset = scatter_data[scatter_data['category'] == category]
        drp.scatter(subset, x='x_coord', y='y_coord', ax=ax2, label=category, marker=markers[i], s=50, alpha=0.7)
    drp.scatter(pd.DataFrame(), x=None, y=None, ax=ax2, title='Multi-Scatter Plot', legend=True)

    # --- 3. Multi-Bar Plot (Grouped) ---
    # For plots with a direct FigureManager method, call it directly
    bar_data = pd.DataFrame({
        'group': ['Group 1', 'Group 2', 'Group 3'] * 2,
        'category': np.repeat(['Category A', 'Category B'], 3),
        'value': np.random.rand(6) * 10 + 2
    })
    fm.grouped_bar(row=1, col=0, data=bar_data, x='group', y='value', hue='category', 
                   title='Grouped Bar Plot', legend=True)

    # --- 4. Grouped Violin Plot ---
    groups = ['Group 1', 'Group 2', 'Group 3']
    hues = ['Type A', 'Type B']
    data = []
    for group in groups:
        for hue in hues:
            values = np.random.normal(loc=groups.index(group) * 3 + hues.index(hue), scale=1, size=100)
            for value in values:
                data.append([group, hue, value])
    violin_data = pd.DataFrame(data, columns=['main_category', 'sub_category', 'value'])
    fm.violin(row=1, col=1, data=violin_data, x='main_category', y='value', hue='sub_category', 
              title='Grouped Violin Plot', legend=True)

    # --- Show or save the entire figure ---
    show_or_save_plot(fm.fig, args, '08_multi_series_manager')
