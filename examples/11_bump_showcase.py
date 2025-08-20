"""
Example 11: Bump Plot Showcase - All bump plot features.
Demonstrates ranking visualizations over time.
"""

import dr_plotter.api as drp
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

if __name__ == "__main__":
    parser = setup_arg_parser(description="Bump Plot Showcase")
    args = parser.parse_args()

    # Basic bump plot
    ranking_data = ExampleData.ranking_data()
    fig, ax = drp.bump_plot(ranking_data, time_col="time", category_col="category", 
                           value_col="score", title="Bump Plot: Rankings Over Time")
    
    show_or_save_plot(fig, args, "11_bump_showcase")