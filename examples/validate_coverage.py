"""
Validation script to ensure all plotters and features are tested in examples.
Follows the design philosophy of pragmatic, example-driven testing.
"""

import os
import re
from pathlib import Path
from dr_plotter.plotters import BasePlotter

def get_all_example_files():
    """Get all example files except this validation script."""
    examples_dir = Path(__file__).parent
    return [
        f for f in examples_dir.glob("*.py") 
        if f.name not in ["validate_coverage.py", "plot_data.py"]
    ]

def extract_plotter_usage(file_path):
    """Extract all plotter usage patterns from an example file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    used_plotters = set()
    
    # Direct method calls (fm.scatter, drp.line, etc.)
    method_patterns = [
        r'\.scatter\(',
        r'\.line\(',
        r'\.bar\(',
        r'\.hist\(',
        r'\.violin\(',
        r'\.heatmap\(',
        r'\.bump_plot\(',
        r'\.gmm_level_set\(',
        r'\.grouped_bar\(',
    ]
    
    plotter_mapping = {
        'scatter': 'scatter',
        'line': 'line', 
        'bar': 'bar',
        'hist': 'histogram',
        'violin': 'violin',
        'heatmap': 'heatmap',
        'bump_plot': 'bump',
        'gmm_level_set': 'contour',
        'grouped_bar': 'bar',  # Same plotter, different usage
    }
    
    for pattern in method_patterns:
        if re.search(pattern, content):
            method_name = pattern.replace(r'\.', '').replace(r'\(', '')
            if method_name in plotter_mapping:
                used_plotters.add(plotter_mapping[method_name])
    
    # Generic plot() calls with string literals
    plot_calls = re.findall(r'\.plot\(\s*["\'](\w+)["\']', content)
    used_plotters.update(plot_calls)
    
    return used_plotters

def extract_feature_usage(file_path):
    """Extract visual encoding features used in an example."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    features = set()
    
    # Visual encoding parameters (updated for _by suffix pattern)
    encoding_patterns = [
        (r'hue_by\s*=', 'hue_encoding'),
        (r'style_by\s*=', 'style_encoding'),
        (r'size_by\s*=', 'size_encoding'),
        (r'marker_by\s*=', 'marker_encoding'),
        (r'alpha_by\s*=', 'alpha_encoding'),
        (r'y\s*=\s*\[', 'multi_metrics'),  # Multi-metric plotting
        (r'consts\.METRICS', 'metrics_constant'),
        (r'FigureManager', 'figure_manager'),
        (r'external_ax\s*=', 'external_axes'),
    ]
    
    for pattern, feature in encoding_patterns:
        if re.search(pattern, content):
            features.add(feature)
    
    return features

def main():
    """Main validation logic."""
    print("🔍 Validating example coverage...\n")
    
    # Get all registered plotters
    all_plotters = set(BasePlotter.list_plotters())
    print(f"📋 Registered plotters ({len(all_plotters)}):")
    for plotter in sorted(all_plotters):
        print(f"   - {plotter}")
    print()
    
    # Analyze all examples
    example_files = get_all_example_files()
    print(f"📁 Found {len(example_files)} example files\n")
    
    all_used_plotters = set()
    all_used_features = set()
    file_analysis = {}
    
    for example_file in example_files:
        plotters = extract_plotter_usage(example_file)
        features = extract_feature_usage(example_file)
        
        all_used_plotters.update(plotters)
        all_used_features.update(features)
        
        file_analysis[example_file.name] = {
            'plotters': plotters,
            'features': features
        }
    
    # Report coverage
    print("📊 PLOTTER COVERAGE ANALYSIS")
    print("=" * 50)
    
    covered_plotters = all_plotters & all_used_plotters
    missing_plotters = all_plotters - all_used_plotters
    
    print(f"✅ Covered plotters ({len(covered_plotters)}/{len(all_plotters)}):")
    for plotter in sorted(covered_plotters):
        # Find which examples use this plotter
        examples = [
            fname for fname, analysis in file_analysis.items()
            if plotter in analysis['plotters']
        ]
        print(f"   - {plotter}: {', '.join(sorted(examples))}")
    
    if missing_plotters:
        print(f"\n❌ Missing plotters ({len(missing_plotters)}):")
        for plotter in sorted(missing_plotters):
            print(f"   - {plotter}")
    
    print(f"\n📈 FEATURE COVERAGE ANALYSIS")
    print("=" * 50)
    
    expected_features = {
        'hue_encoding', 'style_encoding', 'size_encoding', 'marker_encoding', 
        'alpha_encoding', 'multi_metrics', 'metrics_constant', 'figure_manager'
    }
    
    covered_features = expected_features & all_used_features
    missing_features = expected_features - all_used_features
    
    print(f"✅ Covered features ({len(covered_features)}/{len(expected_features)}):")
    for feature in sorted(covered_features):
        examples = [
            fname for fname, analysis in file_analysis.items()
            if feature in analysis['features']
        ]
        print(f"   - {feature}: {', '.join(sorted(examples))}")
    
    if missing_features:
        print(f"\n❌ Missing features ({len(missing_features)}):")
        for feature in sorted(missing_features):
            print(f"   - {feature}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT")
    print("=" * 50)
    
    plotter_coverage = len(covered_plotters) / len(all_plotters) * 100
    feature_coverage = len(covered_features) / len(expected_features) * 100
    
    print(f"📊 Plotter coverage: {plotter_coverage:.1f}% ({len(covered_plotters)}/{len(all_plotters)})")
    print(f"🔧 Feature coverage: {feature_coverage:.1f}% ({len(covered_features)}/{len(expected_features)})")
    
    if plotter_coverage == 100 and feature_coverage == 100:
        print("🎉 PERFECT COVERAGE! All plotters and features are tested.")
        return True
    elif plotter_coverage >= 90 and feature_coverage >= 90:
        print("✅ EXCELLENT COVERAGE! Nearly all functionality is tested.")
        return True
    elif plotter_coverage >= 80 and feature_coverage >= 80:
        print("👍 GOOD COVERAGE! Most functionality is tested.")
        return True
    else:
        print("⚠️  NEEDS IMPROVEMENT! Coverage is below recommended levels.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)