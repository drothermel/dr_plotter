"""
Example 6: Line Plot Showcase - All line plot features.
Demonstrates all visual encoding options for line plots including multi-series.
"""

import dr_plotter.api as drp
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from dr_plotter import consts
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Line Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Line Plot Showcase: All Visual Encoding Options", fontsize=16)

        # Basic line
        basic_data = ExampleData.time_series()
        fm.line(0, 0, basic_data, x="time", y="value", title="Basic Line Plot")

        # Multiple lines with hue
        grouped_data = ExampleData.time_series_grouped()
        fm.line(0, 1, grouped_data, x="time", y="value", hue_by="group", 
               title="Multi-Series (hue)")

        # Line style encoding
        fm.line(1, 0, grouped_data, x="time", y="value", hue_by="group", 
               style_by="group", title="Color + Line Style")

        # Multi-metrics with METRICS encoding
        ml_data = ExampleData.ml_training_curves(epochs=30)
        fm.line(1, 1, ml_data, x="epoch", y=["train_loss", "val_loss"], 
               hue_by=consts.METRICS, style_by="learning_rate", 
               title="Multi-Metrics (METRICS)")

        show_or_save_plot(fm.fig, args, "06_line_showcase")