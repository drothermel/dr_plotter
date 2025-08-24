"""
This file makes the plotters package a Python package and exposes the plotters.

All plotters are automatically registered when imported via the BasePlotter
registry mechanism using __init_subclass__.
"""

# Import BasePlotter first to set up the registry
from .base import BasePlotter

# Import all concrete plotters - this triggers their registration
from .scatter import ScatterPlotter

from .line import LinePlotter
from .bar import BarPlotter
from .histogram import HistogramPlotter
from .violin import ViolinPlotter
from .heatmap import HeatmapPlotter

# from .bump import BumpPlotter  # BROKEN: needs migration to legend manager
from .contour import ContourPlotter

__all__ = [
    "BasePlotter",  # Expose for registry access
    "ScatterPlotter",
    "LinePlotter",
    "BarPlotter",
    "HistogramPlotter",
    "ViolinPlotter",
    "HeatmapPlotter",
    # "BumpPlotter",  # BROKEN: needs migration
    "ContourPlotter",
]
