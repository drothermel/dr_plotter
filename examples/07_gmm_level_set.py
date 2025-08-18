"""
Example 7: GMM Level Set Plot
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='GMM Level Set Plot Example')
    args = parser.parse_args()

    np.random.seed(0)
    c1 = np.random.randn(100, 2) + [0, 0]
    c2 = np.random.randn(100, 2) * 0.5 + [3, 3]
    c3 = np.random.randn(100, 2) * 0.7 + [0, 4]
    data = pd.DataFrame(np.vstack([c1, c2, c3]), columns=['x_coord', 'y_coord'])

    fig, _ = drp.gmm_level_set(data, x='x_coord', y='y_coord', 
                               title='GMM Level Set Plot', 
                               cmap='viridis')

    show_or_save_plot(fig, args, '07_gmm_level_set')
