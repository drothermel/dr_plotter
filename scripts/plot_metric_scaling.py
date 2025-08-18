#!/usr/bin/env python3
"""
Plot model scaling for any DataDecide metric.

Usage:
    python scripts/plot_metric_scaling.py wikitext_103-valppl
    python scripts/plot_metric_scaling.py pile-valppl
    python scripts/plot_metric_scaling.py primary_metric --min-params 150M
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datadec import DataDecide
from datadec import model_utils
import dr_plotter.api as dp
from dr_plotter.plotters.curve import CurvePlotter


def load_datadec_data(data_dir="./test_data", verbose=False):
    """Load DataDecide data, checking if it exists first."""
    data_exists = os.path.exists(os.path.join(data_dir, "datadecide", "full_eval.parquet"))
    recompute_param = None if data_exists else "all"
    
    if not data_exists:
        print("Data not found, downloading and processing (this may take a few minutes)...")
    
    dd = DataDecide(data_dir=data_dir, recompute_from=recompute_param, verbose=verbose)
    return dd


def prepare_scaling_data(dd, metric_name, min_params=None):
    """Prepare data for scaling analysis."""
    # Get analysis dataframe
    analysis_df = dd.get_analysis_df(
        min_params=min_params, 
        add_lr_cols=True, 
        verbose=False
    )
    
    # Check if metric exists
    if metric_name not in analysis_df.columns:
        available_metrics = [col for col in analysis_df.columns 
                           if any(keyword in col.lower() for keyword in ['ppl', 'acc', 'metric', 'prob', 'correct'])]
        raise ValueError(f"Metric '{metric_name}' not found. Available metrics include: {available_metrics[:10]}...")
    
    # Filter out rows with missing metric values
    clean_df = analysis_df.dropna(subset=[metric_name])
    
    if len(clean_df) == 0:
        raise ValueError(f"No data available for metric '{metric_name}'")
    
    # Group by model size and data recipe, average across seeds
    scaling_data = clean_df.groupby(['params', 'data']).agg({
        metric_name: 'mean'
    }).reset_index()
    
    # Convert model size to numeric for proper ordering
    scaling_data['params_numeric'] = scaling_data['params'].apply(model_utils.param_to_numeric)
    scaling_data = scaling_data.sort_values('params_numeric')
    
    return scaling_data


def create_scaling_plot(scaling_data, metric_name):
    """Create scaling plot using dr_plotter's curve comparison."""
    
    # Sort data for proper line connections
    scaling_data = scaling_data.sort_values('params_numeric')
    
    # Use CurvePlotter's built-in comparison method
    plotter = CurvePlotter(scaling_data)
    fig, ax = plotter.plot_curve_comparison(
        x_col='params_numeric',
        y_col=metric_name, 
        group_by='data',
        marker='o'  # Add markers to make it look more like scatter
    )
    
    # Only add what dr_plotter doesn't handle
    ax.set_xscale('log')  # Log scale for model sizes
    ax.set_xlabel('Model Size (M parameters)')
    ax.set_ylabel(metric_name.replace('_', ' ').replace('-', ' ').title())
    ax.set_title(f'Model Scaling: {metric_name.replace("_", " ").replace("-", " ").title()}')
    
    plt.show()
    return fig, ax


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Plot model scaling for DataDecide metrics')
    parser.add_argument('metric', help='Metric name to plot (e.g., wikitext_103-valppl, pile-valppl)')
    parser.add_argument('--min-params', help='Minimum model size (e.g., 10M, 150M)')
    parser.add_argument('--data-dir', default='./test_data', 
                       help='Data directory for DataDecide cache (default: ./test_data)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        print(f"Loading DataDecide data...")
        dd = load_datadec_data(args.data_dir, args.verbose)
        
        print(f"Preparing scaling data for metric: {args.metric}")
        scaling_data = prepare_scaling_data(dd, args.metric, args.min_params)
        
        print(f"Found {len(scaling_data)} model-recipe combinations")
        print(f"Model sizes: {sorted(scaling_data['params'].unique())}")
        print(f"Data recipes: {sorted(scaling_data['data'].unique())}")
        
        print("Creating scaling plot...")
        fig, ax = create_scaling_plot(scaling_data, args.metric)
        
        print("✅ Plot displayed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()