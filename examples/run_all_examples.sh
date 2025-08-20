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

# Updated list of example files (new structure)
EXAMPLES=(
    # Basic API examples (01-04)
    "01_quickstart.py"
    "02_high_level_api.py"
    "03_figure_manager_basics.py"
    "04_plot_registry.py"
    
    # Plotter showcase examples (05-12)
    "05_scatter_showcase.py"
    "06_line_showcase.py"
    "07_bar_showcase.py"
    "08_histogram_showcase.py"
    "09_violin_showcase.py"
    "10_heatmap_showcase.py"
    "11_bump_showcase.py"
    "12_contour_showcase.py"
    
    # Advanced features examples (13-16)
    "13_multi_series.py"
    "14_multi_metrics.py"
    "15_layering.py"
    "16_color_coordination.py"
    
    # Real-world use cases (17-20)
    "17_ml_experiment.py"
    "18_scientific_figures.py"
    "19_custom_plotter.py"
    "20_matplotlib_integration.py"
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
echo "📋 Generated plot files by category:"

echo "   📁 Basic API (01-04):"
ls -1 "$PLOTS_DIR"/{01,02,03,04}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

echo "   📁 Plotter Showcase (05-12):"
ls -1 "$PLOTS_DIR"/{05,06,07,08,09,10,11,12}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

echo "   📁 Advanced Features (13-16):"
ls -1 "$PLOTS_DIR"/{13,14,15,16}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

echo "   📁 Real-World Use Cases (17-20):"
ls -1 "$PLOTS_DIR"/{17,18,19,20}_*.png 2>/dev/null | sed 's/.*\//      /' || echo "      No files found"

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