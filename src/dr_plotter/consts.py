"""
Constants for dr_plotter, including special markers for multi-series plotting.
"""


class _MetricsMarker:
    """Sentinel class for the METRICS constant."""

    def __repr__(self):
        return "METRICS"

    def __str__(self):
        return "_metrics"


# Special constant to indicate that a visual attribute should vary by metric
METRICS = _MetricsMarker()

# String fallback for interactive use
METRICS_STR = "_metrics"
