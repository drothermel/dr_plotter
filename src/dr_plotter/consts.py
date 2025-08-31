from typing import Dict, List

from dr_plotter.types import (
    StyleAttrName,
    VisualChannel,
)

VISUAL_CHANNELS: List[VisualChannel] = ["hue", "style", "size", "marker", "alpha"]

CHANNEL_TO_ATTR: Dict[VisualChannel, StyleAttrName] = {
    "hue": "color",
    "style": "linestyle",
    "marker": "marker",
    "size": "size_mult",
    "alpha": "alpha",
}


def get_cycle_key(channel: VisualChannel) -> str:
    return f"{channel}_cycle"


X_COL_NAME = "_x"
METRIC_COL_NAME = "_metric"
Y_COL_NAME = "_value"
