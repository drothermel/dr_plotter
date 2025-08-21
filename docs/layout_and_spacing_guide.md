# Layout and Spacing Guide for dr_plotter

## Overview

This document describes the layout and spacing strategies used in dr_plotter, including the challenges we've solved and the design decisions made to achieve publication-quality plots with consistent spacing.

## The Challenge: Matplotlib Layout Complexity

Creating well-spaced plots in matplotlib involves navigating several competing layout systems:

1. **Default matplotlib spacing**: Often results in overlapping elements
2. **`tight_layout()`**: Good for basic layouts, but doesn't handle figure titles or complex elements
3. **`constrained_layout`**: More advanced but incompatible with `make_axes_locatable`
4. **Manual positioning**: Precise control but requires extensive configuration

## dr_plotter's Layout Philosophy

We've adopted a **unified approach** that prioritizes:

- **Consistency**: All plot types use the same layout strategy
- **Predictability**: Spacing behaves the same in single and multi-subplot scenarios
- **Quality**: Publication-ready results by default
- **Transparency**: Users don't need to understand the complexity

## Our Solution: tight_layout + make_axes_locatable

After extensive research and testing, we've standardized on:

```python
# For all plots:
tight_layout(rect=[0, 0, 1, 0.95], pad=0.5)  # When suptitle present
tight_layout(pad=0.5)                        # When no suptitle

# For colorbar placement:
make_axes_locatable(ax).append_axes("right", size="5%", pad=0.1)
```

### Why This Combination?

1. **`tight_layout`** handles subplot spacing and prevents overlap
2. **`make_axes_locatable`** provides precise colorbar control
3. **`rect` parameter** reserves space for figure-level elements
4. **Consistent values** based on matplotlib community best practices

## The Layout Conflict We Solved

### Problem: constrained_layout vs make_axes_locatable

Initial attempts mixed layout systems:
- `FigureManager` used `constrained_layout=True` for multi-subplot figures
- Individual plotters used `make_axes_locatable()` for colorbars
- These systems **cannot work together** - they fight for layout control

**Symptoms:**
- Heatmaps with excessive spacing between subplots
- Contour plots with overlapping colorbars
- Unpredictable results across different plot types

### Solution: Unified tight_layout Approach

We eliminated the conflict by:
1. **Removing `constrained_layout`** entirely from dr_plotter
2. **Using `tight_layout` everywhere** with smart rect parameters
3. **Centralizing layout logic** in `FigureManager.__exit__()`

## Spacing Parameters and Values

### Established Best Practices

Based on matplotlib community research, we use these proven values:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `rect=[0, 0, 1, 0.95]` | 5% top margin | Space for figure suptitle |
| `rect=[0, 0, 1, 0.9]` | 10% top margin | Space for longer titles |
| `pad=0.5` | Padding fraction | Prevents text clipping (recommended: ≥0.3) |
| Colorbar `size="5%"` | 5% of subplot width | Professional colorbar proportion |
| Colorbar `pad=0.1` | 0.1 inches | Space between plot and colorbar |

### Common rect Parameter Patterns

```python
# Standard layouts
[0, 0, 1, 1]      # Full figure (no suptitle)
[0, 0, 1, 0.95]   # 5% top space for suptitle
[0, 0, 1, 0.9]    # 10% top space for longer titles

# Split layouts (advanced)
[0, 0, 0.5, 1]    # Left half of figure
[0.5, 0, 1, 1]    # Right half of figure
[0, 0.5, 1, 1]    # Top half of figure
```

## Implementation Details

### Automatic Suptitle Detection

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    """Apply appropriate layout based on figure content."""
    try:
        if self.fig._suptitle is not None:
            # Reserve space for suptitle
            self.fig.tight_layout(rect=[0, 0, 1, 0.95], pad=0.5)
        else:
            # Standard layout
            self.fig.tight_layout(pad=0.5)
    except (ValueError, RuntimeError) as e:
        warnings.warn(f"tight_layout failed: {e}. Layout may not be optimal.", UserWarning)
    return False
```

### User Override Capabilities

For edge cases, users can specify custom layout parameters:

```python
# Custom spacing rectangle for special layouts
with FigureManager(rows=2, cols=2, layout_rect=[0, 0.1, 1, 0.85]) as fm:
    # Custom top/bottom margins
    fm.heatmap(...)

# Custom padding for tighter/looser spacing
with FigureManager(rows=1, cols=2, layout_pad=0.3) as fm:
    # Tighter spacing (minimum recommended: 0.3)
    fm.heatmap(...)

# Combined custom parameters
with FigureManager(layout_rect=[0, 0, 1, 0.9], layout_pad=0.8) as fm:
    # Custom rectangle with extra padding
    fm.heatmap(...)
```

## Colorbar Integration

### Why make_axes_locatable Works

See [axes_grid1 Reference](axes_grid1_reference.md) for complete details.

Key advantages:
- **Precise control**: Exact sizing (5% width) and positioning
- **Consistent proportions**: Maintains subplot ratios
- **tight_layout compatible**: Works seamlessly with our layout strategy
- **Professional results**: Publication-quality colorbar placement

### Colorbar Layout Pattern

```python
# Standard implementation (automatic in dr_plotter)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
cbar = fig.colorbar(im, cax=cax)
```

## Common Layout Issues and Solutions

### 1. Title Cutoff/Overlap
**Problem**: Figure titles get cut off or overlap with subplots  
**Solution**: Automatic `rect=[0, 0, 1, 0.95]` when suptitle detected

### 2. Colorbar Spacing
**Problem**: Inconsistent spacing between plots and colorbars  
**Solution**: Standardized `size="5%", pad=0.1` across all colorbar plots

### 3. Multi-subplot Consistency
**Problem**: Different spacing between single and multi-subplot scenarios  
**Solution**: Same `tight_layout` + `make_axes_locatable` approach everywhere

### 4. Edge Cases
**Problem**: Special layouts need custom spacing  
**Solution**: `layout_rect` parameter for user override

## Testing and Validation

Our layout approach has been validated across:
- ✅ All 20 example files
- ✅ Single and multi-subplot scenarios  
- ✅ All plot types (scatter, line, bar, heatmap, violin, etc.)
- ✅ Plots with and without colorbars
- ✅ Various figure sizes and aspect ratios

## Debugging Layout Issues

When `tight_layout` fails, dr_plotter provides specific warnings:

```python
# Example warnings you might see:
"tight_layout failed: tight_layout cannot make axes width small enough to accommodate all axes decorations"
"tight_layout runtime error: ..."
```

Common causes and solutions:
1. **Too many subplots**: Reduce subplot count or increase figure size
2. **Long labels**: Use shorter labels or rotate text
3. **Large colorbars**: Adjust colorbar size percentage
4. **Complex layouts**: Use custom `layout_rect` parameter

## Advanced Usage

### Custom Layout Parameters

```python
# Reserve extra space at bottom for caption
with FigureManager(layout_rect=[0, 0.15, 1, 0.9]) as fm:
    fm.scatter(0, 0, data, x="x", y="y")
    
# Tighter spacing for dense layouts
with FigureManager(rows=3, cols=3, layout_pad=0.2) as fm:
    # Minimum spacing between subplots
    for i in range(9):
        fm.scatter(i//3, i%3, data, x="x", y="y")

# Split figure for side-by-side panels with custom padding
with FigureManager(layout_rect=[0, 0, 0.48, 1], layout_pad=0.8) as fm_left:
    fm_left.heatmap(0, 0, data1, ...)
    
with FigureManager(layout_rect=[0.52, 0, 1, 1], layout_pad=0.8) as fm_right:
    fm_right.heatmap(0, 0, data2, ...)
```

### Integration with matplotlib

```python
# dr_plotter works seamlessly with matplotlib
fig, axes = plt.subplots(2, 2)
with FigureManager(external_ax=axes[0,0]) as fm:
    fm.scatter(0, 0, data, x="x", y="y")
# Layout handled automatically
```

## References

- [axes_grid1 Reference](axes_grid1_reference.md) - Comprehensive guide to matplotlib's advanced layout toolkit
- [Matplotlib tight_layout guide](https://matplotlib.org/stable/users/explain/axes/tight_layout_guide.html)
- [Stack Overflow: tight_layout with suptitle](https://stackoverflow.com/questions/8248467/tight-layout-doesnt-take-into-account-figure-suptitle)

## Summary

dr_plotter's layout system provides:
- **Automatic spacing optimization** via intelligent `tight_layout` usage
- **Professional colorbar placement** via `make_axes_locatable`  
- **Suptitle compatibility** via automatic `rect` parameter adjustment
- **User control** via optional `layout_rect` parameter
- **Consistent results** across all plot types and scenarios

This approach delivers publication-quality layouts with minimal user configuration while maintaining full control for advanced use cases.