from typing import Any, Dict

PUBLICATION_COLORS = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]
BUMP_OPTIMIZED_PALETTE = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#96CEB4",
    "#FFEAA7",
    "#DDA0DD",
]

PLOT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "default": {
        "layout": (1, 1),
        "style": {"theme": "base"},
        "legend": {"style": "subplot"},
    },
    "dashboard": {
        "layout": {"rows": 2, "cols": 2, "figsize": (16, 12), "tight_layout_pad": 0.3},
        "legend": {"style": "grouped"},
    },
    "publication": {
        "layout": {"figsize": (12, 8), "tight_layout_pad": 0.8},
        "style": {
            "colors": PUBLICATION_COLORS,
            "fonts": {"size": 12},
            "figure_styles": {"dpi": 300},
        },
        "legend": {"style": "figure"},
    },
    "bump_plot": {
        "style": {
            "colors": BUMP_OPTIMIZED_PALETTE,
            "theme": "line",
            "plot_styles": {"linewidth": 3, "marker": "o"},
        },
        "legend": {"style": "grouped"},
    },
    "faceted_analysis": {
        "layout": {"rows": 3, "cols": 2, "figsize": (14, 16)},
        "legend": {"style": "figure"},
    },
}
