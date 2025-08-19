"""
Example 5: Heatmap with the new Theming system.
"""

import pandas as pd
import numpy as np
import dr_plotter.api as drp
from dr_plotter import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="Heatmap Example")
    args = parser.parse_args()

    np.random.seed(0)

    # Create tidy/long format data for heatmap
    features = [f"Feature_{i}" for i in range(8)]
    samples = [f"Sample_{i}" for i in range(8)]

    # Generate correlation-like data in tidy format
    tidy_data = []
    for i, feature1 in enumerate(features):
        for j, feature2 in enumerate(features):
            # Create correlation-like values
            if i == j:
                correlation = 1.0  # Perfect self-correlation
            else:
                correlation = (
                    np.random.rand() * 0.8 - 0.4
                )  # Random correlation between -0.4 and 0.4

            tidy_data.append(
                {
                    "feature_x": feature1,
                    "feature_y": feature2,
                    "correlation": correlation,
                }
            )

    data = pd.DataFrame(tidy_data)

    # Themed heatmap with default options
    fig1, _ = drp.heatmap(
        data,
        x="feature_x",
        y="feature_y",
        values="correlation",
        title="Themed Correlation Matrix",
    )
    show_or_save_plot(fig1, args, "05_heatmap_default")

    # Themed heatmap with user overrides
    fig2, _ = drp.heatmap(
        data,
        x="feature_x",
        y="feature_y",
        values="correlation",
        title="Themed Correlation Matrix (Customized)",
        cmap="plasma",
        display_values=False,
        xlabel_pos="bottom",
    )
    show_or_save_plot(fig2, args, "05_heatmap_custom")

    # Example using FigureManager for multi-subplot heatmaps
    with FigureManager(rows=1, cols=2, figsize=(12, 5)) as fm:
        # Add first heatmap
        fm.heatmap(
            0,
            0,
            data,
            x="feature_x",
            y="feature_y",
            values="correlation",
            title="Correlation Matrix (Left)",
            cmap="viridis",
        )

        # Create second dataset with different values for comparison
        data2 = data.copy()
        data2["correlation"] = data2["correlation"] * 1.5  # Scale values

        # Add second heatmap
        fm.heatmap(
            0,
            1,
            data2,
            x="feature_x",
            y="feature_y",
            values="correlation",
            title="Scaled Correlation Matrix (Right)",
            cmap="plasma",
            display_values=False,
        )

        fig3 = fm.fig

    show_or_save_plot(fig3, args, "05_heatmap_figure_manager")
