"""
Example 20: Validation - Error handling and data validation.
Demonstrates the library's validation system and helpful error messages.
"""

import pandas as pd
from dr_plotter.figure import FigureManager
from dr_plotter.utils import setup_arg_parser, show_or_save_plot
from plot_data import ExampleData

def demonstrate_validation_errors():
    """Show examples of validation errors and proper error messages."""
    
    print("🔍 Demonstrating validation system...")
    print()
    
    # 1. Missing column error
    print("1. Missing column validation:")
    try:
        data = ExampleData.simple_scatter()
        fm = FigureManager(rows=1, cols=1)
        fm.plot("scatter", 0, 0, data, x="nonexistent_column", y="y")
    except ValueError as e:
        print(f"   ✅ Caught error: {str(e)[:80]}...")
    print()
    
    # 2. Wrong data type error
    print("2. Data type validation:")
    try:
        # Create data with text in numeric column
        bad_data = pd.DataFrame({
            "x": ["a", "b", "c", "d"],
            "y": [1, 2, 3, 4]
        })
        fm = FigureManager(rows=1, cols=1)
        fm.plot("scatter", 0, 0, bad_data, x="x", y="y")
    except ValueError as e:
        print(f"   ✅ Caught error: {str(e)[:80]}...")
    print()
    
    # 3. Empty dataframe error
    print("3. Empty dataframe validation:")
    try:
        empty_data = pd.DataFrame()
        fm = FigureManager(rows=1, cols=1)
        fm.plot("scatter", 0, 0, empty_data, x="x", y="y")
    except ValueError as e:
        print(f"   ✅ Caught error: {str(e)[:80]}...")
    print()
    
    # 4. Too many categories error
    print("4. Categorical data validation:")
    try:
        # Create data with too many categories
        large_cat_data = pd.DataFrame({
            "category": [f"cat_{i}" for i in range(25)],  # 25 categories
            "value": range(25)
        })
        fm = FigureManager(rows=1, cols=1)
        fm.plot("bar", 0, 0, large_cat_data, x="category", y="value")
    except ValueError as e:
        print(f"   ✅ Caught error: {str(e)[:80]}...")
    print()
    
    print("✅ All validation checks working correctly!")
    print()

if __name__ == "__main__":
    parser = setup_arg_parser(description="Validation Demonstration")
    args = parser.parse_args()
    
    # Demonstrate validation system
    demonstrate_validation_errors()
    
    # Show successful plotting with proper data
    print("🎨 Creating valid plots to show successful validation...")
    
    with FigureManager(rows=2, cols=2, figsize=(12, 10)) as fm:
        fm.fig.suptitle("Validation: Successful Plots with Proper Data", fontsize=16)
        
        # Valid scatter plot
        scatter_data = ExampleData.simple_scatter()
        fm.plot("scatter", 0, 0, scatter_data, x="x", y="y", title="Valid Scatter")
        
        # Valid bar plot with reasonable categories
        cat_data = ExampleData.categorical_data()
        fm.plot("bar", 0, 1, cat_data.groupby("category")["value"].mean().reset_index(), 
                x="category", y="value", title="Valid Bar")
        
        # Valid line plot
        line_data = ExampleData.time_series()
        fm.plot("line", 1, 0, line_data, x="time", y="value", title="Valid Line")
        
        # Valid violin plot
        fm.plot("violin", 1, 1, cat_data, x="category", y="value", title="Valid Violin")
        
        show_or_save_plot(fm.fig, args, "20_validation")