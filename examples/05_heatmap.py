"""
Example 5: Heatmap
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='Heatmap Example')
    args = parser.parse_args()

    np.random.seed(0)
    data = pd.DataFrame(np.random.rand(8, 8),
                        columns=[f'Feature_{i}' for i in range(8)],
                        index=[f'Sample_{i}' for i in range(8)])
    corr_matrix = data.corr()

    # --- Heatmap with default options (values on, labels top) ---
    fig1, _ = drp.heatmap(corr_matrix, 
                          title='Correlation Matrix (Labels on Top)', 
                          cmap='plasma')
    show_or_save_plot(fig1, args, '05_heatmap_default')

    # --- Heatmap with values off and labels bottom ---
    fig2, _ = drp.heatmap(corr_matrix, 
                          title='Correlation Matrix (Labels on Bottom)', 
                          cmap='plasma',
                          display_values=False,
                          xlabel_pos='bottom')
    show_or_save_plot(fig2, args, '05_heatmap_custom')