"""
Example 10: Cross-Subplot Color Coordination with FigureManager

This example demonstrates the new color coordination feature where
the same hue values get consistent colors across all subplots.
"""

import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot

if __name__ == "__main__":
    parser = setup_arg_parser(description="Color Coordination Example")
    args = parser.parse_args()

    # Create synthetic scaling data similar to ML experiments
    np.random.seed(42)
    
    # Simulate model scaling data across different datasets
    model_sizes = ["10M", "100M", "1B"]
    datasets = ["Dataset A", "Dataset B", "Dataset C"] 
    tokens = np.logspace(8, 10, 20)  # 10^8 to 10^10 tokens
    
    data_records = []
    for dataset in datasets:
        for model_size in model_sizes:
            # Simulate scaling law: loss ~ tokens^(-alpha) with model-dependent alpha
            size_factor = {"10M": 1.0, "100M": 0.7, "1B": 0.5}[model_size]
            dataset_factor = {"Dataset A": 1.0, "Dataset B": 0.8, "Dataset C": 1.2}[dataset]
            
            base_loss = 100 * size_factor * dataset_factor
            alpha = 0.1 + {"10M": 0.0, "100M": 0.02, "1B": 0.04}[model_size]
            
            for token_count in tokens:
                loss = base_loss * (token_count / 1e8) ** (-alpha)
                # Add some noise
                loss *= (1 + np.random.normal(0, 0.1))
                
                data_records.append({
                    "tokens": token_count,
                    "loss": loss,
                    "model_size": model_size,
                    "dataset": dataset
                })
    
    df = pd.DataFrame(data_records)
    
    # Create figure with 1 row, 3 columns (one per dataset)
    fm = FigureManager(rows=1, cols=3, figsize=(15, 5))
    fm.fig.suptitle("ML Scaling Laws: Color Coordination Demo", fontsize=16)
    
    # Plot each dataset in a separate subplot
    # The key feature: model_size colors will be consistent across all subplots!
    for i, dataset in enumerate(datasets):
        dataset_data = df[df["dataset"] == dataset]
        
        fm.line(
            row=0,
            col=i,
            data=dataset_data,
            x="tokens",
            y="loss",
            hue="model_size",  # This will have consistent colors across subplots!
            title=f"{dataset}",
            xlabel="Training Tokens",
            ylabel="Loss"
        )
        
        # Set log scale for better visualization
        ax = fm.get_axes(row=0, col=i)
        ax.set_xscale('log')
        ax.set_yscale('log')
    
    show_or_save_plot(fm.fig, args, "10_color_coordination")