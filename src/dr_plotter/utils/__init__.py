"""
Utility functions for dr_plotter.
"""

from .validation import validate_columns_exist, validate_numeric_columns
from .scripting import setup_arg_parser, show_or_save_plot, create_and_render_plot

__all__ = [
    "validate_columns_exist", 
    "validate_numeric_columns",
    "setup_arg_parser",
    "show_or_save_plot", 
    "create_and_render_plot"
]