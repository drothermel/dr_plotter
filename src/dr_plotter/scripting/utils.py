import argparse
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def setup_arg_parser(
    description: str = "dr_plotter example script",
) -> argparse.ArgumentParser:
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


def show_or_save_plot(fig: Any, args: Any, filename: str) -> None:
    if args.save_dir:
        save_dir = Path(args.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        savename = save_dir / f"{filename}.png"
        fig.savefig(savename, dpi=300)
        print(f"Plot saved to {savename}")
    else:
        plt.show(block=False)
        plt.pause(args.pause)

    plt.close(fig)


def create_and_render_plot(
    ax: Any, plotter_class: Any, plotter_args: Any, **kwargs: Any
) -> None:
    plotter = plotter_class(*plotter_args, **kwargs)
    plotter.render(ax)


def parse_key_value_args(args: list[str] | None) -> dict[str, Any]:
    """Parse key=value arguments into dict.
    
    Handles comma-separated values and automatic type conversion to numbers.
    
    Examples:
        parse_key_value_args(["seed=0", "data=C4,Dolma1.7"]) 
        # Returns: {"seed": 0, "data": ["C4", "Dolma1.7"]}
        
        parse_key_value_args(["params=7B,30B,70B"])
        # Returns: {"params": ["7B", "30B", "70B"]}
    """
    result = {}
    if not args:
        return result

    for arg in args:
        if "=" not in arg:
            raise ValueError(f"Invalid format: {arg}. Use key=value")

        key, value = arg.split("=", 1)
        key = key.strip()

        # Handle comma-separated values
        if "," in value:
            values = [v.strip() for v in value.split(",")]
            # Try to convert to numbers if possible
            converted_values = []
            for v in values:
                try:
                    # Try integer first
                    if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                        converted_values.append(int(v))
                    else:
                        # Try float
                        converted_values.append(float(v))
                except ValueError:
                    # Keep as string
                    converted_values.append(v)
            result[key] = converted_values
        else:
            # Try to convert single value to number if possible
            value = value.strip()
            try:
                if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                    result[key] = int(value)
                else:
                    result[key] = float(value)
            except ValueError:
                result[key] = value

    return result
