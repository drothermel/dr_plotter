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

# Updated list of example files (new thematic structure)
EXAMPLES=(
    # Part 1: The Basics (01-04)
    "01_quickstart.py"
    "02_high_level_api.py"
    "03_figure_manager_basics.py"
    "04_plot_registry.py"
    
    # Part 2: Core Concepts (05-08)
    "05_multi_series_plotting.py"
    "06_multi_metric_plotting.py"
    "07_grouped_plotting.py"
    "08_color_coordination.py"
    
    # Part 3: Plotter Showcases (09-14)
    "09_scatter_showcase.py"
    "10_line_showcase.py"
    "11_bar_showcase.py"
    "12_violin_showcase.py"
    "13_heatmap_showcase.py"
    "14_contour_showcase.py"
    
    # Part 4: Advanced Usage (15-20)
    "15_layering_plots.py"
    "16_matplotlib_integration.py"
    "17_custom_plotters.py"
    "18_scientific_figures.py"
    "19_ml_dashboard.py"
)

echo ""
echo "🚀 Running examples..."
echo "📋 Total examples to run: ${#EXAMPLES[@]}"
echo ""

# Run coverage validation first
echo "🔍 Validating coverage..."
if uv run python "examples/validate_coverage.py"; then
    echo "✅ Coverage validation passed"
else
    echo "❌ Coverage validation failed"
    exit 1
fi
echo ""

# Run each example
PASSED=0
FAILED=0

for example in "${EXAMPLES[@]}"; do
    echo "▶️  Running $example..."
    
    # Run with uv and pass save directory
    if uv run python "examples/$example" --save-dir "$PLOTS_DIR"; then
        echo "✅ $example completed successfully"
        ((PASSED++))
    else
        echo "❌ $example failed"
        ((FAILED++))
        if [[ "${CONTINUE_ON_FAILURE:-0}" != "1" ]]; then
            exit 1
        fi
    fi
    echo ""
done

echo "🎉 Examples run completed!"
echo "📊 Results: $PASSED passed, $FAILED failed"
echo "📁 Generated plots are in: $PLOTS_DIR"

# List generated plots by category
echo ""
echo "📋 Generated plot files by thematic category:"

echo "   📁 Part 1: The Basics (01-04):"
ls -1 "$PLOTS_DIR"/{01,02,03,04}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

echo "   📁 Part 2: Core Concepts (05-08):"
ls -1 "$PLOTS_DIR"/{05,06,07,08}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

echo "   📁 Part 3: Plotter Showcases (09-14):"
ls -1 "$PLOTS_DIR"/{09,10,11,12,13,14}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

echo "   📁 Part 4: Advanced Usage (15-20):"
ls -1 "$PLOTS_DIR"/{15,16,17,18,19,20}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

# Final count
TOTAL_PLOTS=$(ls "$PLOTS_DIR"/*.png 2>/dev/null | wc -l || echo "0")
echo ""
echo "📊 Total plots generated: $TOTAL_PLOTS"

# Success only if no failures
if [[ $FAILED -eq 0 ]]; then
    echo "🎉 All examples completed successfully!"
    exit 0
else
    echo "⚠️  Some examples failed. Check output above."
    exit 1
fi
