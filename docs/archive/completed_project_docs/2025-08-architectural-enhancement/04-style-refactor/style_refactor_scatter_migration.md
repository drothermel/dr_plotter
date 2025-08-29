# ScatterPlotter Migration: First Grouped Plotter

## Summary

ScatterPlotter has been successfully migrated to the new StyleApplicator system, marking the first plotter with grouping support (hue, size, marker, alpha) to use the new styling architecture. This migration revealed important insights about handling visual channels and style precedence.

## Key Challenges & Solutions

### 1. Visual Channel Ambiguity

**Problem**: Parameters like `alpha` can be both:
- A visual channel for grouping (`alpha="column_name"`)
- A style value (`alpha=0.6`)

**Solution**: Smart detection in `_is_reserved_kwarg()`:
```python
if key in visual_channel_names and key in self.kwargs:
    value = self.kwargs[key]
    if isinstance(value, str):
        # It's a column name for grouping
        return True
    # It's a numeric value for styling
    return False
```

### 2. Grouped Rendering Architecture

**Discovery**: Matplotlib scatter requires multiple calls for different markers/sizes - you can't vary these in a single call.

**Implementation**: 
- `_render_with_grouped_method` iterates through groups
- Each group gets its own scatter call with consistent visual properties
- Default `_draw_grouped` in BasePlotter just calls `_draw` (perfect for scatter/line)
- Position-based plotters (bar/violin) override with custom `_draw_grouped`

### 3. Constants-Based Configuration

**Problem**: Hard-coded lists of visual channels scattered through code.

**Solution**: Use `VISUAL_CHANNELS` from `consts.py`:
```python
from dr_plotter.consts import VISUAL_CHANNELS

visual_channel_by_names = {f"{ch}_by" for ch in VISUAL_CHANNELS}
```

### 4. Unnecessary Style Properties

**Problem**: `cmap` was included even without color mapping data.

**Solution**: Conditional inclusion:
```python
if "cmap" in resolved_styles and "c" not in resolved_styles:
    del resolved_styles["cmap"]
```

## Migration Changes

### BasePlotter Updates

1. **Added default `_draw_grouped` method**: Fallback that calls `_draw` for overlaid groups
2. **Updated `_render_with_grouped_method`**: Uses StyleApplicator for grouped plots
3. **Fixed render logic**: Properly routes grouped vs non-grouped rendering

### ScatterPlotter Changes

Minimal changes required:
```python
class ScatterPlotter(BasePlotter):
    # ... existing configuration ...
    use_style_applicator: bool = True  # Opt into new system
    
    def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
        ax.scatter(data[consts.X_COL_NAME], data[consts.Y_COL_NAME], **kwargs)
```

### StyleApplicator Enhancements

1. **Dynamic visual channel detection** using constants
2. **Smart parameter filtering** for reserved vs style kwargs
3. **Conditional property inclusion** (e.g., cmap only with c)
4. **Group style integration** for visual channels

## Test Coverage

Comprehensive tests verify:
- ✓ Basic scatter without groups
- ✓ Hue grouping with automatic colors
- ✓ Multiple visual channels (hue + size + marker + alpha)
- ✓ Style precedence (user > group > theme)
- ✓ Backward compatibility with existing examples

## Design Insights

### Grouping Patterns

Two distinct patterns emerged:

1. **Overlay Pattern** (scatter, line):
   - Groups rendered on top of each other
   - Different visual properties per group
   - Simple `_draw_grouped` → `_draw` delegation

2. **Position Pattern** (bar, violin):
   - Groups positioned side-by-side
   - Requires position calculations
   - Custom `_draw_grouped` implementation

### Visual Channel vs Style Property

The same parameter name can serve different purposes:
- `alpha="transparency_column"` → Visual channel for grouping
- `alpha=0.6` → Style property for all points

This duality requires intelligent parameter interpretation based on value type.

## Migration Template for Grouped Plotters

For plotters with grouping support:

1. Set `use_style_applicator = True`
2. Ensure `enabled_channels` is a `Set[VisualChannel]`
3. Remove manual theme/style manipulation
4. For overlay pattern: Use default `_draw_grouped`
5. For position pattern: Keep custom `_draw_grouped`
6. Test with all supported visual channels

## Benefits Demonstrated

1. **Unified Styling**: Groups and non-grouped plots use same system
2. **Automatic Precedence**: User kwargs properly override group styles
3. **Clean Separation**: Visual channels vs style properties clearly distinguished
4. **Minimal Changes**: Most plotters need only flag + type fix
5. **Maintained Compatibility**: All existing examples continue working

## Next Steps

With ScatterPlotter proving the grouped plotter migration path:
1. Migrate other overlay plotters (LinePlotter)
2. Migrate position-based plotters (BarPlotter, ViolinPlotter)
3. Handle complex multi-component plotters (ContourPlotter, BumpPlotter)
4. Remove old styling infrastructure once all migrated