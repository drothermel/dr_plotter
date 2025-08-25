# New Examples Implementation Reference

This document provides implementation agents with all necessary patterns, conventions, and standards for creating the 6 new dr_plotter functionality-testing examples.

## File Naming Conventions

### Format
`{number}_{descriptive_name}.py`

### Assigned Names
1. `01_basic_functionality.py` - Fundamental plot types without complex encoding
2. `02_visual_encoding.py` - Visual encoding systems (hue_by, marker_by, etc.)
3. `03_layout_composition.py` - FigureManager layouts and subplot coordination  
4. `04_specialized_plots.py` - Heatmap, contour, violin specialized functionality
5. `05_advanced_features.py` - Complex parameter combinations and edge cases
6. `06_integration_patterns.py` - Real-world usage patterns and performance

### Numbering Rationale
Numbers 01-06 replace the existing scattered examples while maintaining intuitive ordering by complexity.

## Import Pattern Standards

### Required Imports (All Files)
```python
from dr_plotter.figure import FigureManager
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_example, verify_plot_properties
from plot_data import ExampleData
```

### Optional Imports (When Needed)
```python
import dr_plotter.api as drp  # Only for single-plot examples (rare)
from typing import Dict, Tuple, List  # For type aliases only
```

### Import Ordering
1. Standard library imports (none expected for these examples)
2. Third-party imports (none expected)
3. dr_plotter imports (as shown above)
4. Local imports (`plot_data`)

## Function Signature Templates

### Standard Template
```python
@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)  # If needed
@verify_example(
    expected_legends=N,
    # ... additional verification parameters
)
def main(args):
    # Implementation
    show_or_save_plot(fm.fig, args, "filename_without_extension")
    return fm.fig


if __name__ == "__main__":
    parser = setup_arg_parser(description="Clear Example Description")
    args = parser.parse_args()
    main(args)
```

### Type Annotations
```python
from typing import Any
from argparse import Namespace

def main(args: Namespace) -> Any:
    # Implementation
```

## Title and Description Patterns

### Module Docstring Template
```python
"""
Example N: Title - Specific focus description.
Demonstrates specific functionality being tested.
"""
```

### Description Guidelines
- **Title**: Clear, specific functionality focus
- **Subtitle**: 2-4 word focus description
- **Demonstrates**: Single sentence explaining what's being tested

### Examples
```python
"""
Example 1: Basic Functionality - Core plot types without visual encoding.
Demonstrates fundamental plotting capabilities across all basic plot types.
"""

"""
Example 2: Visual Encoding - Color, marker, and style encoding systems.
Demonstrates hue_by, marker_by, and other visual encoding parameters.
"""
```

### Plot Title Standards
- Format: `"Descriptive Purpose"` (not generic labels)
- Good: `"Color Encoded Time Series"`, `"Multi-Channel Scatter"`
- Bad: `"Plot 1"`, `"Scatter"`, `"Data Visualization"`

### Figure Suptitle Pattern
```python
fm.fig.suptitle("Example N: Focus Area - Comprehensive Description", fontsize=16)
```

## FigureManager Usage Patterns

### Context Manager (Always Use)
```python
with FigureManager(rows=2, cols=2, figsize=(12, 10)) as fm:
    # All plotting within context
    fm.fig.suptitle("Overall Title", fontsize=16)
    
    # Individual plots
    fm.plot("plot_type", row, col, data, 
           x="x", y="y",                    # REQUIRED: data mapping
           hue_by="group",                  # GROUPING: color encoding
           title="Specific Plot Purpose"    # STYLING: plot identification
    )
```

### Layout Guidelines
- **2x2 Grid**: Standard for showcasing 4 different aspects
- **1x3 or 3x1**: For progressive complexity demonstrations
- **2x3**: For comprehensive coverage (6 plots maximum)
- **figsize**: `(12, 10)` for 2x2, `(15, 5)` for 1x3, `(15, 12)` for 2x3

### Subplot Coordination
Ensure subplots serve complementary purposes:
- Progressive complexity (simple → complex)
- Feature comparison (encoding A vs encoding B)
- Data type variation (categorical vs continuous)
- Parameter effect demonstration (default vs custom)

## Data Generation Patterns

### Standard Data Loading
```python
# Use specific seeds from DATA_MAPPING_STRATEGY.md
data = ExampleData.generator_name(param1=value1, seed=specific_seed)

# Always validate critical columns exist
assert 'x_column' in data.columns
assert 'y_column' in data.columns
```

### Data Validation Template
```python
# For grouped data
grouped_data = ExampleData.grouped_generator(groups=3, seed=201)
assert 'group' in grouped_data.columns
assert len(grouped_data.groupby('group')) == 3
```

### Data Transformation (When Needed)
```python
# Only when necessary for specific plot types
summary_data = raw_data.groupby("category")["value"].mean().reset_index()
```

## Verification Integration

### EXPECTED_CHANNELS Definition
```python
# Place before function definition, after imports
EXPECTED_CHANNELS = {
    (0, 0): ["hue"],                    # subplot (0,0) has color encoding
    (0, 1): ["hue", "marker"],          # subplot (0,1) has color + marker
    (1, 0): [],                         # subplot (1,0) has no encoding  
    (1, 1): ["hue", "marker", "size"],  # subplot (1,1) has triple encoding
}
```

### Verification Parameter Alignment
Ensure consistency between:
- Data generation parameters (group counts)
- EXPECTED_CHANNELS specifications
- expected_legend_entries counts
- Actual plotting parameters

## Parameter Documentation Integration

### Required Parameter Documentation
Every plot call must use the parameter documentation template:
```python
fm.plot("scatter", 0, 0, data,
    x="x", y="y",                    # REQUIRED: data mapping
    hue_by="group",                 # GROUPING: color encoding  
    alpha=0.7,                      # CUSTOM: transparency override
    title="Clear Plot Purpose"      # STYLING: plot identification
)
```

### Documentation Consistency
- All REQUIRED parameters documented
- All GROUPING parameters documented
- Selected CUSTOM parameters documented
- STYLING titles always present

## Success Criteria Definitions

### Functional Requirements
- All plots render without errors
- Verification decorators pass successfully
- Data parameters create expected visual variation
- Legends appear with correct entry counts
- Layout coordination works as expected

### Quality Requirements  
- Code follows dr_plotter style (no comments, comprehensive typing)
- Parameter documentation is complete and accurate
- Data selections optimize visual testing
- Plot titles clearly indicate testing purpose
- File structure matches template exactly

### Educational Value
- Each example tests distinct functionality
- Progressive complexity across examples
- Clear parameter effect demonstrations
- Practical usage pattern examples

## Error Prevention Checklist

### Before Implementation
- [ ] Review DATA_MAPPING_STRATEGY.md for data assignments
- [ ] Review VERIFICATION_PATTERNS.md for decorator usage
- [ ] Review PARAMETER_DOCUMENTATION_TEMPLATE.md for commenting
- [ ] Confirm example number and focus area

### During Implementation  
- [ ] Use exact import patterns
- [ ] Follow FigureManager context manager pattern
- [ ] Apply parameter documentation to every plot call
- [ ] Validate data structure before plotting
- [ ] Test verification decorator parameters

### After Implementation
- [ ] All verification decorators pass
- [ ] Plot titles are descriptive and specific  
- [ ] Parameter documentation is complete
- [ ] File follows exact template structure
- [ ] Code adheres to dr_plotter style guidelines

## Integration Notes

### With Existing Infrastructure
These examples build on:
- **ExampleData class**: Proven data generation patterns
- **Verification decorators**: Established testing framework
- **FigureManager**: Mature subplot coordination
- **Utility functions**: Standard argument parsing and plot saving

### Replacement Strategy
New examples replace existing scattered functionality while:
- Maintaining all tested functionality
- Improving organization and focus
- Adding systematic parameter testing
- Enhancing educational progression

This reference ensures all implementation agents create consistent, high-quality examples that fulfill the dr_plotter restructuring objectives.