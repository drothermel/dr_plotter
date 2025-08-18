"""
Utility functions for dr_plotter, especially for scripting and examples.
"""

import argparse
import matplotlib.pyplot as plt
import os

DR_PLOTTER_STYLE_KEYS = ['title', 'xlabel', 'ylabel', 'legend', 'display_values', 'xlabel_pos']

def setup_arg_parser(description: str = 'dr_plotter example script'):
    """
    Sets up a standard argument parser for example scripts.

    Args:
        description: The description for the argument parser.

    Returns:
        An argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--save-dir', type=str, default=None, 
                        help='Save the plot(s) to the specified directory instead of displaying them.')
    parser.add_argument('--pause', type=int, default=5, 
                        help='Duration in seconds to display the plot.')
    return parser

def show_or_save_plot(fig, args, filename: str):
    """
    Shows or saves a plot based on the provided arguments.

    Args:
        fig: The matplotlib Figure object to show or save.
        args: The parsed arguments from setup_arg_parser.
        filename: The base filename for the saved plot.
    """
    rect = [0, 0, 1, 1]
    if fig._suptitle is not None:
        rect = [0, 0, 1, 0.95]
    fig.tight_layout(rect=rect)

    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
        savename = os.path.join(args.save_dir, f"{filename}.png")
        fig.savefig(savename, dpi=300)
        print(f"Plot saved to {savename}")
    else:
        plt.show(block=False)
        plt.pause(args.pause)
    
    plt.close(fig)

def partition_kwargs(kwargs):
    """Partitions kwargs into dr_plotter specific and matplotlib specific."""
    dr_plotter_kwargs = {}
    matplotlib_kwargs = {}
    for key, value in kwargs.items():
        if key in DR_PLOTTER_STYLE_KEYS:
            dr_plotter_kwargs[key] = value
        else:
            matplotlib_kwargs[key] = value
    return dr_plotter_kwargs, matplotlib_kwargs
