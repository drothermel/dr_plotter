"""
Constants for dr_plotter, including special markers for multi-series plotting.
"""

from typing import Dict, List

from dr_plotter.types import (
    StyleAttrName,
    VisualChannel,
)

# Different methods of visual groupings
VISUAL_CHANNELS: List[VisualChannel] = ["hue", "style", "size", "marker", "alpha"]
DEFAULT_VISUAL_CHANNEL: VisualChannel = "hue"

# Mapping from visual channels to their corresponding style attribute names
CHANNEL_TO_ATTR: Dict[VisualChannel, StyleAttrName] = {
    "hue": "color",
    "style": "linestyle",
    "marker": "marker",
    "size": "size_mult",
    "alpha": "alpha",
}


# Helper function for theme cycle key convention
def get_cycle_key(channel: VisualChannel) -> str:
    """Get the theme key for a visual channel's cycle."""
    return f"{channel}_cycle"


# Column name constants for prepping data for patterned plot building
X_COL_NAME = "_x"
METRIC_COL_NAME = "_metric"
Y_COL_NAME = "_value"
