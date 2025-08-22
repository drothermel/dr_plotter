"""
Constants for dr_plotter, including special markers for multi-series plotting.
"""

from typing import List

from dr_plotter.types import (
    VisualChannel,
)

# Different methods of visual groupings
VISUAL_CHANNELS: List[VisualChannel] = ["hue", "style", "size", "marker", "alpha"]
DEFAULT_VISUAL_CHANNEL: VisualChannel = "hue"

# Column name constants for prepping data for patterned plot building
X_COL_NAME = "_x"
METRIC_COL_NAME = "_metric"
Y_COL_NAME = "_value"
