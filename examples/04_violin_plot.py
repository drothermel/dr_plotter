"""
Example 4: Violin Plot
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='Violin Plot Example')
    args = parser.parse_args()

    data = pd.DataFrame({
        'category': np.repeat(['Category A', 'Category B', 'Category C', 'Category D'], 25),
        'value_distribution': np.random.randn(100)
    })

    fig, _ = drp.violin(data, x='category', y='value_distribution', title='Violin Plot Example')

    show_or_save_plot(fig, args, '04_violin_plot')