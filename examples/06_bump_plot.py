"""
Example 6: Bump Plot
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='Bump Plot Example')
    args = parser.parse_args()

    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    data = []
    for quarter in quarters:
        for product in products:
            sales = 1000 + np.random.randint(-100, 100) * (products.index(product) + 1)
            data.append([quarter, product, sales])
    sales_df = pd.DataFrame(data, columns=['quarter', 'product', 'sales'])

    fig, _ = drp.bump_plot(sales_df, 
                         time_col='quarter', 
                         category_col='product', 
                         value_col='sales', 
                         title='Product Sales Rankings Per Quarter', 
                         linewidth=3)

    show_or_save_plot(fig, args, '06_bump_plot')
