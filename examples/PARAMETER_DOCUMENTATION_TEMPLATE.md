# Parameter Documentation Template

This template establishes consistent parameter documentation patterns for all dr_plotter examples. Each parameter should be categorized and documented using inline comments that indicate its purpose and classification.

## Parameter Categories

### REQUIRED: Data Mapping Parameters
Parameters that specify which columns to map to visual channels. These are essential for the plot to function.

```python
fm.plot("scatter", 0, 0, data,
    x="x", y="y",                    # REQUIRED: data mapping
    # ... other parameters
)
```

### DEFAULT: Theme Default Parameters
Parameters that use theme defaults but could be customized. Do not specify these unless testing default behavior.

```python
fm.plot("scatter", 0, 0, data,
    x="x", y="y",                    # REQUIRED: data mapping
    s=50,                           # DEFAULT: marker size (theme default)
    linewidth=1.5,                  # DEFAULT: line width (theme default)
    # ... other parameters
)
```

### CUSTOM: Styling Overrides
Parameters that override theme defaults to demonstrate customization capabilities.

```python
fm.plot("scatter", 0, 0, data,
    x="x", y="y",                    # REQUIRED: data mapping
    alpha=0.8,                      # CUSTOM: transparency override
    color="red",                    # CUSTOM: color override
    # ... other parameters
)
```

### GROUPING: Visual Encoding
Parameters that create visual groupings through hue, marker, or other encoding channels.

```python
fm.plot("scatter", 0, 0, data,
    x="x", y="y",                    # REQUIRED: data mapping
    hue_by="group",                 # GROUPING: color encoding
    marker_by="type",               # GROUPING: marker encoding
    # ... other parameters
)
```

### STYLING: Plot Identification
Parameters that help identify and organize plots but don't affect data representation.

```python
fm.plot("scatter", 0, 0, data,
    x="x", y="y",                    # REQUIRED: data mapping
    title="Clear Purpose",          # STYLING: plot identification
    # ... other parameters
)
```

## Plot Type Specific Templates

### Scatter Plots
```python
fm.plot("scatter", row, col, data,
    x="x_column", y="y_column",     # REQUIRED: data mapping
    hue_by="group_column",          # GROUPING: color encoding
    marker_by="type_column",        # GROUPING: marker encoding
    s=50,                          # DEFAULT: marker size
    alpha=0.7,                     # CUSTOM: transparency override
    title="Plot Purpose"           # STYLING: plot identification
)
```

### Line Plots
```python
fm.plot("line", row, col, data,
    x="time", y="value",           # REQUIRED: data mapping
    hue_by="series",               # GROUPING: color encoding
    style_by="condition",          # GROUPING: line style encoding
    linewidth=2,                   # DEFAULT: line width
    alpha=0.8,                     # CUSTOM: transparency override
    title="Time Series Analysis"   # STYLING: plot identification
)
```

### Bar Plots
```python
fm.plot("bar", row, col, data,
    x="category", y="value",       # REQUIRED: data mapping
    hue_by="group",                # GROUPING: color encoding
    width=0.8,                     # DEFAULT: bar width
    alpha=0.9,                     # CUSTOM: transparency override
    title="Category Comparison"    # STYLING: plot identification
)
```

### Heatmaps
```python
fm.plot("heatmap", row, col, data,
    x="column", y="row", values="value",  # REQUIRED: data mapping
    cmap="viridis",                # DEFAULT: colormap
    annot=True,                    # CUSTOM: show annotations
    title="Correlation Matrix"     # STYLING: plot identification
)
```

### Violin Plots
```python
fm.plot("violin", row, col, data,
    x="category", y="value",       # REQUIRED: data mapping
    hue_by="group",                # GROUPING: color encoding
    inner="quartile",              # DEFAULT: inner representation
    alpha=0.7,                     # CUSTOM: transparency override
    title="Distribution Comparison" # STYLING: plot identification
)
```

### Contour Plots
```python
fm.plot("contour", row, col, data,
    x="x", y="y", values="z",      # REQUIRED: data mapping
    levels=10,                     # DEFAULT: number of contours
    cmap="plasma",                 # CUSTOM: colormap override
    title="Density Contours"       # STYLING: plot identification
)
```

## Documentation Guidelines

### When to Use Each Category

1. **REQUIRED**: Always document data mapping parameters. These are non-negotiable for plot functionality.

2. **DEFAULT**: Use sparingly, only when demonstrating that defaults work well or when showing parameter availability.

3. **CUSTOM**: Use to show customization capabilities and parameter effects. Focus on parameters that significantly change plot appearance.

4. **GROUPING**: Always document visual encoding parameters. These are key to dr_plotter's functionality.

5. **STYLING**: Use for titles and organizational parameters. Keep titles descriptive of the plot's purpose.

### Comment Formatting Rules

- Keep comments on the same line as parameters
- Use consistent spacing: `parameter=value,  # CATEGORY: description`
- Description should be concise but informative
- Group related parameters visually by placing them adjacent

### Parameter Selection Strategy

For each example plot:
1. Always include REQUIRED data mapping
2. Include 1-2 GROUPING parameters when testing visual encoding
3. Include 1-2 CUSTOM parameters to show flexibility
4. Always include STYLING title parameter
5. Minimize DEFAULT parameters unless specifically demonstrating defaults

This ensures each plot serves a clear testing purpose while maintaining documentation consistency across all examples.