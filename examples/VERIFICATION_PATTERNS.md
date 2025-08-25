# Verification Patterns Template

This document establishes consistent patterns for using the dr_plotter verification decorators (`@verify_example` and `@verify_plot_properties`) across all 6 new examples.

## Decorator Overview

### @verify_example
Verifies legend visibility and consistency. Ensures legends appear when expected and contain correct entries.

### @verify_plot_properties  
Verifies visual encoding channels. Ensures data parameters actually create visual variation in the plots.

## Complexity Levels and Templates

### Level 1: Simple Plots (No Visual Encoding)
For plots with only data mapping, no grouping variables.

```python
@verify_example(expected_legends=0)
def main(args):
    # Simple plots without hue_by, marker_by, etc.
    # Should have clean appearance with no legends
```

**Use Case**: Basic functionality testing - scatter, line, bar, histogram without grouping.

### Level 2: Single Encoding Channel
For plots with one visual encoding parameter (typically hue_by).

```python
EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (1, 1): ["hue"],  
}

@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=2,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 3},  # 3 groups expected
        (1, 1): {"hue": 2},  # 2 groups expected
    },
)
def main(args):
    # Plots with hue_by parameter
    # Should show legends with correct group counts
```

**Use Case**: Visual encoding testing - color-based grouping.

### Level 3: Multi-Channel Encoding
For plots with multiple visual encoding parameters.

```python
EXPECTED_CHANNELS = {
    (0, 1): ["hue"],
    (1, 0): ["hue", "marker"],
    (1, 1): ["hue", "marker", "size"],
}

@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=3,
    verify_legend_consistency=True,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 1): {"hue": 4},
        (1, 0): {"hue": 3, "marker": 2},
        (1, 1): {"hue": 2, "marker": 2, "size": 3},
    },
)
def main(args):
    # Complex plots with multiple encoding channels
    # Should show consistent legends across all visual elements
```

**Use Case**: Advanced encoding testing - multiple visual channels working together.

## EXPECTED_CHANNELS Dictionary Patterns

### Coordinate System
- Key format: `(row, col)` tuples for subplot positions
- 0-indexed coordinates matching FigureManager layout
- Single plots use `(0, 0)`

### Channel Names
Standard channel names that correspond to visual encoding parameters:

- `"hue"` - Color encoding via hue_by parameter
- `"marker"` - Shape encoding via marker_by parameter  
- `"size"` - Size encoding via size_by parameter
- `"style"` - Line style encoding via style_by parameter
- `"alpha"` - Transparency encoding via alpha_by parameter

### Example Patterns

**Single Row Layout**:
```python
EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue", "marker"],
    (0, 2): ["marker"],
}
```

**2x2 Grid Layout**:
```python
EXPECTED_CHANNELS = {
    (0, 0): [],           # No encoding - basic plot
    (0, 1): ["hue"],      # Color encoding only
    (1, 0): ["marker"],   # Marker encoding only  
    (1, 1): ["hue", "marker"],  # Both encodings
}
```

## expected_legend_entries Specifications

### Format
Dictionary mapping subplot coordinates to expected legend content:
```python
expected_legend_entries={
    (row, col): {"channel_name": count, ...},
}
```

### Count Guidelines
- **hue**: Number of unique groups in hue_by column
- **marker**: Number of unique markers in marker_by column
- **size**: Number of size categories (usually 3-5 for continuous)
- **style**: Number of line styles in style_by column

### Validation Strategy
Counts should match the data generation parameters:
```python
# If using ExampleData.time_series_grouped(groups=3)
expected_legend_entries={(0, 0): {"hue": 3}}

# If using ExampleData.grouped_categories(n_groups=2, n_categories=4)  
# With hue_by="group", marker_by="category"
expected_legend_entries={(0, 0): {"hue": 2, "marker": 4}}
```

## subplot_descriptions Pattern

Optional parameter for enhanced failure messaging:
```python
@verify_example(
    expected_legends=3,
    subplot_descriptions={
        0: "Basic scatter without encoding",
        1: "Color-encoded time series", 
        2: "Multi-channel encoded complex data",
    }
)
```

Use when subplot purposes aren't obvious from titles.

## Implementation Examples by Complexity

### Example 1: Basic Functionality (Level 1)
```python
@verify_example(expected_legends=0)
def main(args):
    with FigureManager(rows=2, cols=2) as fm:
        # All basic plots, no visual encoding
        data1 = ExampleData.simple_scatter(seed=101)
        fm.plot("scatter", 0, 0, data1, x="x", y="y", title="Basic Scatter")
        
        data2 = ExampleData.time_series(seed=102)  
        fm.plot("line", 0, 1, data2, x="time", y="value", title="Basic Line")
        # ... etc
```

### Example 2: Visual Encoding (Level 2)
```python
EXPECTED_CHANNELS = {
    (0, 0): ["hue"],
    (0, 1): ["hue"], 
    (1, 0): ["hue"],
    (1, 1): ["hue"],
}

@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=4,
    expected_channels=EXPECTED_CHANNELS, 
    expected_legend_entries={
        (0, 0): {"hue": 3},
        (0, 1): {"hue": 4}, 
        (1, 0): {"hue": 2},
        (1, 1): {"hue": 3},
    },
)
def main(args):
    with FigureManager(rows=2, cols=2) as fm:
        # All plots use hue_by encoding
        data1 = ExampleData.time_series_grouped(groups=3, seed=201)
        fm.plot("scatter", 0, 0, data1, 
               x="time", y="value", hue_by="group", 
               title="Color Encoded Scatter")
        # ... etc
```

### Example 5: Advanced Features (Level 3)
```python
EXPECTED_CHANNELS = {
    (0, 0): ["hue", "style"],
    (1, 0): ["hue", "marker"],
    (1, 1): ["hue", "marker", "size"],
}

@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)
@verify_example(
    expected_legends=3,
    verify_legend_consistency=True,
    expected_channels=EXPECTED_CHANNELS,
    expected_legend_entries={
        (0, 0): {"hue": 4, "style": 2},
        (1, 0): {"hue": 3, "marker": 2}, 
        (1, 1): {"hue": 2, "marker": 2, "size": 3},
    },
)
def main(args):
    with FigureManager(rows=2, cols=2) as fm:
        # Complex multi-channel encoding
        # ... sophisticated plotting code
```

## Decorator Ordering

Always use this order when combining decorators:
```python
@verify_plot_properties(expected_channels=EXPECTED_CHANNELS)  # First
@verify_example(                                             # Second  
    expected_legends=N,
    expected_channels=EXPECTED_CHANNELS,                     # Pass same channels
    # ... other parameters
)
def main(args):
    # Function body
```

This ensures plot properties are verified before legend consistency checks.

## Error Handling Philosophy

The verification decorators are designed to:
- **Fail Fast**: Exit immediately when verification fails
- **Provide Context**: Give detailed error messages with debugging info
- **Save Plots**: Always save plots for visual debugging when failures occur
- **Be Deterministic**: Same data + same verification = same results

## Common Verification Patterns

### Pattern 1: Progressive Complexity
Start simple, add encoding channels:
- Plot 1: Basic (no encoding)
- Plot 2: Single channel (hue only)  
- Plot 3: Dual channel (hue + marker)
- Plot 4: Triple channel (hue + marker + size)

### Pattern 2: Channel Comparison
Compare different encoding approaches:
- Plot 1: Color encoding
- Plot 2: Marker encoding
- Plot 3: Size encoding  
- Plot 4: Combined encoding

### Pattern 3: Data Type Testing
Test same encoding with different data:
- Plot 1: Categorical hue_by
- Plot 2: Continuous hue_by (binned)
- Plot 3: Time-based hue_by
- Plot 4: Multi-level hue_by

Use these patterns to ensure comprehensive functionality verification across all 6 planned examples.