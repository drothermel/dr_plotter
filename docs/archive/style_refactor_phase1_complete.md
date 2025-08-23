# Style Refactor Phase 1: Complete

## Summary

Phase 1 of the styling system refactor has been successfully implemented. The new `StyleApplicator` class provides a unified, component-based styling system that addresses all the issues identified in the original plan.

## Key Implementation Decisions

### 1. Universal Multi-Component Model

Every plot is treated as having components, with simple plots having a single "main" component. This provides:
- Consistent interface across all plot types
- Natural progression from simple to complex plots
- Explicit component boundaries through schemas

### 2. Component Schema System

Each plot type defines its component schema:
```python
"scatter": {"main": {"s", "alpha", "color", "marker", ...}}
"contour": {
    "contour": {"levels", "cmap", "alpha", ...},
    "scatter": {"s", "alpha", "color", ...}
}
```

### 3. Precedence Resolution

Clear, predictable precedence order:
1. User kwargs (highest priority)
2. Group-based styles (hue, style, marker, size)
3. Plot-specific theme styles
4. Base theme styles (lowest priority)

### 4. Component-Specific Kwargs

Multi-component plots can use prefixed kwargs:
- `scatter_s=50` → applies to scatter component
- `contour_levels=20` → applies to contour component
- `s=50` → applies to main/default component

## Files Created

1. **`src/dr_plotter/style_applicator.py`** (168 lines)
   - Core `StyleApplicator` class
   - Component schema definitions
   - Precedence resolution logic
   - Group style integration

2. **`test_style_applicator.py`** (135 lines)
   - Comprehensive test suite
   - Validates all major functionality
   - Demonstrates usage patterns

## Test Results

All tests pass successfully:
- ✓ Simple scatter plot styling
- ✓ Multi-component contour plot styling
- ✓ Group-based styling integration
- ✓ Precedence order validation
- ✓ Single component queries

## What StyleApplicator Provides

### For Simple Plots
```python
applicator = StyleApplicator(SCATTER_THEME, {"color": "red", "s": 100})
styles = applicator.get_component_styles("scatter")
# Returns: {"main": {"color": "red", "s": 100, "alpha": 0.7}}
```

### For Multi-Component Plots
```python
applicator = StyleApplicator(CONTOUR_THEME, {
    "contour_levels": 20,
    "scatter_alpha": 0.3
})
styles = applicator.get_component_styles("contour")
# Returns: {
#   "contour": {"levels": 20, "cmap": "viridis"},
#   "scatter": {"alpha": 0.3, "s": 10}
# }
```

### For Group Styling
```python
applicator = StyleApplicator(
    theme=BASE_THEME,
    kwargs={"hue": "category"},
    grouping_cfg=grouping_cfg,
    group_values={"category": "A"}
)
styles = applicator.get_component_styles("line")
# Returns styles with group-based color, linestyle, etc.
```

## Next Steps (Phase 2)

With the StyleApplicator foundation in place, Phase 2 will:
1. Update `BasePlotter` to use `StyleApplicator`
2. Remove `_filtered_plot_kwargs` property
3. Update `_apply_styling` method
4. Begin migrating individual plotters

## Benefits Achieved

1. **Unified Interface**: Single styling system for all plot types
2. **Explicit Components**: Clear component boundaries and schemas
3. **Predictable Precedence**: No more confusion about which styles apply
4. **Backward Compatible**: Existing kwargs patterns still work
5. **Extensible**: Easy to add new plot types and components

## Design Philosophy Alignment

This implementation strongly aligns with the project's design philosophy:
- **"Intuitive and Consistent API"**: One styling interface for all plots
- **"Clarity Through Structure"**: Explicit component schemas
- **"Atomicity"**: Each component has a single, well-defined purpose
- **"Fail Fast, Fail Loudly"**: Clear precedence rules prevent hidden bugs
- **"Minimalism"**: No unnecessary abstraction layers