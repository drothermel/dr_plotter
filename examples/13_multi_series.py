"""
Example 13: Multi-Series Plotting - Visual encoding channels.
Demonstrates all visual encoding options: hue, style, size, marker, alpha.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Multi-Series Plotting Example")
    args = parser.parse_args()

    with FigureManager(rows=2, cols=2, figsize=(15, 12)) as fm:
        fm.fig.suptitle("Multi-Series: All Visual Encoding Channels", fontsize=16)

        # Complex data with multiple grouping variables
        complex_data = ExampleData.complex_encoding_data()

        # Scatter: hue + marker encoding
        fm.scatter(
            0,
            0,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            marker_by="condition",
            title="Scatter: hue + marker",
        )

        # Scatter: hue + size encoding
        fm.scatter(
            0,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="condition",
            size_by="performance",
            title="Scatter: hue + size",
        )

        # Line plot with grouped time series
        grouped_ts = ExampleData.time_series_grouped(periods=30, groups=4)

        # Line: hue + style encoding
        fm.line(
            1,
            0,
            grouped_ts,
            x="time",
            y="value",
            hue_by="group",
            style_by="group",
            title="Line: hue + style",
        )

        # Scatter: alpha encoding for emphasis
        fm.scatter(
            1,
            1,
            complex_data,
            x="x",
            y="y",
            hue_by="experiment",
            alpha_by="algorithm",
            title="Scatter: hue + alpha",
        )

        show_or_save_plot(fm.fig, args, "13_multi_series")
