#!/bin/bash

# Script to run all dr_plotter examples and save plots to examples/plots/
# Usage: ./examples/run_all_examples.sh

set -e  # Exit on any error

# Get the script directory (examples/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLOTS_DIR="$SCRIPT_DIR/plots"

echo "🎨 Running all dr_plotter examples..."
echo "📁 Project root: $PROJECT_ROOT"
echo "📊 Plots will be saved to: $PLOTS_DIR"

# Create plots directory if it doesn't exist
mkdir -p "$PLOTS_DIR"

# Change to project root for proper module imports
cd "$PROJECT_ROOT"

# List of example files to run (in order)
EXAMPLES=(
    "01_high_level_api.py"
    "02_layering_plots.py"
    "03_figure_manager.py"
    "04_violin_plot.py"
    "05_heatmap.py"
    "06_bump_plot.py"
    "07_gmm_level_set.py"
    "08_multi_series_plots.py"
)

echo ""
echo "🚀 Running examples..."

# Run each example
for example in "${EXAMPLES[@]}"; do
    echo "▶️  Running $example..."
    
    # Run with uv and pass save directory
    if uv run python "examples/$example" --save-dir "$PLOTS_DIR"; then
        echo "✅ $example completed successfully"
    else
        echo "❌ $example failed"
        exit 1
    fi
    echo ""
done

echo "🎉 All examples completed successfully!"
echo "📊 Generated plots are in: $PLOTS_DIR"

# List generated plots
echo ""
echo "📋 Generated plot files:"
ls -la "$PLOTS_DIR"/*.png 2>/dev/null || echo "No PNG files found"