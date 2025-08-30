"""
Example 15: Layering Plots - Combining multiple plot types.
Demonstrates combining different plot types in the same subplot.
"""

import dr_plotter.api as drp
import matplotlib.pyplot as plt
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_plot, inspect_plot_properties
from plot_data import ExampleData


@inspect_plot_properties()
@verify_plot(expected_legends=2)
def main(args):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle("Layering: Combining Multiple Plot Types", fontsize=16)

    # === Left plot: Scatter + Line ===
    ax1 = axes[0]

    # Base scatter plot - test direct matplotlib parameter (alpha=0.6)
    scatter_data = ExampleData.simple_scatter()
    drp.scatter(scatter_data, x="x", y="y", ax=ax1, alpha=0.6, label="Data points")

    # Add trend line (simplified - just connect sorted points)
    sorted_data = scatter_data.sort_values("x")
    drp.line(
        sorted_data, x="x", y="y", ax=ax1, color="red", linewidth=2, label="Trend line"
    )

    ax1.set_title("Scatter + Trend Line")
    ax1.legend()

    # === Right plot: Histogram + Distribution overlay ===
    ax2 = axes[1]

    # Base histogram - test direct matplotlib parameter (alpha=0.7)
    dist_data = ExampleData.distribution_data()
    drp.hist(
        dist_data,
        x="values",
        ax=ax2,
        alpha=0.7,
        density=True,
        bins=30,
        label="Empirical distribution",
    )

    # Add theoretical normal curve
    import numpy as np

    x_theory = np.linspace(dist_data["values"].min(), dist_data["values"].max(), 100)
    y_theory = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x_theory**2)
    ax2.plot(x_theory, y_theory, "r-", linewidth=2, label="Standard normal")

    ax2.set_title("Histogram + Theoretical Curve")
    ax2.legend()

    show_or_save_plot(fig, args, "15_layering_plots")
    return fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Layering Example")
    args = parser.parse_args()
    main(args)
