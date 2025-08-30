import argparse
import os

import matplotlib.pyplot as plt


def setup_arg_parser(description: str = "dr_plotter example script"):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--save-dir",
        type=str,
        default=None,
        help="Save the plot(s) to the specified directory instead of displaying them.",
    )
    parser.add_argument(
        "--pause", type=int, default=5, help="Duration in seconds to display the plot."
    )
    return parser


def show_or_save_plot(fig, args, filename: str):
    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
        savename = os.path.join(args.save_dir, f"{filename}.png")
        fig.savefig(savename, dpi=300)
        print(f"Plot saved to {savename}")
    else:
        plt.show(block=False)
        plt.pause(args.pause)

    plt.close(fig)


def create_and_render_plot(ax, plotter_class, plotter_args, **kwargs):
    plotter = plotter_class(*plotter_args, **kwargs)
    plotter.render(ax)
