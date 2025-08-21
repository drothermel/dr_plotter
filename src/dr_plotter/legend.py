"""
Legend abstraction for handling custom legend entries in plotters.
"""

from matplotlib.patches import Patch
from matplotlib.lines import Line2D


class Legend:
    """
    A builder class for creating legend entries.
    
    This class encapsulates the creation of legend handles, allowing plotters
    to add custom legend entries without needing to return values or manipulate
    the axes object directly.
    """
    
    def __init__(self):
        """Initialize an empty legend builder."""
        self.handles = []
    
    def add_patch(self, label, **kwargs):
        """
        Add a patch (colored rectangle) to the legend.
        
        Args:
            label: The label for this legend entry
            **kwargs: Additional arguments passed to matplotlib.patches.Patch
                     (e.g., facecolor, edgecolor, alpha)
        """
        self.handles.append(Patch(label=label, **kwargs))
    
    def add_line(self, label, **kwargs):
        """
        Add a line to the legend.
        
        Args:
            label: The label for this legend entry
            **kwargs: Additional arguments passed to matplotlib.lines.Line2D
                     (e.g., color, linestyle, linewidth, marker)
        """
        # Set defaults for Line2D that make sense for legend
        if 'xdata' not in kwargs:
            kwargs['xdata'] = []
        if 'ydata' not in kwargs:
            kwargs['ydata'] = []
        self.handles.append(Line2D(label=label, **kwargs))
    
    def get_handles(self):
        """
        Get all legend handles that have been added.
        
        Returns:
            List of matplotlib artists (Patch, Line2D, etc.) for the legend
        """
        return self.handles
    
    def has_entries(self):
        """
        Check if any legend entries have been added.
        
        Returns:
            True if there are legend entries, False otherwise
        """
        return len(self.handles) > 0