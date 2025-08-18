"""
Example 3: The Low-Level API (FigureManager) with the new Theming system.
"""

import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="FigureManager Example")
    args = parser.parse_args()

    ts_data = pd.DataFrame(
        {"x_axis_time": np.arange(100), "y_axis_value": np.random.randn(100).cumsum()}
    )
    dist_data = pd.DataFrame({"distribution": np.random.randn(1000)})

    fm = FigureManager(rows=1, cols=2, figsize=(12, 5))
    fm.fig.suptitle("Example 3: FigureManager with Themed Plots")

    # The plot will use the LINE_THEME by default
    fm.line(
        row=0,
        col=0,
        data=ts_data,
        x="x_axis_time",
        y="y_axis_value",
        title="Time Series",
    )

    # The plot will use the HISTOGRAM_THEME by default
    fm.hist(
        row=0,
        col=1,
        data=dist_data,
        x="distribution",
        title="Value Distribution",
        bins=20,
    )

    show_or_save_plot(fm.fig, args, "03_figure_manager")
