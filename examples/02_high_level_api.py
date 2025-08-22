"""
Example 2: High-Level API - All plotting functions.
Demonstrates each high-level plotting function with consistent data.
"""

from plot_data import ExampleData

import dr_plotter.api as drp
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="High-Level API Example")
    args = parser.parse_args()
    # === Bump Plot ===
    bump_data = ExampleData.ranking_data()
    fig7, _ = drp.bump_plot(
        bump_data,
        time_col="time",
        category_col="category",
        value_col="score",
        title="High-Level API: Bump Plot",
    )
    show_or_save_plot(fig7, args, "02_bump")

    # === Contour Plot ===
    contour_data = ExampleData.gaussian_mixture()
    fig8, _ = drp.gmm_level_set(
        contour_data, x="x", y="y", title="High-Level API: Contour"
    )
    show_or_save_plot(fig8, args, "02_contour")

    # === Heatmap ===
    heatmap_data = ExampleData.heatmap_data()
    fig6, _ = drp.heatmap(
        heatmap_data,
        x="column",
        y="row",
        values="value",
        title="High-Level API: Heatmap",
    )
    show_or_save_plot(fig6, args, "02_heatmap")

    # === Violin Plot ===
    violin_data = ExampleData.categorical_data()
    fig5, _ = drp.violin(
        violin_data, x="category", y="value", title="High-Level API: Violin"
    )
    show_or_save_plot(fig5, args, "02_violin")

    # === Histogram ===
    hist_data = ExampleData.distribution_data()
    fig4, _ = drp.hist(hist_data, x="values", title="High-Level API: Histogram")
    show_or_save_plot(fig4, args, "02_histogram")

    # === Scatter Plot ===
    scatter_data = ExampleData.simple_scatter()
    fig1, _ = drp.scatter(
        scatter_data,
        x="x",
        y="y",
        title="High-Level API: Scatter",
        s=10,
    )
    show_or_save_plot(fig1, args, "02_scatter")

    # === Line Plot ===
    line_data = ExampleData.time_series()
    fig2, _ = drp.line(line_data, x="time", y="value", title="High-Level API: Line")
    show_or_save_plot(fig2, args, "02_line")

    # === Bar Plot ===
    bar_data = ExampleData.categorical_data()
    bar_summary = bar_data.groupby("category")["value"].mean().reset_index()
    fig3, _ = drp.bar(bar_summary, x="category", y="value", title="High-Level API: Bar")
    show_or_save_plot(fig3, args, "02_bar")
