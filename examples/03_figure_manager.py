"""
Example 3: The Low-Level API (FigureManager)
"""

import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.plotters.line import LinePlotter
from dr_plotter.plotters.histogram import HistogramPlotter
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description='FigureManager Example')
    args = parser.parse_args()

    ts_data = pd.DataFrame({'x_axis_time': np.arange(100), 'y_axis_value': np.random.randn(100).cumsum()})
    dist_data = pd.DataFrame({'distribution': np.random.randn(1000)})

    fm = FigureManager(rows=1, cols=2, figsize=(12, 5))
    fm.fig.suptitle("Example 3: FigureManager with Low-Level Plotters")

    line_plotter = LinePlotter(ts_data, 'x_axis_time', 'y_axis_value', 
                               dr_plotter_kwargs={'title': 'Time Series'}, 
                               matplotlib_kwargs={})
    fm.add_plotter(line_plotter, row=0, col=0)

    hist_plotter = HistogramPlotter(dist_data, 'distribution', 
                                    dr_plotter_kwargs={'title': 'Value Distribution'}, 
                                    matplotlib_kwargs={'bins': 20})
    fm.add_plotter(hist_plotter, row=0, col=1)

    show_or_save_plot(fm.fig, args, '03_figure_manager')