"""
Example 12: Contour Plot Showcase - All contour plot features.
Demonstrates Gaussian Mixture Model level set visualizations.
"""

from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Contour Plot Showcase")
    args = parser.parse_args()

    with FigureManager(rows=1, cols=2, figsize=(15, 6)) as fm:
        fm.fig.suptitle("Contour Plot Showcase: Density Visualization", fontsize=16)

        # Basic contour plot
        mixture_data = ExampleData.gaussian_mixture(n_components=2)
        fm.gmm_level_set(0, 0, mixture_data, x="x", y="y", title="2-Component GMM")

        # More complex mixture
        complex_mixture = ExampleData.gaussian_mixture(n_components=3)
        fm.gmm_level_set(0, 1, complex_mixture, x="x", y="y", title="3-Component GMM")

        show_or_save_plot(fm.fig, args, "12_contour_showcase")
