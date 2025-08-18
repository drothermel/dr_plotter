"""
Utility functions for dr_plotter, especially for scripting and examples.
"""

import argparse
import matplotlib.pyplot as plt

def setup_arg_parser(description: str = 'dr_plotter example script'):
    """
    Sets up a standard argument parser for example scripts.

    Args:
        description: The description for the argument parser.

    Returns:
        An argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--save-prefix', type=str, default=None, 
                        help='Save the plot(s) to files with this prefix instead of displaying them.')
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
    # Use a more robust layout algorithm
    rect = [0, 0, 1, 1]
    if fig._suptitle is not None:
        rect = [0, 0, 1, 0.95] # Leave space for the suptitle
    fig.tight_layout(rect=rect)

    if args.save_prefix:
        savename = f"{args.save_prefix}_{filename}.png"
        fig.savefig(savename, dpi=300) # Save with higher resolution
        print(f"Plot saved to {savename}")
    else:
        plt.show(block=False)
        plt.pause(args.pause)
    
    plt.close(fig)